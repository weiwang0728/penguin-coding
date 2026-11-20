"""Real SDK export, redaction, propagation and fail-open behavior (no network)."""
import builtins
import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from contextvars import copy_context
from types import SimpleNamespace as NS

import pytest

from src import observability as obs


def test_disabled_never_imports_sdk_or_serializes(monkeypatch):
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_ENABLED", "false")
    original = builtins.__import__

    def guarded(name, *args, **kwargs):
        assert not name.startswith(("langfuse", "opentelemetry"))
        return original(name, *args, **kwargs)

    class Poison:
        def model_dump(self):
            raise AssertionError("disabled tracing serialized content")

    monkeypatch.setattr(builtins, "__import__", guarded)
    with obs.run_context("agent.run") as root:
        with obs.observation("llm.generate", input=Poison()) as span:
            span.update(output=Poison())
            obs.record_response(span, Poison())
            assert root.trace_id is None and not span.enabled
            assert obs.trace_headers() == {}
            assert not obs.score("test", 1)


def test_sdk_preserves_parentage_sessions_and_thread_context(tracing):
    def tool(call_id):
        with obs.bind_context(tool_use_id=call_id):
            with obs.observation("tool.read", as_type="tool"):
                return obs.current_trace_fields()

    with obs.run_context("agent.run", session_id="conversation", run_id="request") as root:
        with ThreadPoolExecutor(2) as pool:
            futures = [pool.submit(copy_context().run, tool, f"call-{i}") for i in range(2)]
            fields = [f.result() for f in futures]
        assert "tool_use_id" not in obs.current_trace_fields()
    assert obs.current_trace_fields() == {}
    spans = tracing.spans("tool.read")
    assert len(spans) == 2
    assert len({s.context.span_id for s in spans}) == 2
    assert all(s.context.trace_id == int(root.trace_id, 16) for s in spans)
    assert all(s.parent.span_id == int(root.span_id, 16) for s in spans)
    assert {f["tool_use_id"] for f in fields} == {"call-0", "call-1"}
    assert all(tracing.metadata(s)["session_id"] == "conversation" for s in spans)
    assert all(s.attributes["session.id"] == "conversation" for s in spans)


def test_sdk_generation_uses_response_usage_and_no_prompt_by_default(tracing):
    with obs.observation("llm.generate", as_type="generation", model="model", input="PRIVATE PROMPT") as span:
        span.first_token()
        span.first_token()
        obs.record_response(span, NS(content="PRIVATE OUTPUT", stop_reason="end_turn", usage=NS(
            input_tokens=13, output_tokens=7, cache_read_input_tokens=9,
            cache_creation_input_tokens=4, cache_creation=NS(ephemeral_5m_input_tokens=4))))
    exported = tracing.spans()[0]
    attributes = exported.attributes
    assert "PRIVATE" not in repr(attributes)
    usage = json.loads(attributes["langfuse.observation.usage_details"])
    assert usage == {"input": 13, "output": 7, "cache_read_input_tokens": 9, "cache_creation_input_tokens": 4}
    assert tracing.metadata(exported)["ephemeral_5m_input_tokens"] == 4
    assert "langfuse.observation.completion_start_time" in attributes
    assert tracing.metadata(exported)["ttft_ms"] >= 0


def test_unknown_usage_is_not_zero_cost(tracing):
    with obs.observation("llm.generate", as_type="generation") as span:
        obs.record_response(span, NS(content="answer"))
    exported = tracing.spans()[0]
    assert "langfuse.observation.usage_details" not in exported.attributes
    assert tracing.metadata(exported)["usage_available"] is False


