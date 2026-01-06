from typing import Type, TypeVar, List
from pydantic import BaseModel

from src.core.db_manager import SQLiteDataManager
from src.core.excel_parser import ExcelParser
from src.core.schemas import AssaySchema, HoleSchema

T = TypeVar("T", bound=BaseModel)


class ImportService:
    SCHEMA_MAPPING = {
        "holes": HoleSchema,
        "assays": AssaySchema,
    }

    def __init__(self, parser: ExcelParser, db_manager: SQLiteDataManager):
        self.parser = parser
        self.db_manager = db_manager

    def import_data(self, file_path: str) -> None:
        raw_data = self._extract_data(file_path)

        validated_data = self._transform_and_validate(raw_data)

        self._load_data(validated_data)

    def _extract_data(self, file_path: str) -> dict:
        return self.parser.parse(file_path)

    def _transform_and_validate(self, data: dict) -> dict:
        return {
            key: self._validate_single_type(self.SCHEMA_MAPPING[key], value)
            for key, value in data.items()
        }

    def _validate_single_type(self, schema: Type[T], data_list: List[dict]) -> List[T]:
        return [schema(**data_object) for data_object in data_list]

    def _load_data(self, data: dict):
        self.db_manager.save_import_data(data["holes"], data["assays"])
