"""Tests for tool_registry.py and tools/base.py."""

import pytest

from src.tool_registry import ToolRegistry, register_tool
from src.tools.base import Tool


class TestToolRegistry:
    def test_all_tools_registered(self):
        names = ToolRegistry.all_names()
        assert "read_file" in names
        assert "write_file" in names
        assert "run_command" in names
        assert "edit_file" in names
        assert "search_files" in names
        assert "list_directory" in names
        assert "task" in names
        assert "load_skill" in names
        assert "background_run" in names
        assert "check_background" in names
        assert "team_spawn" in names
        assert "team_send" in names
        assert "team_broadcast" in names
        assert "team_list" in names
        assert "team_shutdown" in names
        assert len(names) >= 15

    def test_get_tool_class(self):
        cls = ToolRegistry.get("read_file")
        assert cls is not None
        assert cls.name == "read_file"

    def test_get_unknown_returns_none(self):
        assert ToolRegistry.get("nonexistent_tool_xyz") is None

    def test_create_instance(self):
        inst = ToolRegistry.create_instance("read_file")
        assert inst is not None
        assert inst.name == "read_file"
        assert hasattr(inst, "execute")

    def test_create_unknown_returns_none(self):
        assert ToolRegistry.create_instance("nonexistent_tool_xyz") is None

    def test_has(self):
        assert ToolRegistry.has("read_file") is True
        assert ToolRegistry.has("nonexistent_tool_xyz") is False


class TestRegisterToolDecorator:
    def test_register_tool_decorator(self):
        @register_tool
        class _TestTool(Tool):
            name = "_test_registry_tool"
            description = "Test"
            parameters = {"type": "object", "properties": {}, "required": []}

            def execute(self, **kwargs):
                return "ok"

        assert ToolRegistry.has("_test_registry_tool")
        inst = ToolRegistry.create_instance("_test_registry_tool")
        assert inst is not None

    def test_register_tool_no_name_raises(self):
        with pytest.raises(ValueError, match="must define a 'name'"):
            @register_tool
            class _BadTool(Tool):
                description = "No name"
                parameters = {"type": "object", "properties": {}, "required": []}

                def execute(self, **kwargs):
                    return "ok"


class TestToolBaseClass:
    def test_schema_format(self):
        inst = ToolRegistry.create_instance("read_file")
        schema = inst.schema()
        assert schema["name"] == "read_file"
        assert "description" in schema
        assert "input_schema" in schema
        assert schema["input_schema"]["type"] == "object"

    def test_default_permission_level(self):
        inst = ToolRegistry.create_instance("read_file")
        assert inst.default_permission_level == "allow"
        write_inst = ToolRegistry.create_instance("write_file")
        assert write_inst.default_permission_level == "confirm"

    def test_execute_abstract(self):
        """Tool subclasses must implement execute."""
        with pytest.raises(TypeError):
            Tool()
