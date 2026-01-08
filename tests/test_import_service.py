import pytest
from unittest.mock import Mock
from src.core.schemas import HoleSchema, AssaySchema
from src.services.import_service import ImportService


class TestImportService:
    @pytest.fixture
    def mock_parser(self):
        return Mock()

    @pytest.fixture
    def mock_db_manager(self):
        return Mock()

    @pytest.fixture
    def sample_raw_data(self):
        return {
            "holes": [
                {"name": "Hole1", "x": 100.0, "y": 200.0, "z": 50.0,
                 "lenght": 150.0, "_level": 10.0, "issue_date": "2024-01-15"},
                {"name": "Hole2", "x": 200.0, "y": 300.0, "z": 60.0,
                 "lenght": 250.0, "_level": 20.0, "issue_date": "2024-01-16"}
            ],
            "assays": [
                {"name": "Hole1", "_from": 0.0, "_to": 10.0, "Au": 1.5},
                {"name": "Hole1", "_from": 10.0, "_to": 20.0, "Au": 2.5}
            ]
        }

    @pytest.fixture
    def import_service(self, mock_parser, mock_db_manager):
        return ImportService(mock_parser, mock_db_manager)

    def test_extract_data_calls_parser(self, import_service, mock_parser):
        file_path = "test.xlsx"
        expected_data = {"holes": [], "assays": []}
        mock_parser.parse.return_value = expected_data

        result = import_service._extract_data(file_path)

        mock_parser.parse.assert_called_once_with(file_path)
        assert result == expected_data

    def test_validate_single_type_creates_schemas(self, import_service):
        raw_holes = [
            {"name": "Hole1", "x": 100.0, "y": 200.0, "z": 50.0,
             "lenght": 150.0, "_level": 10.0, "issue_date": "2024-01-15"}
        ]

        result = import_service._validate_single_type(HoleSchema, raw_holes)

        assert len(result) == 1
        assert isinstance(result[0], HoleSchema)
        assert result[0].name == "Hole1"
        assert result[0].x == 100.0

    def test_validate_single_type_empty_list(self, import_service):
        result = import_service._validate_single_type(HoleSchema, [])

        assert result == []
        assert isinstance(result, list)

    def test_transform_and_validate_creates_all_schemas(self, import_service, sample_raw_data):
        result = import_service._transform_and_validate(sample_raw_data)

        assert "holes" in result
        assert "assays" in result
        assert isinstance(result["holes"][0], HoleSchema)
        assert isinstance(result["assays"][0], AssaySchema)
        assert len(result["holes"]) == 2
        assert len(result["assays"]) == 2


    def test_load_data_calls_db_manager(self, import_service, mock_db_manager, sample_raw_data):
        validated_data = import_service._transform_and_validate(sample_raw_data)

        import_service._load_data(validated_data)

        mock_db_manager.save_import_data.assert_called_once()
        call_args = mock_db_manager.save_import_data.call_args[0]
        assert len(call_args[0]) == 2  # holes
        assert len(call_args[1]) == 2  # assays
        assert isinstance(call_args[0][0], HoleSchema)
        assert isinstance(call_args[1][0], AssaySchema)

    def test_import_data_full_flow(self, import_service, mock_parser, mock_db_manager, sample_raw_data):
        mock_parser.parse.return_value = sample_raw_data

        import_service.import_data("test.xlsx")

        mock_parser.parse.assert_called_once_with("test.xlsx")
        mock_db_manager.save_import_data.assert_called_once()

    def test_import_data_with_parser_error(self, import_service, mock_parser, mock_db_manager):
        mock_parser.parse.side_effect = Exception("Parse error")

        with pytest.raises(Exception, match="Parse error"):
            import_service.import_data("test.xlsx")

        mock_db_manager.save_import_data.assert_not_called()

    def test_import_data_with_validation_error(self, import_service, mock_parser, mock_db_manager):
        invalid_data = {
            "holes": [{"name": "", "x": "not_a_number"}],  # Invalid data
            "assays": []
        }
        mock_parser.parse.return_value = invalid_data

        with pytest.raises(Exception):
            import_service.import_data("test.xlsx")

        mock_db_manager.save_import_data.assert_not_called()

    def test_schema_mapping_correct(self, import_service):
        assert import_service.SCHEMA_MAPPING["holes"] == HoleSchema
        assert import_service.SCHEMA_MAPPING["assays"] == AssaySchema

    def test_service_initialization(self):
        parser = Mock()
        db_manager = Mock()

        service = ImportService(parser, db_manager)

        assert service.parser == parser
        assert service.db_manager == db_manager

    def test_import_empty_file(self, import_service, mock_parser, mock_db_manager):
        empty_data = {"holes": [], "assays": []}
        mock_parser.parse.return_value = empty_data

        import_service.import_data("empty.xlsx")

        mock_db_manager.save_import_data.assert_called_once_with([], [])
