"""Persistent memory system — loop-embedded, auto-extracting, threshold-consolidated.

Memory is NOT a tool the agent calls — it's infrastructure that wraps the
agent loop:
  1. Index always present in system prompt (build_system_index)
  2. Relevant memories injected per iteration (build_iteration_context)
  3. Memories auto-extracted after each turn (extract_from_turn)
  4. Consolidation triggered by thresholds (consolidate)
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("penguin")


# ── Enums ──

class MemoryType(str, Enum):
    USER = "user"
    PROJECT = "project"
    FEEDBACK = "feedback"
    REFERENCE = "reference"


class MemoryScope(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"


# ── Data model ──

@dataclass
class Memory:
    id: str
    type: str
    scope: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    relevance: int = 5
    access_count: int = 0
    last_accessed: str = ""


# ── Index ──

class MemoryIndex:
    """In-memory index backed by index.json on disk."""

    def __init__(self, path: Path):
        self.path = path
        self.entries: list[dict] = []
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self.entries = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.entries = []
        else:
            self.entries = []

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, memory: Memory):
        self.entries.append({
            "id": memory.id,
            "type": memory.type,
            "scope": memory.scope,
            "title": memory.title,
            "tags": memory.tags,
            "relevance": memory.relevance,
            "updated_at": memory.updated_at,
        })
        self.save()

    def remove(self, memory_id: str):
        self.entries = [e for e in self.entries if e["id"] != memory_id]
        self.save()

    def update(self, memory: Memory):
        for i, e in enumerate(self.entries):
            if e["id"] == memory.id:
                self.entries[i] = {
                    "id": memory.id,
                    "type": memory.type,
                    "scope": memory.scope,
                    "title": memory.title,
                    "tags": memory.tags,
                    "relevance": memory.relevance,
                    "updated_at": memory.updated_at,
                }
                break
        self.save()

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            e for e in self.entries
            if q in e.get("title", "").lower()
            or any(q in t.lower() for t in e.get("tags", []))
        ]


# ── Core store ──

class MemoryStore:
    MEMORY_BUDGET_TOKENS = 2000
    INDEX_BUDGET_TOKENS = 300
    CONSOLIDATE_THRESHOLD = 50
    DECAY_DAYS = 30

    GLOBAL_DIR = Path.home() / ".penguin_memory"

    def __init__(self, project_dir: Path | None = None):
        self.global_dir = self.GLOBAL_DIR
        self.global_dir.mkdir(parents=True, exist_ok=True)
        (self.global_dir / "memories").mkdir(exist_ok=True)

        self.project_dir = project_dir
        if project_dir:
            self.project_mem_dir = project_dir / ".penguin_memory"
            self.project_mem_dir.mkdir(parents=True, exist_ok=True)
            (self.project_mem_dir / "memories").mkdir(exist_ok=True)
        else:
            self.project_mem_dir = None

        self._global_index = MemoryIndex(self.global_dir / "index.json")
        self._project_index = (
            MemoryIndex(self.project_mem_dir / "index.json")
            if self.project_mem_dir
            else None
        )

        self._global_next_id = self._max_id(self.global_dir / "memories", "global") + 1
        self._project_next_id = (
            self._max_id(self.project_mem_dir / "memories", "project") + 1
            if self.project_mem_dir else 1
        )

    # ── Helpers ──

    @staticmethod
    def _max_id(memories_dir: Path, prefix: str) -> int:
        if not memories_dir.exists():
            return 0
        ids = []
        for f in memories_dir.glob(f"{prefix}_*.json"):
            try:
                ids.append(int(f.stem.split("_")[1]))
            except (ValueError, IndexError):
                pass
        return max(ids) if ids else 0

    def _dir_for_scope(self, scope: str) -> Path:
        if scope == MemoryScope.GLOBAL:
            return self.global_dir / "memories"
        if not self.project_mem_dir:
            raise ValueError("No project directory configured")
        return self.project_mem_dir / "memories"

    def _index_for_scope(self, scope: str) -> MemoryIndex:
        if scope == MemoryScope.GLOBAL:
            return self._global_index
        if not self._project_index:
            raise ValueError("No project directory configured")
        return self._project_index

    def _next_id_for_scope(self, scope: str) -> int:
        if scope == MemoryScope.GLOBAL:
            val = self._global_next_id
            self._global_next_id += 1
            return val
        val = self._project_next_id
        self._project_next_id += 1
        return val

    def _load(self, memory_id: str, scope: str) -> Memory:
        path = self._dir_for_scope(scope) / f"{memory_id}.json"
        if not path.exists():
            raise ValueError(f"Memory {memory_id} not found in {scope} scope")
        data = json.loads(path.read_text(encoding="utf-8"))
        return Memory(**data)

    def _save(self, memory: Memory):
        path = self._dir_for_scope(memory.scope) / f"{memory.id}.json"
        path.write_text(
            json.dumps(asdict(memory), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def count(self) -> int:
        total = len(self._global_index.entries)
        if self._project_index:
            total += len(self._project_index.entries)
        return total

    # ── CRUD ──

    def save(
        self,
        title: str,
        content: str,
        memory_type: str = MemoryType.PROJECT,
        scope: str = MemoryScope.PROJECT,
        tags: list[str] | None = None,
        relevance: int = 5,
    ) -> str:
        if scope == MemoryScope.PROJECT and not self.project_mem_dir:
            return "Error: No project directory configured for project-scope memories"
        if memory_type not in [t.value for t in MemoryType]:
            return f"Error: Invalid memory type '{memory_type}'. Valid: {[t.value for t in MemoryType]}"
        if scope not in [s.value for s in MemoryScope]:
            return f"Error: Invalid scope '{scope}'. Valid: {[s.value for s in MemoryScope]}"

        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        num = self._next_id_for_scope(scope)
        memory_id = f"{scope}_{num:03d}"

        memory = Memory(
            id=memory_id,
            type=memory_type,
            scope=scope,
            title=title,
            content=content,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            relevance=max(1, min(10, relevance)),
            access_count=0,
            last_accessed=now,
        )
        self._save(memory)
        self._index_for_scope(scope).add(memory)
        return f"Memory saved: [{memory_id}] ({memory_type}/{scope}) {title}"

    def recall(self, memory_id: str, scope: str | None = None) -> str:
        if scope:
            try:
                m = self._load(memory_id, scope)
                m.access_count += 1
                m.last_accessed = time.strftime("%Y-%m-%dT%H:%M:%S")
                self._save(m)
                self._index_for_scope(scope).update(m)
                return self._render_memory(m)
            except ValueError as e:
                return f"Error: {e}"

        for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            if s == MemoryScope.PROJECT and not self.project_mem_dir:
                continue
            path = self._dir_for_scope(s) / f"{memory_id}.json"
            if path.exists():
                m = self._load(memory_id, s)
                m.access_count += 1
                m.last_accessed = time.strftime("%Y-%m-%dT%H:%M:%S")
                self._save(m)
                self._index_for_scope(s).update(m)
                return self._render_memory(m)
        return f"Error: Memory '{memory_id}' not found"

    def search(self, query: str, scope: str | None = None) -> str:
        results = []
        scopes_to_search = (
            [scope] if scope
            else [s for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]
                  if s == MemoryScope.GLOBAL or self.project_mem_dir]
        )
        for s in scopes_to_search:
            try:
                index = self._index_for_scope(s)
            except ValueError:
                continue
            matches = index.search(query)
            for entry in matches:
                path = self._dir_for_scope(s) / f"{entry['id']}.json"
                if path.exists():
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if query.lower() in data.get("content", "").lower():
                        results.append(entry)
                        continue
                results.append(entry)

        if not results:
            return f"No memories matching '{query}'."

        lines = [f"Found {len(results)} matching:"]
        for r in sorted(results, key=lambda x: x.get("relevance", 5), reverse=True):
            tags_str = f" [{', '.join(r['tags'])}]" if r.get("tags") else ""
            lines.append(
                f"  [{r['id']}] ({r['type']}/{r.get('scope', '?')}) "
                f"{r['title']}{tags_str} (rel:{r.get('relevance', '?')})"
            )
        return "\n".join(lines)

    def list_memories(self, scope: str | None = None, memory_type: str | None = None) -> str:
        entries = []
        scopes_to_list = (
            [scope] if scope
            else [s for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]
                  if s == MemoryScope.GLOBAL or self.project_mem_dir]
        )
        for s in scopes_to_list:
            try:
                index = self._index_for_scope(s)
            except ValueError:
                continue
            for entry in index.entries:
                entry = dict(entry)
                entry["scope"] = s
                if memory_type and entry.get("type") != memory_type:
                    continue
                entries.append(entry)

        if not entries:
            return "No memories found."

        lines = []
        for e in sorted(entries, key=lambda x: (x.get("scope", ""), x.get("id", ""))):
            tags_str = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
            lines.append(
                f"  [{e['id']}] ({e['type']}/{e['scope']}) {e['title']}{tags_str}"
            )
        return "\n".join(lines)

    def delete(self, memory_id: str, scope: str | None = None) -> str:
        for s in ([scope] if scope else [MemoryScope.GLOBAL, MemoryScope.PROJECT]):
            if s == MemoryScope.PROJECT and not self.project_mem_dir:
                continue
            path = self._dir_for_scope(s) / f"{memory_id}.json"
            if path.exists():
                try:
                    m = self._load(memory_id, s)
                except ValueError:
                    m = None
                path.unlink()
                self._index_for_scope(s).remove(memory_id)
                title = m.title if m else memory_id
                return f"Memory deleted: [{memory_id}] ({title})"
        return f"Error: Memory '{memory_id}' not found"

    # ── System prompt: always-present index ──

    def build_system_index(self) -> str:
        """Render compact index for system prompt injection (~100-300 tokens)."""
        lines = ["## Memory Index"]
        for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            if s == MemoryScope.PROJECT and not self._project_index:
                continue
            index = self._index_for_scope(s)
            if not index.entries:
                continue
            lines.append(f"\n### {s.title()} Scope")
            for e in sorted(index.entries, key=lambda x: x.get("relevance", 0), reverse=True):
                tags_str = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
                lines.append(
                    f"- [{e['id']}] ({e['type']}) {e['title']}{tags_str} "
                    f"(rel:{e.get('relevance', '?')})"
                )
        if len(lines) == 1:
            lines.append("(no memories yet)")
        return "\n".join(lines)

    # ── Per-iteration: context injection ──

    def build_iteration_context(self, messages: list[dict], token_budget: int = 1700) -> str:
        """Match relevant memories to current conversation, return content within budget."""
        from .compact import estimate_tokens

        keywords = self._extract_keywords(messages[-6:])

        matched = []
        for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            if s == MemoryScope.PROJECT and not self._project_index:
                continue
            try:
                index = self._index_for_scope(s)
            except ValueError:
                continue
            for entry in index.entries:
                score = self._relevance_score(entry, keywords)
                if score > 0:
                    matched.append((entry, score, s))

        if not matched:
            return ""

        matched.sort(key=lambda x: (x[1], x[0].get("relevance", 0)), reverse=True)

        parts = []
        remaining = token_budget
        for entry, score, scope in matched:
            try:
                m = self._load(entry["id"], scope)
            except ValueError:
                continue
            text = self._render_memory_compact(m)
            tokens = estimate_tokens(text)
            if remaining - tokens < 0:
                break
            parts.append(text)
            remaining -= tokens

        return "\n\n".join(parts) if parts else ""

    # ── Per-iteration: auto-extraction ──

    EXTRACT_SYSTEM_PROMPT = """Analyze this conversation turn. Identify information worth preserving as a memory for future sessions.

