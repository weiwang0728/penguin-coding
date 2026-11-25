"""Optional, fail-open Langfuse tracing for Penguin's execution boundaries.

No SDK import or network access occurs unless explicitly enabled. Business
exceptions are never suppressed; SDK failures are isolated from the caller.
"""
from __future__ import annotations

import atexit
import json
import logging
import math
import os
import re
import threading
import time
import uuid
from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("penguin.observability")
_context: ContextVar[dict] = ContextVar("penguin_observation_context", default={})
_current: ContextVar[SafeObservation | None] = ContextVar("penguin_observation", default=None)
_client = None
_client_pid = None
_initialized = False
_client_lock = threading.Lock()
_warnings: set[str] = set()
_SECRET_KEY = re.compile(r"api[_-]?key|authorization|password|secret|credential|(?:access|refresh)[_-]?token", re.I)
_SECRET_TEXT = re.compile(
    r"(?i)(bearer\s+)[\w.\-/+=]+|\b(?:sk|pk)-(?:ant-|lf-)?[\w-]{8,}|"
    r"((?:api[_-]?key|password|secret|access[_-]?token)\s*[=:]\s*)[^\s,;]+"
)
_ERROR_STATUSES = frozenset({"error", "failed", "api_error", "connection_error", "timeout",
                            "iteration_limit", "context_limit", "invalid_arguments", "unknown_tool",
                            "tool_error", "execution_error", "worker_error", "nonzero_exit", "patch_error"})
_WARNING_STATUSES = frozenset({"cancelled", "interrupted", "permission_denied", "denied",
                              "truncated", "skipped", "conflict"})


def _warn_once(reason: str) -> None:
    if reason not in _warnings:
        _warnings.add(reason)
        # Do not log exporter exception bodies: they may contain credentials or IO.
        logger.warning("Observability unavailable (%s); execution continues", reason)


def _enabled() -> bool:
    return (os.getenv("PENGUIN_OBSERVABILITY_ENABLED", "false").lower() in {"1", "true", "yes"}
            and os.getenv("LANGFUSE_TRACING_ENABLED", "true").lower() != "false"
            and os.getenv("OTEL_SDK_DISABLED", "false").lower() != "true")


def _redact_text(value: str) -> str:
    for key in ("API_KEY", "EVAL_API_KEY", "ANTHROPIC_API_KEY", "LANGFUSE_SECRET_KEY"):
        secret = os.getenv(key)
        if secret and len(secret) >= 8:
            value = value.replace(secret, "[REDACTED]")
    return _SECRET_TEXT.sub(lambda match: (match.group(1) or match.group(2) or "") + "[REDACTED]", value)


def _sanitize(value: Any, *, depth: int = 0) -> Any:
    """Bound traversal and redact secret keys before serialization."""
    if depth > 8:
        return "[MAX_DEPTH]"
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        return _redact_text(value)[:_content_limit()]
    if isinstance(value, Mapping):
        return {str(key): "[REDACTED]" if _SECRET_KEY.search(str(key)) else _sanitize(item, depth=depth + 1)
                for key, item in list(value.items())[:200]}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item, depth=depth + 1) for item in value[:1000]]
    if hasattr(value, "model_dump"):
        return _sanitize(value.model_dump(), depth=depth + 1)
    # Avoid arbitrary __str__ implementations (and object reprs containing secrets).
    return f"<{type(value).__name__}>"


def _content_limit() -> int:
    try:
        return max(256, min(int(os.getenv("PENGUIN_OBSERVABILITY_MAX_CHARS", "8000")), 2_000_000))
    except ValueError:
        return 8000


def _capture_content() -> bool:
    # Full input/output capture is the default; "metadata_only" opts out and
    # unknown values still fail closed.
    return os.getenv("PENGUIN_OBSERVABILITY_CONTENT", "redacted") == "redacted"


def _payload(value: Any) -> Any:
    clean = _sanitize(value)
    encoded = json.dumps(clean, ensure_ascii=False)
    if len(encoded) > _content_limit():
        return {"truncated": True, "preview": encoded[:_content_limit()]}
    return clean


