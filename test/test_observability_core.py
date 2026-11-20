"""Observation boundaries must follow real Agent work, including recovery paths."""

from contextlib import contextmanager
from contextvars import ContextVar
from types import SimpleNamespace as NS
from unittest.mock import Mock

import anthropic
import httpx
import pytest

import src.agent_loop as loop
import src.compact as compact


class RecordedSpan:
    def __init__(self, name, metadata, parent, enabled=True):
        self.name = name
        self.metadata = dict(metadata)
        self.parent = parent
        self.enabled = enabled
        self.status = None
        self.closed = False
        self.first_token_seen = False
        self.responses = []
        self.values = {}

    def update(self, **kwargs):
        self.metadata.update(kwargs.pop("metadata", {}) or {})
        self.values.update(kwargs)

    def set_status(self, status, **metadata):
        self.status = status
        self.metadata.update(metadata)

    def first_token(self):
        self.first_token_seen = True


class Recorder:
    def __init__(self):
        self.spans = []
        self.current = ContextVar("test_core_current", default=None)
        self.attributes = ContextVar("test_core_attributes", default={})
        self.enabled = True

    @contextmanager
    def observation(self, name, *, metadata=None, **kwargs):
        span = RecordedSpan(name, {**self.attributes.get(), **(metadata or {})},
                            self.current.get(), self.enabled)
        span.values.update(kwargs)
        self.spans.append(span)
        token = self.current.set(span)
        try:
            yield span
        except (GeneratorExit, KeyboardInterrupt):
            span.set_status("cancelled")
            raise
        except BaseException:
            span.set_status("error")
            raise
        finally:
            span.closed = True
            self.current.reset(token)

    @contextmanager
    def bind_context(self, **metadata):
        token = self.attributes.set({**self.attributes.get(), **metadata})
        try:
            yield
        finally:
            self.attributes.reset(token)

    @staticmethod
    def record_response(span, response):
        assert not span.closed
        span.responses.append(response)

    def named(self, name):
        return [span for span in self.spans if span.name == name]


@pytest.fixture
def recorder(monkeypatch):
    recorder = Recorder()
    for module in (loop, compact):
        monkeypatch.setattr(module, "observation", recorder.observation)
        monkeypatch.setattr(module, "record_response", recorder.record_response)
    monkeypatch.setattr(loop, "run_context", recorder.observation)
    monkeypatch.setattr(loop, "bind_context", recorder.bind_context)
    monkeypatch.setattr(loop, "needs_compaction", lambda *_: False)
    monkeypatch.setattr(loop.time, "sleep", lambda *_: None)
    monkeypatch.setattr(loop, "usage_stats", {
        "prompt_tokens": 0, "completion_tokens": 0,
        "last_input_tokens": 0, "pending_delta": 0,
    })
    return recorder


def text_event(text):
    return NS(type="content_block_delta", delta=NS(type="text_delta", text=text))


def final_message(text="done", *, stop_reason="end_turn", input_tokens=20, output_tokens=3):
    return NS(content=[NS(type="text", text=text)], stop_reason=stop_reason,
              usage=NS(input_tokens=input_tokens, output_tokens=output_tokens))


class FakeStream:
    def __init__(self, events, response):
        self.events = events
        self.response = response
        self.closed = False
        self.final_read = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def __iter__(self):
        for event in self.events:
            if isinstance(event, BaseException):
                raise event
            yield event

    def get_final_message(self):
        self.final_read = True
        return self.response


def scripted_client(*steps):
    steps = iter(steps)

    def stream(**kwargs):
        result = next(steps)
        if isinstance(result, BaseException):
            raise result
        return result

    return NS(messages=NS(stream=Mock(side_effect=stream)))


def status_error(code, message="request failed"):
    return anthropic.APIStatusError(
        message, response=httpx.Response(code, request=httpx.Request("POST", "https://unit.invalid")),
        body=None,
    )