Focus on:
1. User preferences/corrections ("I prefer X", "Don't do Y") → type=feedback, relevance=8
2. Architecture decisions ("We decided to use X because...") → type=project, relevance=7
3. Project context discovered (key files, patterns, conventions) → type=project, relevance=6
4. External references (docs, URLs, dashboards) → type=reference, relevance=5

IGNORE:
- Task-specific context that won't be useful in future sessions
- Information already available in the codebase
- Routine tool calls and results
- Things the user said that are just instructions for the current task

Output a JSON array: [{"title": "...", "content": "...", "type": "user|project|feedback|reference", "tags": [...], "relevance": 1-10}]
If nothing is worth saving, output []."""

    def extract_from_turn(
        self,
        user_msg: dict,
        assistant_msg: dict,
        client: Any,
        model_id: str,
    ) -> list[str]:
        """Extract memory-worthy information from a conversation turn."""
        from .compact import estimate_tokens

        text = self._serialize_turn(user_msg, assistant_msg)
        if estimate_tokens(text) < 100:
            return []

        try:
            response = client.messages.create(
                model=model_id,
                max_tokens=800,
                system=self.EXTRACT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text[:6000]}],
            )
            result_text = "".join(
                b.text for b in response.content if b.type == "text"
            )
            candidates = json.loads(result_text)
            saved = []
            for c in candidates:
                if not isinstance(c, dict) or "title" not in c or "content" not in c:
                    continue
                if self._is_duplicate(c["title"], c["content"]):
                    continue
                result = self.save(
                    title=c["title"],
                    content=c["content"],
                    memory_type=c.get("type", "project"),
                    scope=MemoryScope.PROJECT,
                    tags=c.get("tags", []),
                    relevance=c.get("relevance", 5),
                )
                saved.append(result)
            return saved
        except Exception:
            logger.warning("Memory extraction from turn failed", exc_info=True)
            return []

    # ── Pre-compaction safety net ──

    PRESAVE_SYSTEM_PROMPT = """Analyze a conversation about to be compacted. Extract information that should be preserved as memories.

