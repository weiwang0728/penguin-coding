"""Tool dispatcher: registration, validation, and dispatch."""

from typing import Any, Callable

from .base import Tool


class ToolDispatcher:
    def __init__(self) -> None:
        self._registry: dict[str, Tool] = {}
        self._dynamic_handlers: dict[str, Callable[..., str]] = {}

    def register(self, tool: Tool) -> None:
        """Register a Tool instance."""
        self._registry[tool.name] = tool

    def register_dynamic(self, name: str, handler: Callable[..., str], schema: dict[str, Any] | None = None) -> None:
        """Register a dynamic handler (e.g. delegate that needs runtime deps)."""
        self._dynamic_handlers[name] = handler
        if schema:
            self._dynamic_handlers[f"__schema__{name}"] = schema  # type: ignore[assignment]

    def dispatch(self, name: str, args: dict[str, Any]) -> str:
        # Check dynamic handlers first (e.g. delegate)
        if name in self._dynamic_handlers:
            try:
                return self._dynamic_handlers[name](**args)
            except TypeError as e:
                return f"Error calling tool '{name}': {e}"

        if name not in self._registry:
            return f"Unknown tool: {name}"
        tool = self._registry[name]
        errors = self._validate_args(name, args)
        if errors:
            return f"Error: invalid arguments for '{name}': {'; '.join(errors)}"
        try:
            return tool.execute(**args)
        except TypeError as e:
            return f"Error calling tool '{name}': {e}"

    def list_tools(self) -> list[str]:
        names = list(self._registry.keys())
        names.extend(k for k in self._dynamic_handlers if not k.startswith("__schema__"))
        return names

    def get_tool_definitions(self) -> list[dict]:
        """Build the TOOL_DEFINITIONS list for the LLM API."""
        definitions = [tool.schema() for tool in self._registry.values()]
        # Add dynamic handler schemas
        for key, value in self._dynamic_handlers.items():
            if key.startswith("__schema__"):
                name = key[len("__schema__"):]
                definitions.append(value)
        return definitions

    def _validate_args(self, name: str, args: dict[str, Any]) -> list[str]:
        tool = self._registry.get(name)
        if not tool:
            return []
        input_schema = tool.parameters
        errors: list[str] = []
        required = input_schema.get("required", [])
        for field in required:
            if field not in args:
                errors.append(f"missing required field '{field}'")
        properties = input_schema.get("properties", {})
        for key, value in args.items():
            if key not in properties:
                errors.append(f"unexpected field '{key}'")
                continue
            expected_type = properties[key].get("type")
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"field '{key}' must be a string")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"field '{key}' must be an integer")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"field '{key}' must be an array")
        return errors


dispatcher = ToolDispatcher()


def execute_tool(name: str, args: dict[str, Any]) -> str:
    return dispatcher.dispatch(name, args)
