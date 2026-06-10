"""Agent class — dynamically assembled tools and skills per instance."""

import logging
from typing import Any, Callable

from ._constants import ALLOWED_BASE_DIR
from .tool_registry import ToolRegistry
from .tools.dispatcher import ToolDispatcher
from .permissions import PermissionManager
from .permissions_config import load_permissions_config
from .skill_loader import SkillLoader, SKILLS_DIR

logger = logging.getLogger("penguin")

ContentCallback = Callable[[str], None]
ToolStartCallback = Callable[[str, dict], None]
ToolResultCallback = Callable[[str, str], None]
ConfirmCallback = Callable[[str, dict, str], bool]


class Agent:
    """An agent with its own tools, skills, permissions, and system prompt.

    Each Agent instance holds an independent ToolDispatcher, SkillLoader, and
    PermissionManager. Create multiple agents with different tool sets for
    different tasks.
    """

    def __init__(
        self,
        name: str = "penguin",
        tools: list[str] | None = None,
        skills: list[str] | None = None,
        system_prompt: str | None = None,
        permission_profile: str = "standard",
        max_iterations: int = 100,
        parallel_enabled: bool = True,
        parallel_max_workers: int = 4,
    ):
        self.name = name
        self.max_iterations = max_iterations
        self.parallel_enabled = parallel_enabled
        self.parallel_max_workers = parallel_max_workers

        # Independent dispatcher
        self.dispatcher = ToolDispatcher()
        tool_names = tools if tools is not None else ToolRegistry.all_names()
        for tname in tool_names:
            inst = ToolRegistry.create_instance(tname)
            if inst:
                self.dispatcher.register(inst)
            else:
                logger.warning("Agent '%s': unknown tool '%s', skipping", name, tname)

        # Independent permission manager
        config = load_permissions_config()
        config["profile"] = permission_profile
        self.permission_manager = PermissionManager(config)
        self.permission_manager.set_registry(self.dispatcher._registry)
        self.dispatcher.set_permission_manager(self.permission_manager)

        # Independent skill loader
        self.skill_loader = SkillLoader(SKILLS_DIR, initial_skills=skills)

        # System prompt
        self._custom_system_prompt = system_prompt

    @property
    def tool_definitions(self) -> list[dict]:
        return self.dispatcher.get_tool_definitions()

    @property
    def active_tools(self) -> list[str]:
        return self.dispatcher.list_tools()

    @property
    def active_skills(self) -> set[str]:
        return self.skill_loader.active_skills

    def _build_system_prompt(self) -> str:
        if self._custom_system_prompt:
            return self._custom_system_prompt
        skill_descs = self.skill_loader.get_descriptions()
        return (
            f"You are a helpful coding assistant at {ALLOWED_BASE_DIR}. "
            f"You can help users with software engineering tasks.\n\n"
            f"Core principles:\n"
            f"- COMPLETE every task you start. Never stop mid-work to summarize or explain unless the user asks.\n"
            f"- When you encounter errors, fix them. Do not just report the error and stop.\n"
            f"- Prefer action over exploration. Read only what you need, then start writing code immediately.\n"
            f"- Use the task tool to track progress. Break large work into sub-tasks.\n"
            f"- Batch related tool calls in a single response when possible (e.g., read multiple files at once).\n"
            f"- If a task has multiple steps, complete ALL steps before responding to the user.\n"
            f"- Use load_skill when a task needs specialized instructions before you act.\n\n"
            f"Skills available:\n{skill_descs}\n\n"
            f"When writing code, always provide complete and correct implementations."
        )

    # ── Dynamic tool management ──

    def add_tool(self, name: str) -> str:
        """Add a tool from the ToolRegistry at runtime."""
        if name in self.dispatcher._registry or name in self.dispatcher._dynamic_handlers:
            return f"Tool '{name}' already registered"
        inst = ToolRegistry.create_instance(name)
        if not inst:
            return f"Unknown tool: '{name}'. Available: {ToolRegistry.all_names()}"
        self.dispatcher.register(inst)
        self.permission_manager.set_registry(self.dispatcher._registry)
        return f"Tool '{name}' added"

    def remove_tool(self, name: str) -> str:
        """Remove a tool at runtime."""
        if name in self.dispatcher._registry:
            del self.dispatcher._registry[name]
            self.permission_manager.set_registry(self.dispatcher._registry)
            return f"Tool '{name}' removed"
        if name in self.dispatcher._dynamic_handlers:
            # Remove dynamic handler + its schema
            keys_to_remove = [name, f"__schema__{name}"]
            for k in keys_to_remove:
                self.dispatcher._dynamic_handlers.pop(k, None)
            return f"Dynamic tool '{name}' removed"
        return f"Tool '{name}' not found"

    def register_dynamic_tool(
        self, name: str, handler: Callable[..., str], schema: dict[str, Any] | None = None
    ) -> None:
        """Register a dynamic tool (e.g. delegate)."""
        self.dispatcher.register_dynamic(name, handler, schema)

    # ── Dynamic skill management ──

    def load_skill(self, name: str) -> str:
        """Activate a skill and update system prompt."""
        result = self.skill_loader.activate(name)
        return result

    def unload_skill(self, name: str) -> str:
        """Deactivate a skill and update system prompt."""
        return self.skill_loader.deactivate(name)

    # ── Execution ──

    def run(
        self,
        client,
        user_message: str,
        messages: list[dict[str, Any]] | None = None,
        on_content: ContentCallback | None = None,
        on_tool_start: ToolStartCallback | None = None,
        on_tool_result: ToolResultCallback | None = None,
        confirm_callback: ConfirmCallback | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Run the agent loop with this agent's tools, skills, and prompt."""
        from .agent_loop import agent_loop
        from ._constants import client as default_client
        _client = client or default_client
        return agent_loop(
            _client,
            user_message,
            max_iterations=self.max_iterations,
            on_content=on_content,
            on_tool_start=on_tool_start,
            on_tool_result=on_tool_result,
            confirm_callback=confirm_callback,
            messages=messages,
            tool_dispatcher=self.dispatcher,
            tools=self.tool_definitions,
            system_prompt=self._build_system_prompt(),
            parallel_enabled=self.parallel_enabled,
            parallel_max_workers=self.parallel_max_workers,
        )

    def run_subagent(
        self,
        client,
        prompt: str,
        max_iterations: int = 20,
    ) -> str:
        """Run a subagent using this agent's tool set (minus delegate)."""
        from .agent_loop import run_subagent_with_tools
        from ._constants import client as default_client
        _client = client or default_client
        return run_subagent_with_tools(
            _client,
            prompt,
            max_iterations=max_iterations,
            tools=self.tool_definitions,
            system_prompt=self._build_subagent_prompt(),
            tool_dispatcher=self.dispatcher,
        )

    def _build_subagent_prompt(self) -> str:
        return (
            f"You are a focused coding sub-agent at {ALLOWED_BASE_DIR}. "
            f"Complete the given task thoroughly.\n"
            f"When finished, provide a concise summary of:\n"
            f"1. What you did (files read/written/edited, commands run)\n"
            f"2. Key findings or results\n"
            f"3. Any errors encountered\n\n"
            f"Be thorough in execution but concise in your summary. "
            f"Do NOT delegate — complete the work yourself."
        )