def run(client, **kwargs):
    return loop.agent_loop(client, "work", model_id="test-model", tool_dispatcher=Mock(), **kwargs)


def test_stream_observation_lives_until_final_response_is_consumed(recorder):
    response = final_message(input_tokens=123, output_tokens=7)
    stream = FakeStream([text_event("hello"), text_event(" world")], response)
    generator = loop.stream_response(scripted_client(stream), [], model_id="test-model")
    assert recorder.spans == []

    assert next(generator) == ("text_delta", "hello")
    generation = recorder.named("llm.generate")[0]
    assert not generation.closed
    assert generation.first_token_seen
    assert not stream.final_read

    assert list(generator) == [("text_delta", " world"), ("usage", 123)]
    assert generation.closed and stream.closed and stream.final_read
    assert generation.responses == [response]
    assert loop.usage_stats["prompt_tokens"] == 123
    assert loop.usage_stats["completion_tokens"] == 7


def test_tool_only_stream_has_first_response_and_preserves_tool_id(recorder):
    events = [
        NS(type="content_block_start", index=0,
           content_block=NS(type="tool_use", id="read-42", name="read_file")),
        NS(type="content_block_delta", index=0,
           delta=NS(type="input_json_delta", partial_json='{"path":"a.py"}')),
        NS(type="content_block_stop", index=0),
    ]
    result = list(loop.stream_response(scripted_client(FakeStream(events, final_message())), []))
    assert result[0] == ("tool_calls", [{"id": "read-42", "name": "read_file", "input": {"path": "a.py"}}])
    assert recorder.named("llm.generate")[0].first_token_seen


def test_closing_stream_ends_generation_without_inventing_usage(recorder):
    stream = FakeStream([text_event("partial")], final_message())
    generator = loop.stream_response(scripted_client(stream), [])
    next(generator)
    generator.close()

    generation = recorder.named("llm.generate")[0]
    assert generation.closed and stream.closed
    assert generation.status == "cancelled"
    assert not stream.final_read
    assert generation.responses == []
    assert loop.usage_stats["prompt_tokens"] == 0


def test_stream_failure_propagates_and_closes_generation(recorder):
    failure = RuntimeError("connection interrupted")
    stream = FakeStream([text_event("partial"), failure], final_message())
    generator = loop.stream_response(scripted_client(stream), [])
    assert next(generator) == ("text_delta", "partial")
    with pytest.raises(RuntimeError, match="connection interrupted"):
        list(generator)
    assert stream.closed
    assert recorder.named("llm.generate")[0].status == "error"


def test_retry_gets_distinct_generations_under_one_iteration(recorder):
    response = final_message()
    client = scripted_client(status_error(429), FakeStream([text_event("done")], response))
    assert run(client)[0] == "done"

    generations = recorder.named("llm.generate")
    assert len(generations) == 2
    assert [span.metadata["attempt"] for span in generations] == [1, 2]
    assert generations[0].status == "error"
    assert generations[0].responses == []
    assert generations[1].responses == [response]
    assert generations[0].parent is generations[1].parent
    assert generations[0].parent.name == "agent.iteration"
    assert recorder.named("agent.run")[0].status == "completed"


def test_truncated_discarded_output_still_records_its_usage(recorder):
    first = final_message("partial", stop_reason="max_tokens", input_tokens=20, output_tokens=10)
    second = final_message("complete", input_tokens=20, output_tokens=15)
    client = scripted_client(FakeStream([text_event("partial")], first),
                             FakeStream([text_event("complete")], second))
    assert run(client)[0] == "complete"
    generations = recorder.named("llm.generate")
    assert [span.responses[0] for span in generations] == [first, second]
    assert generations[0].status == "truncated"
    assert generations[1].metadata["output_limit_escalated"] is True
    assert loop.usage_stats["completion_tokens"] == 25


