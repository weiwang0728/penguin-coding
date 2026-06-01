"""Interactive REPL — the user-facing terminal interface."""

import sys
import os
import json
import argparse
import logging

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings

from anthropic import Anthropic
from dotenv import load_dotenv

from . import agent_loop as _al
from .agent_loop import agent_loop, register_delegate_tool, usage_stats
from .compact import llm_compact_messages, estimate_tokens, MAX_CONTEXT_TOKENS
from .tools import dispatcher, _changed_files
from ._constants import ALLOWED_BASE_DIR
from .session import save_session, load_session, list_sessions
from . import __version__

console = Console()


def _parse_args():
    p = argparse.ArgumentParser(
        prog="penguin",
        description="Penguin Coding Agent — AI-powered coding assistant with Anthropic Claude.",
    )
    p.add_argument("-m", "--model", help="Model ID (default: $MODEL_ID or claude-sonnet-4-20250514)")
    p.add_argument("--base-url", help="API base URL (default: $BASE_URL)")
    p.add_argument("--api-key", help="API key (default: $API_KEY)")
    p.add_argument("-p", "--prompt", help="One-shot prompt (non-interactive mode)")
    p.add_argument("-r", "--resume", metavar="ID", help="Resume a saved session")
    p.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    return p.parse_args()


def main():
    args = _parse_args()
    load_dotenv()

    api_key = args.api_key or os.getenv("API_KEY")
    base_url = args.base_url or os.getenv("BASE_URL")
    model_id = args.model or os.getenv("MODEL_ID")

    if not api_key:
        console.print("[red bold]No API key found.[/]")
        console.print(
            "Set API_KEY in .env or pass --api-key.\n"
            "\nExamples:\n"
            '  export API_KEY="sk-ant-..."\n'
            '  export BASE_URL="https://..."  # optional, for custom endpoints\n'
            '  export MODEL_ID="claude-sonnet-4-20250514"\n'
        )
        sys.exit(1)

    if not model_id:
        model_id = "claude-sonnet-4-20250514"

    client = Anthropic(api_key=api_key, base_url=base_url)
    register_delegate_tool(client)
    _al.MODEL_ID = model_id

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    conversation_history: list[dict] = []

    # Resume saved session
    if args.resume:
        loaded = load_session(args.resume)
        if loaded:
            conversation_history, loaded_model = loaded
            if not args.model:
                model_id = loaded_model
                _al.MODEL_ID = model_id
            console.print(f"[green]Resumed session: {args.resume} (model: {model_id})[/green]")
        else:
            console.print(f"[red]Session '{args.resume}' not found.[/red]")
            sys.exit(1)

    # One-shot mode
    if args.prompt:
        _run_once(client, model_id, args.prompt, conversation_history)
        return

    # Interactive REPL
    _repl(client, model_id, conversation_history)


def _run_once(client: Anthropic, model_id: str, prompt: str, messages: list[dict]):
    streamed: list[str] = []

    def on_content(text: str):
        streamed.append(text)
        print(text, end="", flush=True)

    def on_tool_start(name: str, kwargs: dict):
        console.print(f"\n[dim]> {name}({_brief(kwargs)})[/dim]")

    def on_tool_result(name: str, result: str):
        pass

    response, messages = agent_loop(
        client, prompt,
        on_content=on_content,
        on_tool_start=on_tool_start,
        on_tool_result=on_tool_result,
        messages=messages,
    )

    if streamed:
        print()
    else:
        console.print(Markdown(response))

