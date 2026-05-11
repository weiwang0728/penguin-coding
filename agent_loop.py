import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Generator

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL_ID = os.getenv("MODEL_ID")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

ALLOWED_BASE_DIR = Path(os.getcwd()).resolve()

DANGEROUS_COMMANDS = [
    r"\brm\s+-rf\s+/",
    r"\brm\s+-rf\s+~",
    r"\brm\s+-rf\s+\$HOME",
    r"\bmkfs\.",
    r"\bdd\s+if=.*of=/dev/",
    r"\b:(){ :|:& };:",
    r"\bchmod\s+-R\s+777\s+/",
    r"\bchown\s+-R\s+.*\s+/",
    r"\bsudo\s+rm\s+-rf",
    r"\bsu\s+-",
    r"\bpasswd\b",
    r"\buseradd\b",
    r"\busermod\b",
    r"\bgroupadd\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+0",
    r"\bsystemctl\s+(stop|restart)\s+(ssh|network|systemd)",
    r"\bkubectl\s+delete\s+.*--all",
    r"\bdocker\s+(rm|kill)\s+.*\*",
    r"\bcurl\s+.*\|\s*sh",
    r"\bwget\s+.*\|\s*sh",
    r"\beval\s*\$",
    r"\bexec\s*\$",
    r">\s*/etc/passwd",
    r">\s*/etc/shadow",
    r">\s+/dev/(sda|nvme|hd)",
]

DANGEROUS_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_COMMANDS]

SYSTEM_PROMPT = f"""You are a helpful coding assistant at {ALLOWED_BASE_DIR}. You can help users with software engineering tasks.
When writing code, always provide complete and correct implementations.
Think step by step and explain your reasoning clearly."""

TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return its output",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                }
            },
            "required": ["command"],
        },
    },
]


class ToolDispatcher:
    _registry: dict[str, Callable[..., str]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
        def decorator(func: Callable[..., str]) -> Callable[..., str]:
            cls._registry[name] = func
            return func

        return decorator

    @classmethod
    def dispatch(cls, name: str, args: dict[str, Any]) -> str:
        if name not in cls._registry:
            return f"Unknown tool: {name}"
        return cls._registry[name](**args)

    @classmethod
    def list_tools(cls) -> list[str]:
        return list(cls._registry.keys())


def resolve_and_validate_path(path: str) -> Path:
    try:
        resolved = (ALLOWED_BASE_DIR / path).resolve()
        resolved.relative_to(ALLOWED_BASE_DIR)
        return resolved
    except (ValueError, RuntimeError):
        raise PermissionError(
            f"Path '{path}' is outside the allowed directory: {ALLOWED_BASE_DIR}"
        )


def check_dangerous_command(command: str) -> str | None:
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return f"Dangerous command detected and blocked: pattern '{pattern.pattern}'"
    return None


@ToolDispatcher.register("read_file")
def read_file(path: str) -> str:
    try:
        resolved_path = resolve_and_validate_path(path)
        with open(resolved_path, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError as e:
        return f"Error: {e}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except UnicodeDecodeError:
        return f"Error: Cannot read binary file: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@ToolDispatcher.register("write_file")
def write_file(path: str, content: str) -> str:
    try:
        resolved_path = resolve_and_validate_path(path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error writing file: {e}"


@ToolDispatcher.register("run_command")
def run_command(command: str) -> str:
    danger_check = check_dangerous_command(command)
    if danger_check:
        return f"Error: {danger_check}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ALLOWED_BASE_DIR,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds"
    except Exception as e:
        return f"Error running command: {e}"


def execute_tool(name: str, args: dict[str, Any]) -> str:
    return ToolDispatcher.dispatch(name, args)


def stream_response(
    client: anthropic.Anthropic, messages: list[dict[str, Any]]
) -> Generator[tuple[str, Any], None, None]:
    tool_use_blocks: dict[int, dict[str, Any]] = {}

    with client.messages.stream(
        model=MODEL_ID,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=TOOL_DEFINITIONS,
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    yield ("content", event.delta.text)

                elif event.delta.type == "input_json_delta":
                    for idx in tool_use_blocks:
                        if not tool_use_blocks[idx].get("_complete"):
                            tool_use_blocks[idx]["_partial_json"] += (
                                event.delta.partial_json
                            )

            elif event.type == "content_block_start":
                if event.content_block.type == "tool_use":
                    tool_use_blocks[event.index] = {
                        "id": event.content_block.id,
                        "name": event.content_block.name,
                        "_partial_json": "",
                        "_complete": False,
                    }

            elif event.type == "content_block_stop":
                if event.index in tool_use_blocks:
                    block = tool_use_blocks[event.index]
                    block["_complete"] = True
                    block["input"] = (
                        json.loads(block["_partial_json"])
                        if block["_partial_json"]
                        else {}
                    )

        final_message = stream.get_final_message()

    tool_calls_list = []
    for idx in sorted(tool_use_blocks):
        block = tool_use_blocks[idx]
        tool_calls_list.append(
            {
                "id": block["id"],
                "name": block["name"],
                "input": block["input"],
            }
        )

    if tool_calls_list:
        yield ("tool_calls", tool_calls_list)


def agent_loop(
    client: anthropic.Anthropic,
    user_message: str,
    max_iterations: int = 10,
    on_content: Any = None,
    on_tool_start: Any = None,
    on_tool_result: Any = None,
) -> str:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": user_message},
    ]

    for iteration in range(max_iterations):
        collected_content = ""
        has_tool_calls = False
        tool_calls_list = []

        for event_type, data in stream_response(client, messages):
            if event_type == "content":
                collected_content += data
                if on_content:
                    on_content(data)

            elif event_type == "tool_calls":
                has_tool_calls = True
                tool_calls_list = data

        assistant_content: list[dict[str, Any]] = []
        if collected_content:
            assistant_content.append({"type": "text", "text": collected_content})
        for tc in tool_calls_list:
            assistant_content.append(
                {
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                }
            )

        messages.append({"role": "assistant", "content": assistant_content})

        if not has_tool_calls:
            return collected_content

        tool_results: list[dict[str, Any]] = []
        for tc in tool_calls_list:
            fn_name = tc["name"]
            fn_args = tc["input"]

            if on_tool_start:
                on_tool_start(fn_name, fn_args)

            result = execute_tool(fn_name, fn_args)

            if on_tool_result:
                on_tool_result(fn_name, result)

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": result,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return "Agent reached maximum iterations without completing the task."


def main():
    client = anthropic.Anthropic(
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    print(f"Penguin Coding Agent (working directory: {ALLOWED_BASE_DIR})")
    print("-" * 50)
    print(f"Available tools: {', '.join(ToolDispatcher.list_tools())}")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        print("\nAgent: ", end="", flush=True)

        def on_content(text: str):
            print(text, end="", flush=True)

        def on_tool_start(name: str, args: dict):
            print(
                f"\n[Tool: {name}({json.dumps(args, ensure_ascii=False)})]", flush=True
            )

        def on_tool_result(name: str, result: str):
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"[Result: {preview}]", flush=True)
            print("\nAgent: ", end="", flush=True)

        final_response = agent_loop(
            client,
            user_input,
            max_iterations=10,
            on_content=on_content,
            on_tool_start=on_tool_start,
            on_tool_result=on_tool_result,
        )

        print()


if __name__ == "__main__":
    main()
