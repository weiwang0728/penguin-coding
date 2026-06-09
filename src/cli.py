"""Interactive REPL — the user-facing terminal interface."""

import sys
import os
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
from .tools import _changed_files
from ._constants import ALLOWED_BASE_DIR
from .agent import Agent
from .session import load_session, list_sessions, autosave_session
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
    p.add_argument("--permissions", choices=["permissive", "standard", "strict"],
                   default=None, help="Permission profile (default: standard)")
    p.add_argument("--tools", nargs="+", default=None,
                   help="Tool names to enable (default: all)")
    p.add_argument("--skills", nargs="+", default=None,
                   help="Initial skills to activate (default: all)")
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
    _al.MODEL_ID = model_id

    # Create Agent instance
    agent = Agent(
        name="penguin",
        tools=args.tools,
        skills=args.skills,
        permission_profile=args.permissions or "standard",
    )

    # Register delegate tool on the agent's dispatcher
    from .tools import DELEGATE_SCHEMA
    def _make_delegate_handler(client):
        from .agent_loop import run_subagent
        def handle_delegate(prompt: str, max_iterations: int = 20) -> str:
            return run_subagent(client, prompt, max_iterations)
        return handle_delegate

    agent.register_dynamic_tool("delegate", _make_delegate_handler(client), DELEGATE_SCHEMA)

    # Also register on the global dispatcher for backward compat
    register_delegate_tool(client)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    conversation_history: list[dict] = []

    # Resume saved session
    if args.resume:
        loaded = load_session(args.resume)
        if loaded:
            conversation_history, loaded_model, loaded_usage = loaded
            if not args.model:
                model_id = loaded_model
                _al.MODEL_ID = model_id
            if loaded_usage:
                usage_stats.update(loaded_usage)
            console.print(f"[green]Resumed session: {args.resume} (model: {model_id})[/green]")
        else:
            console.print(f"[red]Session '{args.resume}' not found.[/red]")
            sys.exit(1)

    # One-shot mode
    if args.prompt:
        _run_once(agent, args.prompt, conversation_history)
        return

    # Interactive REPL
    _repl(agent, model_id, conversation_history)


def _run_once(agent: Agent, prompt: str, messages: list[dict]):
    streamed: list[str] = []

    def on_content(text: str):
        streamed.append(text)
        print(text, end="", flush=True)

    def on_tool_start(name: str, kwargs: dict):
        console.print(f"\n[dim]> {name}({_brief(kwargs)})[/dim]")

    def on_tool_result(name: str, result: str):
        pass

    # Non-interactive: permissive profile allows all, otherwise deny confirm-tier tools
    if agent.permission_manager.profile == "permissive":
        confirm_cb = lambda name, args, reason: True
    else:
        confirm_cb = lambda name, args, reason: False

    response, messages = agent.run(
        client=None,  # will be set by agent_loop via module-level client
        user_message=prompt,
        on_content=on_content,
        on_tool_start=on_tool_start,
        on_tool_result=on_tool_result,
        confirm_callback=confirm_cb,
        messages=messages,
    )

    if streamed:
        print()
    else:
        console.print(Markdown(response))


