import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKDIR = PROJECT_ROOT / "workspace"
SKILLS_DIR = PROJECT_ROOT / "skill" / "skills"


class SkillLoader:
    def __init__(self, skills_dir: Path, initial_skills: list[str] | None = None):
        self.skills_dir = skills_dir
        self._all_skills: dict[str, dict] = {}
        self._active_skills: set[str] = set()
        self._load_all()
        # Activate specified skills (or all if None — backward compat)
        if initial_skills is not None:
            for name in initial_skills:
                if name in self._all_skills:
                    self._active_skills.add(name)
        else:
            self._active_skills = set(self._all_skills.keys())

    def _load_all(self):
        if not self.skills_dir.exists():
            return
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text()
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self._all_skills[name] = {"meta": meta, "body": body, "path": str(f)}

    def _parse_frontmatter(self, text: str) -> tuple[dict, str]:
        """Parse YAML frontmatter between --- delimiters."""
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        try:
            meta = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        return meta, match.group(2).strip()

    def activate(self, name: str) -> str:
        """Activate a skill for use in system prompt."""
        if name not in self._all_skills:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self._all_skills.keys())}"
        self._active_skills.add(name)
        return f"Skill '{name}' activated"

    def deactivate(self, name: str) -> str:
        """Deactivate a skill."""
        self._active_skills.discard(name)
        return f"Skill '{name}' deactivated"

    @property
    def active_skills(self) -> set[str]:
        return self._active_skills.copy()

    def get_descriptions(self) -> str:
        """Short descriptions of active skills for the system prompt."""
        if not self._active_skills:
            return "(no skills available)"
        lines = []
        for name in sorted(self._active_skills):
            skill = self._all_skills[name]
            desc = skill["meta"].get("description", "No description")
            tags = skill["meta"].get("tags", "")
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return "\n".join(lines)

    def get_content(self, name: str) -> str:
        """Full skill body returned in tool_result. Accessible regardless of active status."""
        skill = self._all_skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self._all_skills.keys())}"
        skill_dir = str(Path(skill['path']).parent)
        return f"<skill name=\"{name}\" dir=\"{skill_dir}\">\n{skill['body']}\n</skill>"


# Backward-compatible global instance — activates all skills by default
SKILL_LOADER = SkillLoader(SKILLS_DIR)
