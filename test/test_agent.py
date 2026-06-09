"""Tests for ToolRegistry and Agent class."""

import pytest

from src.tool_registry import ToolRegistry
from src.agent import Agent
from src.permissions import PermissionLevel


class TestToolRegistry:
    def test_all_tools_registered(self):
        names = ToolRegistry.all_names()
        assert "read_file" in names
        assert "write_file" in names
        assert "run_command" in names
        assert len(names) >= 15

    def test_get_tool_class(self):
        cls = ToolRegistry.get("read_file")
        assert cls is not None
        assert cls.name == "read_file"

    def test_get_unknown_returns_none(self):
        assert ToolRegistry.get("nonexistent_tool") is None

    def test_create_instance(self):
        inst = ToolRegistry.create_instance("read_file")
        assert inst is not None
        assert inst.name == "read_file"
        assert hasattr(inst, "execute")

    def test_create_unknown_returns_none(self):
        assert ToolRegistry.create_instance("nonexistent_tool") is None

    def test_has(self):
        assert ToolRegistry.has("read_file")
        assert not ToolRegistry.has("nonexistent_tool")


class TestAgentCreation:
    def test_default_agent_has_all_tools(self):
        agent = Agent(name="test_default")
        assert len(agent.active_tools) >= 15
        assert "read_file" in agent.active_tools
        assert "write_file" in agent.active_tools
        assert "run_command" in agent.active_tools

    def test_custom_tool_set(self):
        agent = Agent(name="minimal", tools=["read_file", "list_directory"])
        assert agent.active_tools == ["read_file", "list_directory"]

    def test_unknown_tools_ignored(self):
        agent = Agent(name="safe", tools=["read_file", "nonexistent"])
        assert agent.active_tools == ["read_file"]

    def test_tool_definitions_count(self):
        agent = Agent(name="test", tools=["read_file", "write_file"])
        assert len(agent.tool_definitions) == 2

    def test_tool_definitions_have_schema(self):
        agent = Agent(name="test", tools=["read_file"])
        defs = agent.tool_definitions
        assert defs[0]["name"] == "read_file"
        assert "input_schema" in defs[0]

    def test_custom_skills(self):
        agent = Agent(name="reviewer", skills=["code-review"])
        assert agent.active_skills == {"code-review"}

    def test_default_skills_all_active(self):
        agent = Agent(name="all_skills")
        from src.skill_loader import SKILL_LOADER
        assert agent.active_skills == set(SKILL_LOADER._all_skills.keys())

    def test_no_skills(self):
        agent = Agent(name="no_skills", skills=[])
        assert agent.active_skills == set()

    def test_permission_profile(self):
        agent = Agent(name="strict_agent", permission_profile="strict")
        assert agent.permission_manager.profile == "strict"

    def test_default_permission_profile(self):
        agent = Agent(name="default_perm")
        assert agent.permission_manager.profile == "standard"


class TestAgentDynamicTools:
    def test_add_tool(self):
        agent = Agent(name="test", tools=["read_file"])
        result = agent.add_tool("write_file")
        assert "added" in result
        assert "write_file" in agent.active_tools

    def test_add_unknown_tool(self):
        agent = Agent(name="test", tools=["read_file"])
        result = agent.add_tool("nonexistent")
        assert "Unknown" in result

    def test_add_duplicate_tool(self):
        agent = Agent(name="test", tools=["read_file"])
        result = agent.add_tool("read_file")
        assert "already registered" in result

    def test_remove_tool(self):
        agent = Agent(name="test", tools=["read_file", "write_file"])
        result = agent.remove_tool("read_file")
        assert "removed" in result
        assert "read_file" not in agent.active_tools
        assert "write_file" in agent.active_tools

    def test_remove_nonexistent_tool(self):
        agent = Agent(name="test", tools=["read_file"])
        result = agent.remove_tool("nonexistent")
        assert "not found" in result