def _repl(agent: Agent, model_id: str, conversation_history: list[dict]):
    """Interactive read-eval-print loop."""
    console.print(Panel(
        f"[bold]Penguin Coding Agent[/bold] v{__version__}\n"
        f"Model: [cyan]{model_id}[/cyan]"
        + "\n"
        + f"Tools: [dim]{', '.join(agent.active_tools)}[/dim]"
        + "\n"
        + f"Skills: [dim]{', '.join(sorted(agent.active_skills)) if agent.active_skills else 'none'}[/dim]"
        + "\nWorkspace: [dim]{ALLOWED_BASE_DIR}[/dim]"
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
            if conversation_history:
                sid = autosave_session(conversation_history, model_id, usage_stats)
                console.print(f"\n[dim]Session auto-saved: {sid}[/dim]")
            console.print("Bye!")
            break

        if not user_input:
            continue

        # Built-in commands
        if user_input.lower() in ("quit", "exit", "/quit", "/exit"):
            if conversation_history:
                sid = autosave_session(conversation_history, model_id, usage_stats)
                console.print(f"[dim]Session auto-saved: {sid}[/dim]")
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
            last_in = usage_stats.get("last_input_tokens", 0)
            pending = usage_stats.get("pending_delta", 0)
            est_total = last_in + pending
            console.print(
                f"Tokens: [cyan]{p}[/cyan] prompt + [cyan]{c}[/cyan] completion = [bold]{p+c}[/bold] total\n"
                f"Context: [cyan]{last_in}[/cyan] last API input + [cyan]{pending}[/cyan] pending delta ≈ [bold]{est_total}[/bold]"
            )
            continue
        if user_input == "/permissions" or user_input.startswith("/permissions "):
            new_profile = user_input[13:].strip() if user_input.startswith("/permissions ") else ""
            if new_profile:
                if new_profile in ("permissive", "standard", "strict"):
                    agent.permission_manager.profile = new_profile
                    agent.permission_manager.reset_session_allowlist()
                    console.print(f"Switched to [cyan]{new_profile}[/cyan] permission profile")
                else:
                    console.print("[red]Invalid profile. Choose: permissive, standard, strict[/red]")
            else:
                console.print(
                    f"Permission profile: [cyan]{agent.permission_manager.profile}[/cyan]\n"
                    f"Session allowlist: {agent.permission_manager._session_allowlist or '(none)'}\n\n"
                    f"Usage: /permissions <permissive|standard|strict>"
                )
            continue
        if user_input == "/tools":
            console.print(
                f"[bold]Active tools ({len(agent.active_tools)}):[/bold]\n"
                + "\n".join(f"  [cyan]{t}[/cyan]" for t in agent.active_tools)
            )
            continue
        if user_input.startswith("/add_tool "):
            tool_name = user_input[10:].strip()
            result = agent.add_tool(tool_name)
            console.print(result)
            continue
        if user_input.startswith("/remove_tool "):
            tool_name = user_input[13:].strip()
            result = agent.remove_tool(tool_name)
            console.print(result)
            continue
        if user_input.startswith("/load_skill "):
            skill_name = user_input[12:].strip()
            result = agent.load_skill(skill_name)
            console.print(result)
            continue
        if user_input.startswith("/unload_skill "):
            skill_name = user_input[14:].strip()
            result = agent.unload_skill(skill_name)
            console.print(result)
            continue
        if user_input == "/compact":
            before = estimate_tokens(str(conversation_history))
            compressed = llm_compact_messages(
                conversation_history, client=None, model_id=model_id, max_tokens=MAX_CONTEXT_TOKENS
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
        if user_input.startswith("/resume"):
            target = user_input[7:].strip()
            sessions = list_sessions()
            if not sessions:
                console.print("[dim]No saved sessions.[/dim]")
                continue
            if not target:
                for s in sessions:
                    console.print(f"  [cyan]{s['id']}[/cyan] {s['name']} ({s['model']}, {s['saved_at']})")
                console.print("\nUsage: /resume <session_id>")
                continue
            loaded = load_session(target)
            if loaded:
                conversation_history.clear()
                conversation_history.extend(loaded[0])
                model_id = loaded[1]
                _al.MODEL_ID = model_id
                loaded_usage = loaded[2]
                if loaded_usage:
                    usage_stats.update(loaded_usage)
                console.print(f"[green]Resumed session: {target} (model: {model_id})[/green]")
            else:
                console.print(f"[red]Session '{target}' not found.[/red]")
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

        def _render_diff(text: str) -> str:
            lines = text.split("\n")
            rendered = []
            for line in lines:
                if line.startswith("---") or line.startswith("+++"):
                    rendered.append(f"[bold]{line}[/bold]")
                elif line.startswith("@@"):
                    rendered.append(f"[cyan]{line}[/cyan]")
                elif line.startswith("-"):
                    rendered.append(f"[red]{line}[/red]")
                elif line.startswith("+"):
                    rendered.append(f"[green]{line}[/green]")
                else:
                    rendered.append(line)
            return "\n".join(rendered)

        def on_tool_start(name: str, kwargs: dict):
            console.print(f"\n> {name}({_brief(kwargs)})")

        def on_tool_result(name: str, result: str):
            if name in ("write_file", "edit_file"):
                if "\n\n--- " in result:
                    summary, diff_part = result.split("\n\n", 1)
                    console.print(f"[Result: {summary}]")
                    console.print(_render_diff(diff_part))
                else:
                    console.print(f"[Result: {result}]")
            else:
                preview = result[:200] + "..." if len(result) > 200 else result
                console.print(f"[Result: {preview}]")

        try:
            response, conversation_history = agent.run(
                client=None,  # agent_loop uses module-level client
                user_message=user_input,
                on_content=on_content,
                on_tool_start=on_tool_start,
                on_tool_result=on_tool_result,
                confirm_callback=_confirm_tool,
                messages=conversation_history,
            )
            if conversation_history:
                autosave_session(conversation_history, model_id, usage_stats)
            if streamed:
                print()
            else:
                console.print(Markdown(response))
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


def _confirm_tool(name: str, args: dict, reason: str) -> bool:
    """Prompt the user for tool confirmation. Returns True if approved."""
    from .tools import permission_manager
    console.print(Panel(
        f"[bold yellow]Permission Required[/bold yellow]\n\n"
        f"Tool: [cyan]{name}[/cyan]\n"
        f"Args: {_brief(args, maxlen=200)}\n"
        f"Reason: {reason}\n\n"
        f"[dim]Press Enter to allow, 'n' to deny, 'a' to always allow this tool[/dim]",
        border_style="yellow",
    ))
    try:
        response = pt_prompt("Allow? [Y/n/a] ").strip().lower()
        if response in ("a", "always"):
            permission_manager.allow_for_session(name)
            return True
        return response in ("", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


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
        "  /tools         Show active tools\n"
        "  /add_tool <name>       Add a tool at runtime\n"
        "  /remove_tool <name>    Remove a tool at runtime\n"
        "  /load_skill <name>     Activate a skill\n"
        "  /unload_skill <name>   Deactivate a skill\n"
        "  /permissions   Show current permission profile\n"
        "  /permissions <profile>  Switch profile (permissive|standard|strict)\n"
        "  /resume        List saved sessions\n"
        "  /resume <id>   Resume a saved session\n"
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