def _repl(client: Anthropic, model_id: str, conversation_history: list[dict]):
    """Interactive read-eval-print loop."""
    console.print(Panel(
        f"[bold]Penguin Coding Agent[/bold] v{__version__}\n"
        f"Model: [cyan]{model_id}[/cyan]"
        + (f"  Base: [dim]{client.base_url}[/dim]" if getattr(client, "base_url", None) else "")
        + f"\nWorkspace: [dim]{ALLOWED_BASE_DIR}[/dim]"
        + "\nType [bold]/help[/bold] for commands, [bold]Ctrl+C[/bold] to cancel, [bold]quit[/bold] to exit.",
        border_style="blue",
    ))

    hist_path = os.path.expanduser("~/.penguin_history")
    history = FileHistory(hist_path)

    # Enter submits, Escape+Enter inserts a newline (for pasting code blocks etc.)
    kb = KeyBindings()

    @kb.add("enter")
    def _submit(event):
        event.current_buffer.validate_and_handle()

    @kb.add("escape", "enter")
    def _newline(event):
        event.current_buffer.insert_text("\n")

    while True:
        try:
            user_input = pt_prompt(
                "You > ",
                history=history,
                multiline=True,
                key_bindings=kb,
                prompt_continuation="...  ",
            ).strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye!")
            break

        if not user_input:
            continue

        # Built-in commands
        if user_input.lower() in ("quit", "exit", "/quit", "/exit"):
            break
        if user_input == "/help":
            _show_help()
            continue
        if user_input == "/reset":
            conversation_history.clear()
            _changed_files.clear()
            console.print("[yellow]Conversation reset.[/yellow]")
            continue
        if user_input == "/model" or user_input.startswith("/model "):
            new_model = user_input[7:].strip() if user_input.startswith("/model ") else ""
            if new_model:
                _al.MODEL_ID = new_model
                model_id = new_model
                console.print(f"Switched to [cyan]{new_model}[/cyan]")
            else:
                console.print(f"Current model: [cyan]{model_id}[/cyan]")
            continue
        if user_input == "/tokens":
            p = usage_stats["prompt_tokens"]
            c = usage_stats["completion_tokens"]
            console.print(
                f"Tokens: [cyan]{p}[/cyan] prompt + [cyan]{c}[/cyan] completion = [bold]{p+c}[/bold] total"
            )
            continue
        if user_input == "/compact":
            before = estimate_tokens(str(conversation_history))
            compressed = llm_compact_messages(
                conversation_history, client, model_id, max_tokens=MAX_CONTEXT_TOKENS
            )
            conversation_history[:] = compressed
            after = estimate_tokens(str(conversation_history))
            if before != after:
                console.print(f"[green]Compressed: {before} -> {after} estimated tokens ({len(conversation_history)} messages)[/green]")
            else:
                console.print(f"[dim]Nothing to compress ({before} estimated tokens, {len(conversation_history)} messages)[/dim]")
            continue
        if user_input == "/diff":
            if not _changed_files:
                console.print("[dim]No files modified this session.[/dim]")
            else:
                console.print(f"[bold]Files modified this session ({len(_changed_files)}):[/bold]")
                for f in sorted(_changed_files):
                    console.print(f"  [cyan]{f}[/cyan]")
            continue
        if user_input == "/save":
            sid = save_session(conversation_history, model_id)
            console.print(f"[green]Session saved: {sid}[/green]")
            console.print(f"Resume with: penguin -r {sid}")
            continue
        if user_input == "/sessions":
            sessions = list_sessions()
            if not sessions:
                console.print("[dim]No saved sessions.[/dim]")
            else:
                for s in sessions:
                    console.print(f"  [cyan]{s['id']}[/cyan] ({s['model']}, {s['saved_at']}) {s['preview']}")
            continue

        # Unknown slash command
        if user_input.startswith("/"):
            console.print(f"[yellow]Unknown command: {user_input}[/yellow]")
            continue

        # Call the agent
        streamed: list[str] = []

        def on_content(text: str):
            streamed.append(text)
            print(text, end="", flush=True)

        def on_tool_start(name: str, kwargs: dict):
            console.print(f"\n[dim]> {name}({_brief(kwargs)})[/dim]")

        def on_tool_result(name: str, result: str):
            preview = result[:200] + "..." if len(result) > 200 else result
            console.print(f"[dim][Result: {preview}][/dim]")

        try:
            response, conversation_history = agent_loop(
                client, user_input,
                max_iterations=500,
                on_content=on_content,
                on_tool_start=on_tool_start,
                on_tool_result=on_tool_result,
                messages=conversation_history,
            )
            if streamed:
                print()
            else:
                console.print(Markdown(response))
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


def _show_help():
    console.print(Panel(
        "[bold]Commands:[/bold]\n"
        "  /help          Show this help\n"
        "  /reset         Clear conversation history\n"
        "  /model         Show current model\n"
        "  /model <name>  Switch model mid-conversation\n"
        "  /tokens        Show token usage\n"
        "  /compact       Compress conversation context\n"
        "  /diff          Show files modified this session\n"
        "  /save          Save session to disk\n"
        "  /sessions      List saved sessions\n"
        "  quit           Exit Penguin\n"
        "\n"
        "[bold]Input:[/bold]\n"
        "  Enter          Submit message\n"
        "  Esc+Enter      Insert newline (for pasting code)",
        title="Penguin Help",
        border_style="dim",
    ))


def _brief(kwargs: dict, maxlen: int = 80) -> str:
    s = ", ".join(f"{k}={repr(v)[:40]}" for k, v in kwargs.items())
    return s[:maxlen] + ("..." if len(s) > maxlen else "")
