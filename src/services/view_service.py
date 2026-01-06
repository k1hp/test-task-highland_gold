from typing import List

from src.app import db_manager
from src.core.db_manager import SQLiteDataManager


class ViewService:
    def __init__(self, db_manager: SQLiteDataManager):
        self.db_manager = db_manager

    def get_wells_for_display(self) -> List[dict]:
        return db_manager.get_all_holes()
