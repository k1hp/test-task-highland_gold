from typing import List
import sqlite3

from src.core.config import LOGGER
from src.core.schemas import HoleSchema, AssaySchema


class SQLiteDataManager:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        LOGGER.info("db_path", db_path)

    def save_import_data(
        self, holes: List[HoleSchema], assays: List[AssaySchema]
    ) -> None:
        with self.connection:
            self._save_holes(holes)
            self._save_assays(assays)

    def _save_holes(self, holes: List[HoleSchema]) -> None:
        cursor = self.connection.cursor()
        sql_insert = "INSERT INTO holes (name, x, y, z, lenght, _level, issue_date) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cursor.executemany(
            sql_insert,
            (tuple(hole.model_dump(by_alias=True).values()) for hole in holes),
        )

    def _save_assays(self, assays: List[AssaySchema]) -> None:
        cursor = self.connection.cursor()

        for assay in assays:
            cursor.execute("SELECT id FROM holes WHERE name = ?", (assay.name,))
            row = cursor.fetchone()

            if row is None:
                LOGGER.warning(
                    f"Предупреждение: скважина '{assay.name}' не найдена, пропускаем assay"
                )
                continue

            hole_id = row[0]
            without_name = assay.model_dump(by_alias=True)
            without_name.pop("name")

            cursor.execute(
                "INSERT INTO assay (hole_id, _from, _to, Au) VALUES (?, ?, ?, ?)",
                (hole_id, *(without_name.values())),
            )

    def get_all_holes(self) -> List[dict]:
        """Для таблицы просмотра скважин"""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT DISTINCT 
                h.name as "Имя скважины",
                a._from as "ОТ",
                a._to as "ДО", 
                a.Au as "Au"
            FROM holes h
            INNER JOIN assay AS a ON h.id = a.hole_id
            ORDER BY h.name
        """
        )

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
