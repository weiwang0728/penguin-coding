"""Tests for skill_loader.py — SkillLoader."""

import pytest
from pathlib import Path

from src.skill_loader import SkillLoader


SKILLS_DIR = Path(__file__).resolve().parent.parent / "skill" / "skills"


class TestSkillLoader:
    def test_load_all_skills(self):
        loader = SkillLoader(SKILLS_DIR)
        assert len(loader._all_skills) > 0

    def test_activate_skill(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=[])
        if not loader._all_skills:
            pytest.skip("No skills found")
        name = list(loader._all_skills.keys())[0]
        result = loader.activate(name)
        assert "activated" in result
        assert name in loader.active_skills

    def test_activate_unknown_skill(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=[])
        result = loader.activate("nonexistent-skill-xyz")
        assert "Unknown skill" in result

    def test_deactivate_skill(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=[])
        if not loader._all_skills:
            pytest.skip("No skills found")
        name = list(loader._all_skills.keys())[0]
        loader.activate(name)
        result = loader.deactivate(name)
        assert "deactivated" in result
        assert name not in loader.active_skills

    def test_deactivate_nonexistent_skill(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=[])
        result = loader.deactivate("nonexistent")
        assert "deactivated" in result  # idempotent

    def test_get_content(self):
        loader = SkillLoader(SKILLS_DIR)
        if not loader._all_skills:
            pytest.skip("No skills found")
        name = list(loader._all_skills.keys())[0]
        content = loader.get_content(name)
        assert f'<skill name="{name}"' in content

    def test_get_content_unknown(self):
        loader = SkillLoader(SKILLS_DIR)
        result = loader.get_content("nonexistent-skill-xyz")
        assert "Unknown skill" in result

    def test_get_descriptions(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=None)
        desc = loader.get_descriptions()
        assert len(desc) > 0  # all skills active

    def test_get_descriptions_empty(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=[])
        desc = loader.get_descriptions()
        assert desc == "(no skills available)"

    def test_initial_skills_none_activates_all(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=None)
        assert loader.active_skills == set(loader._all_skills.keys())

    def test_initial_skills_empty(self):
        loader = SkillLoader(SKILLS_DIR, initial_skills=[])
        assert loader.active_skills == set()

    def test_nonexistent_skills_dir(self):
        loader = SkillLoader(Path("/nonexistent/path"))
        assert len(loader._all_skills) == 0
        assert loader.active_skills == set()
