"""Offline SDK fixture shared by observability integration tests."""
import json
import os
import uuid
from types import SimpleNamespace

import pytest


@pytest.fixture
def tracing(monkeypatch):
    langfuse = pytest.importorskip("langfuse")
    import httpx
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from src import observability as obs

    exporter = InMemorySpanExporter()
    sdk_type = langfuse.Langfuse
    http = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={})))

    def make_client(**kwargs):
        return sdk_type(**kwargs, span_exporter=exporter, httpx_client=http)

    monkeypatch.setattr(langfuse, "Langfuse", make_client)
    monkeypatch.setattr(obs, "_client", None)
    monkeypatch.setattr(obs, "_client_pid", None)
    monkeypatch.setattr(obs, "_initialized", False)
    monkeypatch.setattr(obs, "_warnings", set())
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_ENABLED", "true")
    monkeypatch.setenv("PENGUIN_OBSERVABILITY_CONTENT", "metadata_only")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", f"pk-lf-{uuid.uuid4().hex}")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-offline-test")
    monkeypatch.setenv("LANGFUSE_BASE_URL", "http://langfuse.invalid")
    monkeypatch.setenv("LANGFUSE_SAMPLE_RATE", "1.0")
    client = obs._get_client()
    assert client is not None

    def spans(name=None):
        client.flush()
        return [span for span in exporter.get_finished_spans() if name is None or span.name == name]

    def metadata(span):
        prefix = "langfuse.observation.metadata."
        return {key[len(prefix):]: json.loads(value) for key, value in span.attributes.items()
                if key.startswith(prefix)}

    yield SimpleNamespace(client=client, exporter=exporter, spans=spans, metadata=metadata)
    client.shutdown()
    http.close()