def _get_client():
    global _client, _client_pid, _initialized
    if not _enabled():
        return None
    pid = os.getpid()
    with _client_lock:
        if _client_pid == pid and _initialized:
            return _client
        _client_pid, _initialized, _client = pid, True, None
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            _warn_once("missing Langfuse keys")
            return None
        try:
            from langfuse import Langfuse
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
            sample_rate = float(os.getenv("LANGFUSE_SAMPLE_RATE", "1.0"))
            _client = Langfuse(
                timeout=5, flush_at=128, flush_interval=2,
                # Isolate this exporter and honor parent sampling across processes.
                tracer_provider=TracerProvider(sampler=ParentBased(TraceIdRatioBased(sample_rate))),
                # Do not export unrelated libraries' spans on a shared OTel provider.
                should_export_span=lambda span: bool((span.attributes or {}).get(
                    "langfuse.observation.metadata.penguin_observation")),
            )
        except Exception as error:
            _warn_once(f"SDK initialization: {type(error).__name__}")
        return _client


class SafeObservation:
    """Small safe facade; actual IDs only exist if the SDK created an observation."""
    def __init__(self, handle=None):
        self._handle = handle
        self.enabled = handle is not None
        self.trace_id = getattr(handle, "trace_id", None)
        self.span_id = getattr(handle, "id", None)
        self.parent_span_id = None
        self.status: str | None = None
        self._started = time.perf_counter()
        self._first_token = False
        self._metadata: dict = {}

    def update(self, **fields) -> None:
        if not self.enabled:
            return
        try:
            prepared = {}
            for key, value in fields.items():
                if key in {"input", "output"}:
                    if _capture_content() and value is not None:
                        prepared[key] = _payload(value)
                elif key == "metadata":
                    self._metadata.update(_sanitize(value or {}))
                    prepared[key] = self._metadata.copy()
                elif key == "completion_start_time":
                    prepared[key] = value
                else:
                    prepared[key] = _sanitize(value)
            self._handle.update(**prepared)
        except Exception as error:
            _warn_once(f"span update: {type(error).__name__}")

    def set_status(self, status: str, **metadata) -> None:
        self.status = status
        level = "ERROR" if status in _ERROR_STATUSES else "WARNING" if status in _WARNING_STATUSES else "DEFAULT"
        self.update(level=level, status_message=status, metadata={"status": status, **metadata})

    def first_token(self) -> None:
        if not self.enabled or self._first_token:
            return
        self._first_token = True
        self.update(completion_start_time=datetime.now(timezone.utc),
                    metadata={"ttft_ms": round((time.perf_counter() - self._started) * 1000, 3)})


@contextmanager
def bind_context(**metadata):
    token = _context.set({**_context.get(), **{key: value for key, value in metadata.items() if value is not None}})
    try:
        yield
    finally:
        _context.reset(token)


@contextmanager
def observation(name: str, as_type: str = "span", *, input=None, metadata=None,
                model=None, model_parameters=None, trace_context=None):
    """Only catch instrumentation errors, never errors raised by the business body."""
    manager = propagation = remote_parent = None
    span = SafeObservation()
    parent = _current.get()
    try:
        client = _get_client()
        if client is not None:
            from langfuse import propagate_attributes
            if trace_context:
                from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags, use_span
                remote_parent = use_span(NonRecordingSpan(SpanContext(
                    trace_id=int(trace_context["trace_id"], 16),
                    span_id=int(trace_context["parent_span_id"], 16),
                    is_remote=True, trace_flags=TraceFlags(trace_context.get("trace_flags", 1)),
                )), end_on_exit=False)
                remote_parent.__enter__()
            fields = _context.get()
            propagation = propagate_attributes(session_id=fields.get("session_id"))
            propagation.__enter__()
            combined = _sanitize({**fields, **(metadata or {}), "penguin_observation": True})
            manager = client.start_as_current_observation(
                name=name, as_type=as_type, metadata=combined,
                model=model, model_parameters=_sanitize(model_parameters),
                input=_payload(input) if _capture_content() and input is not None else None,
            )
            span = SafeObservation(manager.__enter__())
            span._metadata = combined
            span.parent_span_id = (trace_context.get("parent_span_id") if trace_context
                                   else parent.span_id if parent else None)
    except Exception as error:
        manager = None
        _warn_once(f"span start: {type(error).__name__}")
    token = _current.set(span)
    try:
        yield span
    except BaseException as error:
        span.set_status("cancelled" if isinstance(error, (KeyboardInterrupt, GeneratorExit)) else "error",
                        exception_type=type(error).__name__)
        raise
    finally:
        _current.reset(token)
        # Passing the business exception into OTel would automatically capture its
        # raw text and traceback, bypassing metadata-only/redaction policy.
        for context_manager in (manager, propagation, remote_parent):
            if context_manager is not None:
                try:
                    context_manager.__exit__(None, None, None)
                except Exception as error:
                    _warn_once(f"span finish: {type(error).__name__}")


