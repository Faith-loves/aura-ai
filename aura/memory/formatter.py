from aura.memory.models import MemoryRecord


class MemoryFormatter:
    def format_memory(
        self,
        memory: MemoryRecord,
        score: float | None = None,
    ) -> str:
        parts = [
            f"Type: {memory.memory_type.value}",
            f"Content: {memory.content}",
            f"Importance: {memory.importance:.2f}",
        ]

        if score is not None:
            parts.append(
                f"Relevance: {score:.4f}"
            )

        if memory.metadata:
            metadata_text = ", ".join(
                f"{key}={value}"
                for key, value in memory.metadata.items()
            )

            parts.append(
                f"Metadata: {metadata_text}"
            )

        return "\n".join(parts)

    def format_ranked_memories(
        self,
        memories: list[
            tuple[MemoryRecord, float]
        ],
    ) -> str:
        if not memories:
            return ""

        formatted = []

        for index, (memory, score) in enumerate(
            memories,
            start=1,
        ):
            formatted.append(
                (
                    f"Memory {index}\n"
                    f"{self.format_memory(memory, score)}"
                )
            )

        return "\n\n".join(formatted)

    def format_for_prompt(
        self,
        memories: list[
            tuple[MemoryRecord, float]
        ],
    ) -> str:
        if not memories:
            return ""

        formatted_memories = (
            self.format_ranked_memories(
                memories
            )
        )

        return (
            "Relevant memory context:\n\n"
            f"{formatted_memories}"
        )