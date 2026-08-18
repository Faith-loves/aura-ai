import json
import re
from datetime import UTC, datetime
from pathlib import Path

from aura.core.logger import logger
from aura.memory.formatter import MemoryFormatter
from aura.memory.models import MemoryRecord, MemoryType
from aura.memory.repository import MemoryRepository
from aura.memory.scorer import MemoryScorer


class MemoryManager:
    def __init__(
        self,
        repository: MemoryRepository,
        scorer: MemoryScorer | None = None,
        formatter: MemoryFormatter | None = None,
    ):
        self.repository = repository
        self.scorer = scorer or MemoryScorer()
        self.formatter = formatter or MemoryFormatter()

    def remember(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        metadata: dict | None = None,
    ) -> MemoryRecord:
        cleaned_content = content.strip()

        existing = self.repository.find_exact(
            content=cleaned_content,
            memory_type=memory_type,
        )

        if existing is None:
            existing = self.find_near_duplicate(
                content=cleaned_content,
                memory_type=memory_type,
            )

        if existing is not None:
            return self._merge_memory(
                existing=existing,
                importance=importance,
                metadata=metadata,
            )

        conflicting = self.find_conflicting_memory(
            content=cleaned_content,
            memory_type=memory_type,
        )

        if conflicting is not None:
            return self._replace_conflicting_memory(
                existing=conflicting,
                new_content=cleaned_content,
                importance=importance,
                metadata=metadata,
            )

        memory = MemoryRecord(
            memory_type=memory_type,
            content=cleaned_content,
            importance=importance,
            metadata=metadata or {},
        )

        saved_memory = self.repository.save(memory)

        logger.info(
            "Saved memory | id=%s | type=%s",
            saved_memory.id,
            saved_memory.memory_type.value,
        )

        return saved_memory

    def _merge_memory(
        self,
        existing: MemoryRecord,
        importance: float,
        metadata: dict | None,
    ) -> MemoryRecord:
        existing.importance = max(
            existing.importance,
            importance,
        )

        existing.updated_at = datetime.now(UTC)

        if metadata:
            existing.metadata.update(metadata)

        saved_memory = self.repository.save(existing)

        logger.info(
            "Updated duplicate memory | id=%s | type=%s",
            saved_memory.id,
            saved_memory.memory_type.value,
        )

        return saved_memory

    def _replace_conflicting_memory(
        self,
        existing: MemoryRecord,
        new_content: str,
        importance: float,
        metadata: dict | None,
    ) -> MemoryRecord:
        previous_content = existing.content

        existing.content = new_content
        existing.importance = max(
            existing.importance,
            importance,
        )
        existing.updated_at = datetime.now(UTC)

        existing.metadata["previous_content"] = previous_content
        existing.metadata["updated"] = True
        existing.metadata["updated_at"] = (
            existing.updated_at.isoformat()
        )

        if metadata:
            existing.metadata.update(metadata)

        saved_memory = self.repository.save(existing)

        logger.info(
            "Updated conflicting memory | id=%s | type=%s",
            saved_memory.id,
            saved_memory.memory_type.value,
        )

        return saved_memory

    def find_near_duplicate(
        self,
        content: str,
        memory_type: MemoryType,
        threshold: float = 0.75,
    ) -> MemoryRecord | None:
        memories = self.repository.list_by_type(
            memory_type
        )

        best_match = None
        best_score = 0.0

        for memory in memories:
            similarity = self._content_similarity(
                content,
                memory.content,
            )

            if (
                similarity >= threshold
                and similarity > best_score
            ):
                best_match = memory
                best_score = similarity

        return best_match

    def find_conflicting_memory(
        self,
        content: str,
        memory_type: MemoryType,
    ) -> MemoryRecord | None:
        if memory_type not in {
            MemoryType.FACT,
            MemoryType.PREFERENCE,
            MemoryType.PROJECT,
            MemoryType.TASK,
        }:
            return None

        new_subject = self._extract_memory_subject(
            content
        )

        if not new_subject:
            return None

        memories = self.repository.list_by_type(
            memory_type
        )

        for memory in memories:
            existing_subject = self._extract_memory_subject(
                memory.content
            )

            if not existing_subject:
                continue

            if new_subject == existing_subject:
                similarity = self._content_similarity(
                    content,
                    memory.content,
                )

                if similarity < 0.75:
                    return memory

        return None

    def _extract_memory_subject(
        self,
        content: str,
    ) -> str | None:
        text = content.lower().strip()

        patterns = [
            r"my project (?:now )?(?:uses|is|runs on)\s+",
            r"my preferred (?:language|framework|tool) is\s+",
            r"i prefer\s+",
            r"my name is\s+",
            r"i work at\s+",
            r"i study at\s+",
            r"my task is\s+",
            r"i need to\s+",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
            )

            if match:
                prefix = match.group(0).strip()

                return prefix.replace(
                    "now ",
                    "",
                )

        return None

    def _content_similarity(
        self,
        first: str,
        second: str,
    ) -> float:
        first_tokens = self._normalize_tokens(first)
        second_tokens = self._normalize_tokens(second)

        if not first_tokens or not second_tokens:
            return 0.0

        intersection = (
            first_tokens
            & second_tokens
        )

        union = (
            first_tokens
            | second_tokens
        )

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _normalize_tokens(
        self,
        content: str,
    ) -> set[str]:
        words = re.findall(
            r"[a-zA-Z0-9]+",
            content.lower(),
        )

        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "my",
            "our",
            "i",
            "me",
            "we",
            "to",
            "of",
            "for",
            "in",
            "on",
            "at",
            "and",
            "or",
            "that",
            "this",
            "it",
            "now",
        }

        return {
            word
            for word in words
            if word not in stop_words
        }

    def recall(
        self,
        memory_id: str,
        mark_accessed: bool = True,
    ) -> MemoryRecord | None:
        memory = self.repository.get_by_id(
            memory_id
        )

        if memory is None:
            return None

        if mark_accessed:
            memory = self.repository.mark_accessed(
                memory_id
            )

        return memory

    def search(
        self,
        query: str,
        limit: int = 5,
        memory_type: MemoryType | None = None,
        mark_accessed: bool = True,
    ) -> list[tuple[MemoryRecord, float]]:
        if limit <= 0:
            return []

        if memory_type is None:
            memories = self.repository.list_all()
        else:
            memories = self.repository.list_by_type(
                memory_type
            )

        if not memories:
            return []

        ranked = self.scorer.rank(
            query=query,
            memories=memories,
        )

        top_results = ranked[:limit]

        if mark_accessed:
            updated_results = []

            for memory, score in top_results:
                updated_memory = (
                    self.repository.mark_accessed(
                        memory.id
                    )
                )

                if updated_memory is not None:
                    updated_results.append(
                        (
                            updated_memory,
                            score,
                        )
                    )

            top_results = updated_results

        return top_results

    def build_context(
        self,
        query: str,
        limit: int = 5,
        memory_type: MemoryType | None = None,
        mark_accessed: bool = True,
    ) -> str:
        memories = self.search(
            query=query,
            limit=limit,
            memory_type=memory_type,
            mark_accessed=mark_accessed,
        )

        return self.formatter.format_for_prompt(
            memories
        )

    def list_memories(
        self,
        memory_type: MemoryType | None = None,
    ) -> list[MemoryRecord]:
        if memory_type is None:
            return self.repository.list_all()

        return self.repository.list_by_type(
            memory_type
        )

    def forget(
        self,
        memory_id: str,
    ) -> bool:
        return self.repository.delete(
            memory_id
        )

    def count(self) -> int:
        return self.repository.count()

    def clear_all_memories(self) -> int:
        deleted = self.repository.clear_all()

        logger.warning(
            "All memories cleared | deleted=%s",
            deleted,
        )

        return deleted

    def get_statistics(self) -> dict:
        memories = self.repository.list_all()

        average_importance = (
            sum(
                memory.importance
                for memory in memories
            )
            / len(memories)
            if memories
            else 0.0
        )

        return {
            "total": self.repository.count(),
            "by_type": self.repository.count_by_type(),
            "most_accessed": [
                {
                    "id": memory.id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "access_count": memory.access_count,
                }
                for memory in self.repository.most_accessed(
                    limit=5
                )
            ],
            "oldest": [
                {
                    "id": memory.id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "created_at": memory.created_at.isoformat(),
                }
                for memory in self.repository.oldest(
                    limit=5
                )
            ],
            "average_importance": average_importance,
        }

    def cleanup(
        self,
        min_importance: float = 0.3,
        max_access_count: int = 0,
        older_than_days: int = 30,
    ) -> int:
        now = datetime.now(UTC)

        deleted_count = 0

        for memory in self.repository.list_all():
            created_at = memory.created_at

            if created_at.tzinfo is None:
                created_at = created_at.replace(
                    tzinfo=UTC
                )

            age_days = (
                now - created_at
            ).total_seconds() / 86400

            should_delete = (
                memory.importance <= min_importance
                and memory.access_count <= max_access_count
                and age_days >= older_than_days
            )

            if should_delete:
                if self.repository.delete(
                    memory.id
                ):
                    deleted_count += 1

        return deleted_count

    def cleanup_contaminated_memories(self) -> int:
        contamination_markers = {
            "relevant memory context:",
            "current user request:",
            "memory 1\n",
            "use the relevant memory context only when it helps",
        }

        deleted_count = 0

        for memory in self.repository.list_all():
            text = memory.content.lower()

            contaminated = any(
                marker in text
                for marker in contamination_markers
            )

            if contaminated:
                if self.repository.delete(
                    memory.id
                ):
                    deleted_count += 1

        return deleted_count

    def export_memories(self) -> dict:
        memories = self.repository.list_all()

        return {
            "version": 1,
            "exported_at": datetime.now(
                UTC
            ).isoformat(),
            "count": len(memories),
            "memories": [
                {
                    "id": memory.id,
                    "memory_type":
                        memory.memory_type.value,
                    "content": memory.content,
                    "importance": memory.importance,
                    "created_at":
                        memory.created_at.isoformat(),
                    "updated_at":
                        memory.updated_at.isoformat(),
                    "access_count":
                        memory.access_count,
                    "last_accessed_at": (
                        memory.last_accessed_at.isoformat()
                        if memory.last_accessed_at
                        else None
                    ),
                    "metadata": memory.metadata,
                }
                for memory in memories
            ],
        }

    def export_to_file(
        self,
        file_path: str,
    ) -> Path:
        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = self.export_memories()

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path

    def import_memories(
        self,
        data: dict,
    ) -> int:
        raw_memories = data.get(
            "memories",
            []
        )

        imported_count = 0

        for item in raw_memories:
            memory = MemoryRecord(
                id=item["id"],
                memory_type=MemoryType(
                    item["memory_type"]
                ),
                content=item["content"],
                importance=item.get(
                    "importance",
                    0.5,
                ),
                created_at=datetime.fromisoformat(
                    item["created_at"]
                ),
                updated_at=datetime.fromisoformat(
                    item["updated_at"]
                ),
                access_count=item.get(
                    "access_count",
                    0,
                ),
                last_accessed_at=(
                    datetime.fromisoformat(
                        item["last_accessed_at"]
                    )
                    if item.get(
                        "last_accessed_at"
                    )
                    else None
                ),
                metadata=item.get(
                    "metadata",
                    {},
                ),
            )

            self.repository.save(memory)

            imported_count += 1

        return imported_count

    def import_from_file(
        self,
        file_path: str,
    ) -> int:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Memory backup not found: {path}"
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return self.import_memories(
            data
        )

    def create_backup(
        self,
        backup_directory: str = "backups",
    ) -> Path:
        timestamp = datetime.now(
            UTC
        ).strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_path = (
            Path(backup_directory)
            / f"aura_memory_{timestamp}.json"
        )

        return self.export_to_file(
            str(backup_path)
        )

    def restore_from_file(
        self,
        file_path: str,
        clear_existing: bool = True,
    ) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Memory backup not found: {path}"
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        previous_count = self.count()

        cleared = 0

        if clear_existing:
            cleared = self.clear_all_memories()

        imported = self.import_memories(
            data
        )

        return {
            "previous_count": previous_count,
            "cleared": cleared,
            "imported": imported,
            "current_count": self.count(),
        }