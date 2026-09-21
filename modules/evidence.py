"""Evidence and notes storage for recon and report workflows."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class EvidenceStore:
    """Stores recon findings as structured evidence entries."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[1] / "r0uter_evidence.db")
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    task TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    next_steps TEXT NOT NULL,
                    raw_output TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def save_entry(
        self,
        target: str,
        task: str,
        summary: str,
        next_steps: list[str],
        raw_output: str,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO evidence (target, task, summary, next_steps, raw_output)
                VALUES (?, ?, ?, ?, ?)
                """,
                (target, task, summary, json.dumps(next_steps, ensure_ascii=False), raw_output),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list_entries(self, target: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        conditions = []
        parameters: list[Any] = []
        if target:
            conditions.append("target = ?")
            parameters.append(target)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        limit_clause = " LIMIT ?" if limit is not None else ""
        if limit is not None:
            parameters.append(max(0, int(limit)))

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                f"""
                SELECT id, target, task, summary, next_steps, raw_output, created_at
                FROM evidence
                {where_clause}
                ORDER BY id DESC
                {limit_clause}
                """,
                parameters,
            ).fetchall()

        return [self._row_to_entry(row) for row in rows]

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        """Return one evidence entry by database id, if it exists."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id, target, task, summary, next_steps, raw_output, created_at
                FROM evidence
                WHERE id = ?
                """,
                (entry_id,),
            ).fetchone()
        return self._row_to_entry(row) if row else None

    @staticmethod
    def _row_to_entry(row: tuple[Any, ...]) -> dict[str, Any]:
        entry_id, target, task, summary, next_steps, raw_output, created_at = row
        return {
            "id": entry_id,
            "target": target,
            "task": task,
            "summary": summary,
            "next_steps": json.loads(next_steps or "[]"),
            "raw_output": raw_output,
            "created_at": created_at,
        }