def test_redacted_capture_and_exception_do_not_leak_secrets(tracing, monkeypatch):
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_CONTENT", "redacted")
    monkeypatch.setenv("API_KEY", "private-long-provider-key")
    with pytest.raises(ValueError, match="private"):
        with obs.observation("tool.run", input={"password": "private-password", "text": "Bearer abcdefghijk"}) as span:
            span.update(output="private-long-provider-key", metadata={"api_key": "private-key"})
            raise ValueError("private exception contains private-long-provider-key")
    exported = tracing.spans()[0]
    serialized = repr(exported.attributes) + repr(exported.events)
    assert "private" not in serialized
    assert "abcdefghijk" not in serialized
    assert "REDACTED" in serialized
    assert exported.attributes["langfuse.observation.level"] == "ERROR"
    assert tracing.metadata(exported)["exception_type"] == "ValueError"
    assert not exported.events


def test_content_is_bounded_and_unknown_modes_disable_capture(tracing, monkeypatch):
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_CONTENT", "redacted")
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_MAX_CHARS", "300")
    with obs.observation("tool.long", input=["x" * 10000] * 100):
        pass
    value = json.loads(tracing.spans()[0].attributes["langfuse.observation.input"])
    assert value["truncated"] and len(value["preview"]) == 300
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_CONTENT", "typo")
    with obs.observation("tool.private", input="hidden"):
        pass
    assert "langfuse.observation.input" not in tracing.spans("tool.private")[0].attributes


@pytest.mark.parametrize("failure", ["start", "update", "finish"])
def test_sdk_failure_preserves_result_and_business_exception(monkeypatch, failure):
    pytest.importorskip("langfuse")

    class Handle:
        trace_id = "a" * 32
        id = "b" * 16

        def update(self, **kwargs):
            if failure == "update":
                raise RuntimeError("SDK failure")

    @contextmanager
    def manager(**kwargs):
        if failure == "start":
            raise RuntimeError("SDK failure")
        yield Handle()
        if failure == "finish":
            raise RuntimeError("SDK failure")

    monkeypatch.setattr(obs, "_get_client", lambda: NS(start_as_current_observation=manager))
    with obs.observation("test") as span:
        span.update(metadata={"done": True})
        result = 42
    assert result == 42
    with pytest.raises(ValueError, match="business failure"):
        with obs.observation("test"):
            raise ValueError("business failure")
    assert obs.current_trace_fields() == {}


def test_explicit_traceparent_and_sampling_flag(tracing):
    carrier = {"Traceparent": f"00-{'a' * 32}-{'b' * 16}-01"}
    with obs.run_context("worker", trace_context=obs.extract_trace_context(carrier)) as span:
        assert span.trace_id == "a" * 32
        assert obs.trace_headers()["traceparent"].startswith(f"00-{'a' * 32}-{span.span_id}")
    assert tracing.spans("worker")[0].parent.span_id == int("b" * 16, 16)
    with obs.run_context("unsampled", trace_context=obs.extract_trace_context(
            {"traceparent": f"00-{'c' * 32}-{'d' * 16}-00"})):
        assert obs.trace_headers()["traceparent"].endswith("-00")
    assert not tracing.spans("unsampled")
    assert obs.extract_trace_context({"traceparent": f"00-{'0' * 32}-{'b' * 16}-01"}) is None
    assert obs.extract_trace_context({"traceparent": "invalid"}) is None


def test_scores_are_idempotently_identified_and_fail_open(monkeypatch):
    calls = []
    monkeypatch.setattr(obs, "_get_client", lambda: NS(create_score=lambda **kwargs: calls.append(kwargs)))
    for _ in range(2):
        assert obs.score("resolved", 1, trace_id="a" * 32, score_id="stable", data_type="BOOLEAN")
    assert calls[0] == calls[1]
    assert not obs.score("invalid", float("nan"), trace_id="a" * 32)
    assert not obs.score("missing", 1)


def test_missing_credentials_disable_without_import(monkeypatch):
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_ENABLED", "true")
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.setattr(obs, "_initialized", False)
    monkeypatch.setattr(obs, "_client", None)
    assert obs._get_client() is None
