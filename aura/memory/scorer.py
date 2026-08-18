from datetime import UTC, datetime
import re

from aura.memory.models import MemoryRecord


class MemoryScorer:
    """
    Scores memories based on:

    1. Lexical similarity
    2. Importance
    3. Recency
    4. Access frequency

    The final score is normalized between 0.0 and 1.0.
    """

    def __init__(
        self,
        similarity_weight: float = 0.55,
        importance_weight: float = 0.20,
        recency_weight: float = 0.15,
        access_weight: float = 0.10,
    ):
        self.similarity_weight = similarity_weight
        self.importance_weight = importance_weight
        self.recency_weight = recency_weight
        self.access_weight = access_weight

    def score(
        self,
        query: str,
        memory: MemoryRecord,
    ) -> float:
        similarity = self.lexical_similarity(
            query,
            memory.content,
        )

        importance = self._normalize_importance(
            memory.importance
        )

        recency = self._recency_score(
            memory
        )

        access_frequency = self._access_score(
            memory.access_count
        )

        final_score = (
            similarity * self.similarity_weight
            + importance * self.importance_weight
            + recency * self.recency_weight
            + access_frequency * self.access_weight
        )

        return max(
            0.0,
            min(1.0, final_score),
        )

    def rank(
        self,
        query: str,
        memories: list[MemoryRecord],
    ) -> list[tuple[MemoryRecord, float]]:
        scored_memories = [
            (
                memory,
                self.score(
                    query=query,
                    memory=memory,
                ),
            )
            for memory in memories
        ]

        scored_memories.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scored_memories

    def lexical_similarity(
        self,
        query: str,
        content: str,
    ) -> float:
        query_tokens = self._tokenize(
            query
        )

        content_tokens = self._tokenize(
            content
        )

        if not query_tokens:
            return 0.0

        if not content_tokens:
            return 0.0

        matching_tokens = (
            query_tokens
            & content_tokens
        )

        similarity = (
            len(matching_tokens)
            / len(query_tokens)
        )

        return max(
            0.0,
            min(1.0, similarity),
        )

    def _tokenize(
        self,
        text: str,
    ) -> set[str]:
        words = re.findall(
            r"[a-zA-Z0-9]+",
            text.lower(),
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
        }

        return {
            word
            for word in words
            if word not in stop_words
        }

    def _normalize_importance(
        self,
        importance: float,
    ) -> float:
        return max(
            0.0,
            min(1.0, importance),
        )

    def _recency_score(
        self,
        memory: MemoryRecord,
    ) -> float:
        now = datetime.now(UTC)

        created_at = memory.created_at

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=UTC
            )

        age = now - created_at

        age_days = max(
            0.0,
            age.total_seconds() / 86400,
        )

        # New memories receive the highest score.
        # The score gradually decreases with age.
        recency = 1.0 / (
            1.0 + age_days
        )

        return max(
            0.0,
            min(1.0, recency),
        )

    def _access_score(
        self,
        access_count: int,
    ) -> float:
        if access_count <= 0:
            return 0.0

        # Gradually approaches 1 as a memory
        # is accessed more frequently.
        access_score = (
            access_count
            / (access_count + 5)
        )

        return max(
            0.0,
            min(1.0, access_score),
        )