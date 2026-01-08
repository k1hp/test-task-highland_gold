import sqlite3

import pytest

from src.core.config import BASE_DIR
from src.core.excel_parser import ExcelParser
from src.core.schemas import HoleSchema, AssaySchema


@pytest.fixture
def sample_hole_name() -> str:
    return "TestHole-123"

@pytest.fixture
def sample_coordinates() -> dict:
    return {"x": 100.0, "y": 200.0, "z": 50.0}


@pytest.fixture
def valid_hole_input_data(sample_hole_name, sample_coordinates) -> dict:
    return {
        "name": sample_hole_name,
        **sample_coordinates,
        "lenght": 150.0,
        "_level": 10.0,
        "issue_date": 203032040402
    }


@pytest.fixture
def expected_hole_output_data(sample_hole_name, sample_coordinates) -> dict:
    """Ожидаемый результат после model_dump(by_alias=True)"""
    return {
        "name": sample_hole_name,
        **sample_coordinates,
        "lenght": 150.0,
        "_level": 10.0,
        "issue_date": "203032040402"
    }

@pytest.fixture
def valid_assay_input_data(sample_hole_name) -> dict:
    return {
        "name": sample_hole_name,
        "_from": 0.0,
        "_to": 10.0,
        "Au": 1.5
    }

@pytest.fixture
def create_parser() -> ExcelParser:
    return ExcelParser()

@pytest.fixture
def wrong_excel_file_path() -> str:
    return str(BASE_DIR / "task" / "wrong_journal.xlsx")


@pytest.fixture
def sample_excel_path(tmp_path):
    import pandas as pd

    holes_data = pd.DataFrame({
        "ИМЯ": ["Hole1", "Hole2"],
        "X": [100.0, 200.0],
        "Y": [300.0, 400.0],
        "Z": [50.0, 60.0],
        "ДЛИНА": [150.0, 250.0],
        "ГОРИЗОНТ": [10.0, 20.0],
        "ДАТА ПРОХОДКИ": [20240101, 20240102]
    })

    assays_data = pd.DataFrame({
        "ОБЪЕКТ": ["Hole1", "Hole1", "Hole2"],
        "ОТ": [0.0, 10.0, 0.0],
        "ДО": [10.0, 20.0, 15.0],
        "Au": [1.5, 2.5, 3.5]
    })

    file_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        holes_data.to_excel(writer, sheet_name='Holes', index=False)
        assays_data.to_excel(writer, sheet_name='Assay', index=False)

    return str(file_path)

@pytest.fixture
def in_memory_db():
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE holes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            x REAL,
            y REAL,
            z REAL,
            lenght REAL,
            _level REAL,
            issue_date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE assay (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hole_id INTEGER,
            _from REAL,
            _to REAL,
            Au REAL,
            FOREIGN KEY (hole_id) REFERENCES holes(id)
        )
    """)
    yield connection
    connection.close()

@pytest.fixture
def sample_holes():
    return [
        HoleSchema(
            name="Hole1",
            x=100.0,
            y=200.0,
            z=50.0,
            lenght=150.0,
            _level=10.0,
            issue_date="422024011523"
        ),
        HoleSchema(
            name="Hole2",
            x=200.0,
            y=300.0,
            z=60.0,
            lenght=250.0,
            _level=20.0,
            issue_date="2320240116"
        )
    ]

@pytest.fixture
def sample_assays():
    return [
        AssaySchema(
            name="Hole1",
            _from=0.0,
            _to=10.0,
            Au=1.5
        ),
        AssaySchema(
            name="Hole1",
            _from=10.0,
            _to=20.0,
            Au=2.5
        ),
        AssaySchema(
            name="Hole2",
            _from=0.0,
            _to=15.0,
            Au=3.5
        )
    ]