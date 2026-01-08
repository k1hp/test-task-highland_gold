import sys
from PyQt5.QtWidgets import QApplication

from src.core.db_manager import SQLiteDataManager
from src.core.excel_parser import ExcelParser
from src.services.import_service import ImportService
from src.services.view_service import ViewService
from src.ui.main_window import MainWindow
from src.core.config import DB_PATH, LOGGER


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")



    if not DB_PATH.exists():
        LOGGER.warning(f"Файл БД не найден: {DB_PATH}")
        LOGGER.info(f"Убедитесь, что база данных находится в {DB_PATH}")
        return

    # Создаем зависимости (Dependency Injection)
    try:
        db_manager = SQLiteDataManager(str(DB_PATH))
        parser = ExcelParser()
        import_service = ImportService(parser=parser, db_manager=db_manager)
        view_service = ViewService(db_manager=db_manager)

    except Exception as e:
        LOGGER.error(f"Ошибка инициализации сервисов: {e}")
        return

    # Создаем главное окно, передавая сервисы
    window = MainWindow(
        import_service=import_service,
        view_service=view_service
    )

    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())