import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from aura.memory.models import MemoryRecord, MemoryType


class MemoryRepository:
    def __init__(
        self,
        database_path: str = "data/aura_memory.db",
    ):
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    access_count INTEGER NOT NULL,
                    last_accessed_at TEXT,
                    metadata TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def save(
        self,
        memory: MemoryRecord,
    ) -> MemoryRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO memories (
                    id,
                    memory_type,
                    content,
                    importance,
                    created_at,
                    updated_at,
                    access_count,
                    last_accessed_at,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.id,
                    memory.memory_type.value,
                    memory.content,
                    memory.importance,
                    memory.created_at.isoformat(),
                    memory.updated_at.isoformat(),
                    memory.access_count,
                    (
                        memory.last_accessed_at.isoformat()
                        if memory.last_accessed_at
                        else None
                    ),
                    json.dumps(
                        memory.metadata
                    ),
                ),
            )

            connection.commit()

        return memory

    def get_by_id(
        self,
        memory_id: str,
    ) -> MemoryRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_memory(
            row
        )

    def find_exact(
        self,
        content: str,
        memory_type: MemoryType | None = None,
    ) -> MemoryRecord | None:
        normalized_content = (
            content.strip().lower()
        )

        with self._connect() as connection:
            if memory_type is None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM memories
                    """
                ).fetchall()

            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM memories
                    WHERE memory_type = ?
                    """,
                    (
                        memory_type.value,
                    ),
                ).fetchall()

        for row in rows:
            memory = self._row_to_memory(
                row
            )

            if (
                memory.content
                .strip()
                .lower()
                == normalized_content
            ):
                return memory

        return None

    def list_all(
        self,
    ) -> list[MemoryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM memories
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [
            self._row_to_memory(
                row
            )
            for row in rows
        ]

    def list_by_type(
        self,
        memory_type: MemoryType,
    ) -> list[MemoryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM memories
                WHERE memory_type = ?
                ORDER BY created_at DESC
                """,
                (
                    memory_type.value,
                ),
            ).fetchall()

        return [
            self._row_to_memory(
                row
            )
            for row in rows
        ]

    def mark_accessed(
        self,
        memory_id: str,
    ) -> MemoryRecord | None:
        memory = self.get_by_id(
            memory_id
        )

        if memory is None:
            return None

        now = datetime.now(
            UTC
        )

        memory.access_count += 1
        memory.last_accessed_at = now
        memory.updated_at = now

        self.save(
            memory
        )

        return memory

    def delete(
        self,
        memory_id: str,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE id = ?
                """,
                (
                    memory_id,
                ),
            )

            connection.commit()

        return cursor.rowcount > 0

    def clear_all(
        self,
    ) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM memories
                """
            ).fetchone()

            count = int(
                row["total"]
            )

            connection.execute(
                """
                DELETE FROM memories
                """
            )

            connection.commit()

        return count

    def count(
        self,
    ) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM memories
                """
            ).fetchone()

        return int(
            row["total"]
        )

    def count_by_type(
        self,
    ) -> dict[str, int]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    memory_type,
                    COUNT(*) AS total
                FROM memories
                GROUP BY memory_type
                """
            ).fetchall()

        return {
            row["memory_type"]:
                int(row["total"])
            for row in rows
        }

    def most_accessed(
        self,
        limit: int = 5,
    ) -> list[MemoryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM memories
                ORDER BY
                    access_count DESC,
                    updated_at DESC
                LIMIT ?
                """,
                (
                    limit,
                ),
            ).fetchall()

        return [
            self._row_to_memory(
                row
            )
            for row in rows
        ]

    def oldest(
        self,
        limit: int = 5,
    ) -> list[MemoryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM memories
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (
                    limit,
                ),
            ).fetchall()

        return [
            self._row_to_memory(
                row
            )
            for row in rows
        ]

    def _row_to_memory(
        self,
        row: sqlite3.Row,
    ) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            memory_type=MemoryType(
                row["memory_type"]
            ),
            content=row["content"],
            importance=row["importance"],
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                row["updated_at"]
            ),
            access_count=row[
                "access_count"
            ],
            last_accessed_at=(
                datetime.fromisoformat(
                    row[
                        "last_accessed_at"
                    ]
                )
                if row[
                    "last_accessed_at"
                ]
                else None
            ),
            metadata=json.loads(
                row["metadata"]
            ),
        )