"""Global tool registry — stores tool classes for Agent to pick from."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tools.base import Tool


class ToolRegistry:
    """Global catalog of tool classes. Agents select and instantiate what they need."""

    _tools: dict[str, type["Tool"]] = {}

    @classmethod
    def register(cls, tool_cls: type["Tool"]) -> None:
        cls._tools[tool_cls.name] = tool_cls

    @classmethod
    def get(cls, name: str) -> type["Tool"] | None:
        return cls._tools.get(name)

    @classmethod
    def all_names(cls) -> list[str]:
        return list(cls._tools.keys())

    @classmethod
    def create_instance(cls, name: str) -> "Tool | None":
        tool_cls = cls._tools.get(name)
        return tool_cls() if tool_cls else None

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._tools


def register_tool(cls):
    """Decorator: explicitly register a Tool subclass into the global registry."""
    if not getattr(cls, "name", None):
        raise ValueError(f"Tool class {cls.__name__} must define a 'name' attribute")
    ToolRegistry.register(cls)
    return cls
