import pathlib

from src.core.db_manager import SQLiteDataManager
from src.core.excel_parser import ExcelParser
from src.services.import_service import ImportService

BASE_DIR = pathlib.Path(__file__).parent.parent
DB_PATH = BASE_DIR / "task" / "database"

if __name__ == '__main__':
    db_manager = SQLiteDataManager(DB_PATH)
    parser = ExcelParser()
    service = ImportService(parser=parser, db_manager=db_manager)
    service.import_data(file_path="../task/journal.xlsx")