@contextmanager
def run_context(name: str, *, session_id=None, run_id=None, metadata=None, trace_context=None):
    previous = _context.get()
    values = {**(metadata or {}),
              "session_id": session_id or previous.get("session_id") or uuid.uuid4().hex,
              "run_id": run_id or previous.get("run_id") or uuid.uuid4().hex}
    with bind_context(**values):
        with observation(name, as_type="agent", trace_context=trace_context) as span:
            yield span


def current_trace_fields() -> dict:
    fields = dict(_context.get())
    span = _current.get()
    if span is not None and span.trace_id and span.span_id:
        fields.update(trace_id=span.trace_id, span_id=span.span_id)
        if span.parent_span_id:
            fields["parent_span_id"] = span.parent_span_id
    return fields


def set_status(status: str, **metadata) -> None:
    span = _current.get()
    if span is not None:
        span.set_status(status, **metadata)


def _field(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, Mapping) else getattr(obj, key, default)


def record_response(span: SafeObservation, response) -> None:
    if not span.enabled:
        return
    try:
        usage = _field(response, "usage")
        details = {}
        for source, target in (("input_tokens", "input"), ("output_tokens", "output"),
                               ("cache_read_input_tokens", "cache_read_input_tokens"),
                               ("cache_creation_input_tokens", "cache_creation_input_tokens")):
            value = _field(usage, source)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                details[target] = value
        metadata = {"stop_reason": _field(response, "stop_reason"), "usage_available": bool(details)}
        cache = _field(usage, "cache_creation")
        # TTL detail is metadata, not another additive usage bucket: avoid counting
        # cache creation twice when the provider also returns the total.
        for key in ("ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"):
            value = _field(cache, key)
            if isinstance(value, int):
                metadata[key] = value
        model = _field(response, "model")
        if isinstance(model, str):
            metadata["response_model"] = model
        span.update(output=_field(response, "content"), metadata=metadata,
                    **({"usage_details": details} if details else {}))
    except Exception as error:
        _warn_once(f"usage capture: {type(error).__name__}")


def trace_headers() -> dict[str, str]:
    fields = current_trace_fields()
    if not fields.get("trace_id") or not fields.get("span_id"):
        return {}
    # Preserve the SDK's sampled flag (including an unsampled trace).
    flag = "01"
    try:
        from opentelemetry import trace
        flag = "01" if trace.get_current_span().get_span_context().trace_flags.sampled else "00"
    except Exception:
        pass
    return {"traceparent": f"00-{fields['trace_id']}-{fields['span_id']}-{flag}"}


def extract_trace_context(carrier: Mapping | None) -> dict | None:
    if not carrier:
        return None
    normalized = {str(key).lower(): value for key, value in carrier.items()}
    raw = normalized.get("traceparent") or normalized.get("penguin_traceparent")
    if not isinstance(raw, str):
        return None
    match = re.fullmatch(r"00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})", raw.lower())
    if not match or int(match[1], 16) == 0 or int(match[2], 16) == 0:
        return None
    return {"trace_id": match[1], "parent_span_id": match[2], "trace_flags": int(match[3], 16)}


def score(name: str, value, *, trace_id=None, score_id=None, data_type="NUMERIC", comment=None) -> bool:
    """Queue a score; True means accepted by the SDK, not confirmed server storage."""
    try:
        client = _get_client()
        trace_id = trace_id or current_trace_fields().get("trace_id")
        if client is None or not trace_id:
            return False
        if data_type == "NUMERIC":
            value = float(value)
            if not math.isfinite(value):
                return False
        client.create_score(name=name, value=value, trace_id=trace_id, score_id=score_id,
                            data_type=data_type, comment=_redact_text(comment)[:_content_limit()] if isinstance(comment, str) else None)
        return True
    except Exception as error:
        _warn_once(f"score: {type(error).__name__}")
        return False


def flush() -> None:
    # Never initialize a client just to flush on process exit.
    if _client is not None and _client_pid == os.getpid():
        try:
            _client.flush()
        except Exception as error:
            _warn_once(f"flush: {type(error).__name__}")


atexit.register(flush)
