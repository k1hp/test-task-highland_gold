from typing import List

from src.core.config import LOGGER
from src.core.db_manager import SQLiteDataManager
from src.core.schemas import HoleDisplaySchema


class ViewService:
    def __init__(self, db_manager: SQLiteDataManager):
        self.db_manager = db_manager

    def get_holes_for_display(self) -> List[dict]:
        raw_data = self.db_manager.get_all_holes()
        validated_data = self._validate_display_data(raw_data)
        return validated_data

    def _validate_display_data(self, raw_data: List[dict]) -> List[dict]:
        validated = []
        for item in raw_data:
            try:
                HoleDisplaySchema.model_validate(item)
                validated.append(item)
            except Exception as e:
                LOGGER.warning(f"Invalid well data skipped: {item}, error: {e}")
        return validated