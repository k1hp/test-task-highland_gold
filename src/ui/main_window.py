import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableView,
    QFileDialog, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QAbstractTableModel

from src.services.import_service import ImportService
from src.services.view_service import ViewService


class TableModel(QAbstractTableModel):
    """Модель для отображения данных в таблице"""

    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self._data[row].get(self._headers[col], "")
            return str(value) if value is not None else ""
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None


class MainWindow(QMainWindow):
    def __init__(self, import_service: ImportService, view_service: ViewService):
        super().__init__()

        self.import_service = import_service
        self.view_service = view_service
        self.current_file_path = ""

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("Импорт данных скважин")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)

        # 1. Секция выбора файла
        file_layout = QHBoxLayout()

        self.label_file = QLabel("Файл журнала:")
        self.line_edit_file = QLineEdit()
        self.line_edit_file.setReadOnly(True)
        self.line_edit_file.setPlaceholderText("Выберите файл Excel...")

        self.btn_select_file = QPushButton("Обзор")

        file_layout.addWidget(self.label_file)
        file_layout.addWidget(self.line_edit_file)
        file_layout.addWidget(self.btn_select_file)

        layout.addLayout(file_layout)

        # 2. Кнопка импорта
        self.btn_import = QPushButton("Импортировать в БД")
        self.btn_import.setMinimumHeight(30)
        layout.addWidget(self.btn_import)

        # 3. Кнопка просмотра данных
        self.btn_show_data = QPushButton("Показать данные из БД")
        self.btn_show_data.setMinimumHeight(30)
        layout.addWidget(self.btn_show_data)

        # 4. Таблица для отображения данных
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_view)

        self.btn_import.setEnabled(False)

    def setup_connections(self):
        self.btn_select_file.clicked.connect(self.select_file)
        self.btn_import.clicked.connect(self.import_data)
        self.btn_show_data.clicked.connect(self.show_data)
        self.line_edit_file.textChanged.connect(self.on_file_path_changed)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл журнала",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if file_path:
            self.current_file_path = file_path
            self.line_edit_file.setText(file_path)

    def on_file_path_changed(self, text):
        self.btn_import.setEnabled(bool(text.strip()))

    def import_data(self):
        if not self.current_file_path:
            self.show_message("Ошибка", "Файл не выбран", QMessageBox.Warning)
            return

        if not os.path.exists(self.current_file_path):
            self.show_message("Ошибка", f"Файл не существует:\n{self.current_file_path}", QMessageBox.Critical)
            return

        self.setCursor(Qt.WaitCursor)
        self.btn_import.setEnabled(False)

        try:
            self.import_service.import_data(self.current_file_path)
            self.show_message("Успех", "Данные успешно импортированы", QMessageBox.Information)

        except Exception as e:
            self.show_message("Ошибка импорта", f"Произошла ошибка:\n{str(e)}", QMessageBox.Critical)

        finally:
            self.setCursor(Qt.ArrowCursor)
            self.btn_import.setEnabled(True)

    def show_data(self):
        """Отображение таблицы скважин"""
        self.setCursor(Qt.WaitCursor)

        try:
            data = self.view_service.get_holes_for_display()

            headers = ["Имя скважины", "ОТ", "ДО", "Au"]

            model = TableModel(data, headers)
            self.table_view.setModel(model)

        except Exception as e:
            self.show_message("Ошибка загрузки", f"Не удалось загрузить данные:\n{str(e)}", QMessageBox.Critical)

        finally:
            self.setCursor(Qt.ArrowCursor)

    def show_message(self, title, message, icon_type):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_type)
        msg_box.exec_()