Focus on:
1. User preferences or corrections
2. Architecture decisions and their rationale
3. Important project context discovered during the conversation
4. Workarounds or validated approaches that were confirmed to work
5. External references or documentation links

Output a JSON array: [{"title": "...", "content": "...", "type": "user|project|feedback|reference", "tags": [...], "relevance": 1-10}]
If nothing is worth saving, output []."""

    def presave_from_compaction(
        self,
        messages: list[dict],
        client: Any,
        model_id: str,
    ) -> list[str]:
        """Save memory-worthy info before compaction discards conversation history."""
        from .compact import estimate_tokens, _serialize_messages

        text = _serialize_messages(messages)
        if estimate_tokens(text) < 200:
            return []

        try:
            response = client.messages.create(
                model=model_id,
                max_tokens=1000,
                system=self.PRESAVE_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": f"Analyze for memory-worthy information:\n\n{text[:8000]}"}
                ],
            )
            result_text = "".join(
                b.text for b in response.content if b.type == "text"
            )
            candidates = json.loads(result_text)
            saved = []
            for c in candidates:
                if not isinstance(c, dict) or "title" not in c or "content" not in c:
                    continue
                if self._is_duplicate(c["title"], c["content"]):
                    continue
                result = self.save(
                    title=c["title"],
                    content=c["content"],
                    memory_type=c.get("type", "project"),
                    scope=MemoryScope.PROJECT,
                    tags=c.get("tags", []),
                    relevance=c.get("relevance", 5),
                )
                saved.append(result)
            return saved
        except Exception:
            logger.warning("Memory presave from compaction failed", exc_info=True)
            return []

    # ── Consolidation ──

    def consolidate(self, client: Any, model_id: str) -> str:
        """Consolidate memories: decay, deduplicate, merge."""
        merged_count = 0
        decayed_count = 0
        deleted_count = 0

        # Phase 1: time decay
        now = datetime.now()
        for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            if s == MemoryScope.PROJECT and not self._project_index:
                continue
            for entry in list(self._index_for_scope(s).entries):
                try:
                    m = self._load(entry["id"], s)
                    last_str = m.last_accessed or m.updated_at
                    if not last_str:
                        continue
                    last = datetime.fromisoformat(last_str)
                    days_inactive = (now - last).days
                    if days_inactive > self.DECAY_DAYS:
                        m.relevance = max(0, m.relevance - 1)
                        if m.relevance <= 0:
                            self.delete(m.id, s)
                            deleted_count += 1
                        else:
                            self._save(m)
                            self._index_for_scope(s).update(m)
                            decayed_count += 1
                except Exception:
                    continue

        # Phase 2: deduplication by title/content similarity
        all_entries = []
        for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            if s == MemoryScope.PROJECT and not self._project_index:
                continue
            for e in self._index_for_scope(s).entries:
                all_entries.append((e, s))

        merged_ids: set[str] = set()
        for i, (e1, s1) in enumerate(all_entries):
            if e1["id"] in merged_ids:
                continue
            for j, (e2, s2) in enumerate(all_entries):
                if i >= j or e2["id"] in merged_ids:
                    continue
                if s1 != s2:
                    continue
                if self._similarity(e1, e2) > 0.7:
                    self._merge_memories(e1["id"], e2["id"], s1, client, model_id)
                    merged_ids.add(e2["id"])
                    merged_count += 1

        return (
            f"Consolidation complete: "
            f"{decayed_count} decayed, {deleted_count} deleted, "
            f"{merged_count} merged."
        )

    # ── Internal helpers ──

    @staticmethod
    def _render_memory(m: Memory) -> str:
        tags = ", ".join(m.tags) if m.tags else "none"
        return (
            f"## Memory: {m.title}\n"
            f"ID: {m.id} | Type: {m.type} | Scope: {m.scope} | Tags: {tags}\n"
            f"Relevance: {m.relevance} | Created: {m.created_at} | Updated: {m.updated_at}\n"
            f"Accessed: {m.access_count} times (last: {m.last_accessed})\n\n"
            f"{m.content}"
        )

    @staticmethod
    def _render_memory_compact(m: Memory) -> str:
        tags = ", ".join(m.tags) if m.tags else ""
        header = f"[{m.id}] ({m.type}) {m.title}"
        if tags:
            header += f" [{tags}]"
        return f"### {header}\n{m.content}"

    def _extract_keywords(self, messages: list[dict]) -> list[str]:
        """Extract simple keywords from recent messages for memory matching."""
        text_parts = []
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, str):
                text_parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))

        combined = " ".join(text_parts).lower()
        words = re.findall(r"[a-z_]{3,}", combined)
        stop = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
                "her", "was", "one", "our", "out", "has", "have", "this", "that", "with",
                "from", "they", "been", "said", "each", "which", "their", "will", "other",
                "about", "many", "then", "them", "these", "some", "would", "make", "like",
                "into", "time", "very", "when", "come", "could", "more", "over", "such",
                "after", "also", "just", "than", "what", "your", "know", "does", "only"}
        freq: dict[str, int] = {}
        for w in words:
            if w not in stop and len(w) >= 3:
                freq[w] = freq.get(w, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:20]]

    @staticmethod
    def _relevance_score(entry: dict, keywords: list[str]) -> float:
        """Score how relevant an index entry is to a set of keywords."""
        if not keywords:
            return 0.0
        title = entry.get("title", "").lower()
        tags = " ".join(entry.get("tags", [])).lower()
        combined = f"{title} {tags}"
        matches = sum(1 for kw in keywords if kw in combined)
        if matches == 0:
            return 0.0
        base = matches / len(keywords)
        relevance_boost = entry.get("relevance", 5) / 10.0
        return base + relevance_boost

    def _serialize_turn(self, user_msg: dict, assistant_msg: dict) -> str:
        """Serialize a single user+assistant turn for LLM analysis."""
        parts = []
        for label, msg in [("User", user_msg), ("Assistant", assistant_msg)]:
            content = msg.get("content")
            if isinstance(content, str):
                parts.append(f"[{label}]: {content}")
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        bt = block.get("type")
                        if bt == "text":
                            parts.append(f"[{label}]: {block.get('text', '')[:500]}")
                        elif bt == "tool_use":
                            name = block.get("name", "")
                            inp = json.dumps(block.get("input", {}), ensure_ascii=False)[:200]
                            parts.append(f"[{label}/tool_use]: {name}({inp})")
                        elif bt == "tool_result":
                            rc = block.get("content", "")
                            if isinstance(rc, str):
                                parts.append(f"[{label}/tool_result]: {rc[:300]}")
        return "\n\n".join(parts)

    def _is_duplicate(self, title: str, content: str) -> bool:
        """Check if a memory with similar title or content already exists."""
        t_lower = title.lower()
        c_lower = content.lower()[:200]
        for s in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            if s == MemoryScope.PROJECT and not self._project_index:
                continue
            try:
                index = self._index_for_scope(s)
            except ValueError:
                continue
            for entry in index.entries:
                if entry.get("title", "").lower() == t_lower:
                    return True
                # Simple content overlap check
                try:
                    m = self._load(entry["id"], s)
                    if m.content.lower()[:200] == c_lower:
                        return True
                except ValueError:
                    continue
        return False

    @staticmethod
    def _similarity(e1: dict, e2: dict) -> float:
        """Jaccard-like similarity between two index entries."""
        def _tokenize(text: str) -> set[str]:
            return set(re.findall(r"[a-z0-9_]{2,}", text.lower()))

        t1 = _tokenize(e1.get("title", ""))
        t2 = _tokenize(e2.get("title", ""))
        tags1 = _tokenize(" ".join(e1.get("tags", [])))
        tags2 = _tokenize(" ".join(e2.get("tags", [])))

        s1 = t1 | tags1
        s2 = t2 | tags2
        if not s1 or not s2:
            return 0.0
        return len(s1 & s2) / len(s1 | s2)

    def _merge_memories(
        self, keep_id: str, merge_id: str, scope: str,
        client: Any, model_id: str,
    ):
        """Merge two memories, keeping the one with higher relevance."""
        try:
            m1 = self._load(keep_id, scope)
            m2 = self._load(merge_id, scope)
        except ValueError:
            return

        # Keep the higher-relevance one, append content from the other
        if m2.relevance > m1.relevance:
            m1, m2 = m2, m1
            keep_id, merge_id = merge_id, keep_id

        # Try LLM merge for content
        try:
            response = client.messages.create(
                model=model_id,
                max_tokens=500,
                system="Merge these two similar memories into one concise memory. Preserve all key information.",
                messages=[{
                    "role": "user",
                    "content": f"Memory 1:\n{m1.content}\n\nMemory 2:\n{m2.content}"
                }],
            )
            merged_content = "".join(
                b.text for b in response.content if b.type == "text"
            )
            m1.content = merged_content
        except Exception:
            m1.content = f"{m1.content}\n\n[Also noted]: {m2.content}"

        m1.tags = list(set(m1.tags + m2.tags))
        m1.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._save(m1)
        self._index_for_scope(scope).update(m1)
        self.delete(merge_id, scope)


# ── Module-level singleton ──

from ._constants import ALLOWED_BASE_DIR

memory_store = MemoryStore(project_dir=Path(ALLOWED_BASE_DIR))