@pytest.mark.parametrize("errors,status", [
    ([status_error(403)], "api_error"),
    ([status_error(400, "prompt too long"), status_error(400, "prompt too long")], "context_limit"),
])
def test_returned_api_error_is_not_marked_completed(recorder, errors, status):
    run(scripted_client(*errors))
    assert recorder.named("agent.run")[0].status == status


def test_iteration_limit_has_explicit_terminal_status(recorder):
    result, _ = run(scripted_client(), max_iterations=0)
    assert "maximum iterations" in result
    assert recorder.named("agent.run")[0].status == "iteration_limit"


def test_exit_loop_and_skipped_calls_are_observed_without_execution(recorder, monkeypatch):
    calls = [{"id": "read", "name": "read_file", "input": {}},
             {"id": "exit", "name": "exit_loop", "input": {}}]
    monkeypatch.setattr(loop, "stream_response", lambda *_, **__: iter([("tool_calls", calls)]))
    execute = Mock()
    monkeypatch.setattr(loop, "execute_tools_parallel", execute)
    _, history = run(scripted_client())
    execute.assert_not_called()
    spans = recorder.named("tool.control")
    assert [(span.metadata["tool_use_id"], span.status) for span in spans] == [
        ("read", "skipped"), ("exit", "completed"),
    ]
    assert history[-1]["content"][0]["is_error"] is True


def test_child_status_does_not_overwrite_parent_status(recorder):
    @loop._observed_agent("test.parent")
    def parent(client, prompt):
        loop.run_subagent(client, prompt, max_iterations=1)
        return "parent completed"

    assert parent(scripted_client(status_error(403)), "work") == "parent completed"
    assert recorder.named("test.parent")[0].status == "completed"
    assert recorder.named("agent.subagent")[0].status == "api_error"
    assert loop._active_run.get() is None


def long_history():
    return [{"role": "user", "content": "Start"}] + [
        {"role": role, "content": "details " * 200}
        for _ in range(5) for role in ("assistant", "user")
    ]


def test_compaction_generations_capture_each_summary_and_collapse(recorder):
    response = final_message("summary " * 100)
    client = NS(messages=NS(create=Mock(return_value=response), count_tokens=Mock()))
    result = compact.llm_compact_messages(long_history(), client, "test-model", max_tokens=10)

    summaries = recorder.named("llm.compact.summarize")
    collapse = recorder.named("llm.compact.collapse")
    assert len(summaries) == 3
    assert [span.metadata["compact_attempt"] for span in summaries] == [1, 2, 3]
    assert len(collapse) == 1
    assert all(span.responses == [response] for span in summaries + collapse)
    assert client.messages.create.call_count == 4
    assert result[0]["content"].startswith("[Context collapsed")


def test_failed_compaction_keeps_history_and_records_failure(recorder):
    client = NS(messages=NS(create=Mock(side_effect=RuntimeError("model unavailable"))))
    messages = long_history()
    assert compact.llm_compact_messages(messages, client, "test-model", max_tokens=10) == messages
    generations = [span for span in recorder.spans if span.name.startswith("llm.compact.")]
    assert len(generations) == 4
    assert all(span.status == "error" and span.closed for span in generations)


def test_count_tokens_is_a_span_without_generation_usage(recorder):
    client = NS(messages=NS(count_tokens=Mock(return_value=NS(input_tokens=42))))
    assert compact._verify_tokens_within_budget([], client, "test-model", 50)
    spans = recorder.named("llm.count_tokens")
    assert len(spans) == 1
    assert spans[0].values["output"] == {"input_tokens": 42}
    assert spans[0].responses == []


def test_disabled_reactive_compact_does_not_walk_content(recorder, monkeypatch):
    recorder.enabled = False
    estimate = Mock(side_effect=AssertionError("disabled telemetry must not walk content"))
    monkeypatch.setattr(compact, "estimate_messages_tokens", estimate)
    messages = long_history()
    assert len(compact.reactive_compact(messages, keep_recent=3)) == 3
    estimate.assert_not_called()
