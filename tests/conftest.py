import pytest

from src.core.config import BASE_DIR
from src.core.excel_parser import ExcelParser


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
    """Создает временный Excel файл для тестов"""
    import pandas as pd

    # Создаем тестовые данные
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

    # Сохраняем во временный файл
    file_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        holes_data.to_excel(writer, sheet_name='Holes', index=False)
        assays_data.to_excel(writer, sheet_name='Assay', index=False)

    return str(file_path)


# Интеграционный тест с реальным Excel файлом
def test_parser_with_real_file(create_parser, sample_excel_path):
    """Интеграционный тест с реальным Excel файлом"""
    parser = create_parser
    result = parser.parse(sample_excel_path)

    assert len(result["holes"]) == 2
    assert len(result["assays"]) == 3

    # Проверяем маппинг
    first_hole = result["holes"][0]
    assert "name" in first_hole  # Было "ИМЯ"
    assert "_level" in first_hole  # Было "ГОРИЗОНТ"