class TestAgentDynamicSkills:
    def test_load_skill(self):
        agent = Agent(name="test", skills=[])
        result = agent.load_skill("code-review")
        assert "activated" in result
        assert "code-review" in agent.active_skills

    def test_load_unknown_skill(self):
        agent = Agent(name="test", skills=[])
        result = agent.load_skill("nonexistent-skill")
        assert "Unknown" in result

    def test_unload_skill(self):
        agent = Agent(name="test", skills=["code-review"])
        result = agent.unload_skill("code-review")
        assert "deactivated" in result
        assert "code-review" not in agent.active_skills

    def test_unload_nonexistent_skill(self):
        agent = Agent(name="test", skills=["code-review"])
        result = agent.unload_skill("nonexistent")
        assert "deactivated" in result  # idempotent

    def test_system_prompt_reflects_active_skills(self):
        agent = Agent(name="test", skills=["code-review"])
        prompt = agent._build_system_prompt()
        assert "code-review" in prompt
        agent.unload_skill("code-review")
        prompt = agent._build_system_prompt()
        assert "code-review" not in prompt


class TestAgentIsolation:
    def test_two_agents_dont_share_tools(self):
        a = Agent(name="a", tools=["read_file"])
        b = Agent(name="b", tools=["write_file"])
        assert a.active_tools == ["read_file"]
        assert b.active_tools == ["write_file"]

    def test_add_tool_doesnt_affect_other_agent(self):
        a = Agent(name="a", tools=["read_file"])
        b = Agent(name="b", tools=["read_file"])
        a.add_tool("write_file")
        assert "write_file" in a.active_tools
        assert "write_file" not in b.active_tools

    def test_remove_tool_doesnt_affect_other_agent(self):
        a = Agent(name="a", tools=["read_file", "write_file"])
        b = Agent(name="b", tools=["read_file", "write_file"])
        a.remove_tool("write_file")
        assert "write_file" not in a.active_tools
        assert "write_file" in b.active_tools

    def test_permission_profiles_independent(self):
        a = Agent(name="a", permission_profile="strict")
        b = Agent(name="b", permission_profile="permissive")
        assert a.permission_manager.profile == "strict"
        assert b.permission_manager.profile == "permissive"

    def test_skill_activation_independent(self):
        a = Agent(name="a", skills=["code-review"])
        b = Agent(name="b", skills=["pdf"])
        assert a.active_skills == {"code-review"}
        assert b.active_skills == {"pdf"}
        a.load_skill("pdf")
        assert "pdf" in a.active_skills
        assert b.active_skills == {"pdf"}

    def test_dispatcher_is_different_instance(self):
        a = Agent(name="a")
        b = Agent(name="b")
        assert a.dispatcher is not b.dispatcher


class TestAgentPermissions:
    def test_strict_agent_denies_command(self):
        agent = Agent(name="strict", permission_profile="strict")
        result = agent.permission_manager.check("run_command", {"command": "custom_cmd"})
        assert result.level == PermissionLevel.DENY

    def test_permissive_agent_allows_write(self):
        agent = Agent(name="permissive", permission_profile="permissive")
        result = agent.permission_manager.check("write_file", {"path": "test.txt", "content": "hi"})
        assert result.level == PermissionLevel.ALLOW

    def test_dangerous_command_denied_regardless(self):
        agent = Agent(name="permissive", permission_profile="permissive")
        result = agent.permission_manager.check("run_command", {"command": "rm -rf /"})
        assert result.level == PermissionLevel.DENY


class TestAgentCustomSystemPrompt:
    def test_custom_prompt(self):
        agent = Agent(name="custom", system_prompt="You are a chef.")
        assert agent._build_system_prompt() == "You are a chef."

    def test_default_prompt_includes_workspace(self):
        agent = Agent(name="default")
        prompt = agent._build_system_prompt()
        assert "coding assistant" in prompt
        assert "Skills available" in prompt
