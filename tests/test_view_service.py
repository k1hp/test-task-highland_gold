import pytest
from unittest.mock import Mock
from src.services.view_service import ViewService


class TestViewService:
    def test_get_holes_for_display_returns_valid_data(self):
        mock_db = Mock()
        mock_db.get_all_holes.return_value = [
            {"Имя скважины": "Hole1", "ОТ": 0.0, "ДО": 10.0, "Au": 1.5}
        ]

        service = ViewService(mock_db)

        result = service.get_holes_for_display()

        assert len(result) == 1
        assert result[0]["Имя скважины"] == "Hole1"
        mock_db.get_all_holes.assert_called_once()

    def test_get_holes_for_display_with_empty_db(self):
        mock_db = Mock()
        mock_db.get_all_holes.return_value = []

        service = ViewService(mock_db)
        result = service.get_holes_for_display()

        assert result == []

    def test_validate_display_data_filters_invalid(self):
        service = ViewService(Mock())

        raw_data = [
            {"Имя скважины": "Hole1", "ОТ": 0.0, "ДО": 10.0, "Au": 1.5},
            {"Имя скважины": "", "ОТ": "not_a_number", "ДО": 10.0, "Au": 1.5},
            {"Имя скважины": "Hole2", "ОТ": 5.0, "ДО": 15.0, "Au": 2.5}
        ]

        result = service._validate_display_data(raw_data)

        assert len(result) == 2
        assert result[0]["Имя скважины"] == "Hole1"
        assert result[1]["Имя скважины"] == "Hole2"

    def test_validate_display_data_all_invalid(self):
        service = ViewService(Mock())

        raw_data = [
            {"wrong_key": "value"},
            {"Имя скважины": None, "ОТ": 0.0, "ДО": 10.0, "Au": 1.5}
        ]

        result = service._validate_display_data(raw_data)

        assert result == []

    def test_service_initialization(self):
        mock_db = Mock()
        service = ViewService(mock_db)

        assert service.db_manager == mock_db

    @pytest.mark.parametrize("field,value", [
        ("ОТ", "not_a_float"),
        ("Au", -1.5),
        ("Имя скважины", 123),
    ])
    def test_validation_rejects_invalid_types(self, field, value):
        service = ViewService(Mock())

        data = {"Имя скважины": "Hole1", "ОТ": 0.0, "ДО": 10.0, "Au": 1.5}
        data[field] = value

        result = service._validate_display_data([data])

        assert result == []

    def test_validation_passes_correct_data(self):
        service = ViewService(Mock())

        valid_data = [
            {"Имя скважины": "Hole1", "ОТ": 0.0, "ДО": 10.0, "Au": 0.0},
            {"Имя скважины": "Hole2", "ОТ": -5.0, "ДО": 5.0, "Au": 1.5},
            {"Имя скважины": "Long Name Here", "ОТ": 100.5, "ДО": 200.5, "Au": 99.99}
        ]

        result = service._validate_display_data(valid_data)

        assert len(result) == 3
        assert result[0]["Имя скважины"] == "Hole1"
        assert result[1]["Au"] == 1.5
        assert result[2]["ОТ"] == 100.5

    @pytest.fixture
    def mock_logger(self, monkeypatch):
        mock_log = Mock()
        monkeypatch.setattr("src.core.services.view_service.LOGGER", mock_log)
        return mock_log
