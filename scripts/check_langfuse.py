#!/usr/bin/env python3
"""Check Langfuse credentials and send one synthetic trace without calling an LLM."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from src.observability import _get_client, run_context, observation, flush
    client = _get_client()
    if client is None:
        print("Langfuse unavailable: enable PENGUIN_OBSERVABILITY_ENABLED, install "
              "requirements-observability.txt and configure both project keys.", file=sys.stderr)
        return 1
    try:
        if not client.auth_check():
            print("Langfuse authentication failed. Check project keys and base URL.", file=sys.stderr)
            return 1
        with run_context("penguin.connection_check", metadata={"synthetic": True}) as root:
            with observation("tool.connection_check", as_type="tool") as child:
                child.set_status("completed")
            root.set_status("completed")
        flush()
        print(f"Authentication succeeded; synthetic trace flushed: {root.trace_id}")
        print("Search this trace ID in Langfuse after ingestion. No model was called.")
        return 0
    except Exception as error:
        print(f"Langfuse check failed ({type(error).__name__}).", file=sys.stderr)
        return 1
    finally:
        flush()


if __name__ == "__main__":
    raise SystemExit(main())
