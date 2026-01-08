import pytest


import pandas as pd
from unittest.mock import patch

class TestExcelParser:
    def test_file_not_found(self, create_parser, wrong_excel_file_path):
        with pytest.raises(FileNotFoundError):
            create_parser.parse(wrong_excel_file_path)

    @patch('pandas.read_excel')
    def test_column_mapping(self, mock_read_excel, create_parser):
        mock_holes_df = pd.DataFrame({
            "ИМЯ": ["Hole1", "Hole2"],
            "X": [100.0, 200.0],
            "Y": [300.0, 400.0],
            "Z": [50.0, 60.0],
            "ДЛИНА": [150.0, 250.0],
            "ГОРИЗОНТ": [10.0, 20.0],
            "ДАТА ПРОХОДКИ": [20240101, 20240102]
        })

        mock_assays_df = pd.DataFrame({
            "ОБЪЕКТ": ["Hole1", "Hole1"],
            "ОТ": [0.0, 10.0],
            "ДО": [10.0, 20.0],
            "Au": [1.5, 2.5]
        })

        mock_read_excel.side_effect = lambda *args, **kwargs: (
            mock_holes_df if kwargs.get('sheet_name') == 'Holes'
            else mock_assays_df
        )

        parser = create_parser
        result = parser.parse("dummy.xlsx")

        holes_result = result["holes"]
        assert "name" in holes_result[0]
        assert "_level" in holes_result[0]
        assert "lenght" in holes_result[0]

        assays_result = result["assays"]
        assert "_from" in assays_result[0]
        assert "_to" in assays_result[0]

    @patch('pandas.read_excel')
    def test_empty_sheets(self, mock_read_excel, create_parser):
        mock_read_excel.return_value = pd.DataFrame()

        parser = create_parser
        result = parser.parse("dummy.xlsx")

        assert result["holes"] == []
        assert result["assays"] == []

    @patch('pandas.read_excel')
    def test_extra_columns_ignored(self, mock_read_excel, create_parser):
        mock_holes_df = pd.DataFrame({
            "ИМЯ": ["Hole1"],
            "X": [100.0],
            "EXTRA_COLUMN": ["extra_value"]  # Колонки нет в маппинге
        })

        mock_read_excel.return_value = mock_holes_df

        parser = create_parser
        result = parser.parse("dummy.xlsx")

        # EXTRA_COLUMN должна остаться в результате
        assert "EXTRA_COLUMN" in result["holes"][0]
        assert result["holes"][0]["EXTRA_COLUMN"] == "extra_value"

    @patch('pandas.read_excel')
    def test_column_stripping(self, mock_read_excel, create_parser):
        mock_holes_df = pd.DataFrame({
            "  ИМЯ  ": ["Hole1"],  # Колонка с пробелами
            "X ": [100.0]  # Колонка с пробелом в конце
        })

        mock_read_excel.return_value = mock_holes_df

        parser = create_parser
        result = parser.parse("dummy.xlsx")

        assert "name" in result["holes"][0]

    @patch('pandas.read_excel')
    def test_return_structure(self, mock_read_excel, create_parser):
        mock_holes_df = pd.DataFrame({"ИМЯ": ["Hole1"], "X": [100.0]})
        mock_assays_df = pd.DataFrame({"ОБЪЕКТ": ["Hole1"], "ОТ": [0.0]})

        mock_read_excel.side_effect = lambda *args, **kwargs: (
            mock_holes_df if kwargs.get('sheet_name') == 'Holes'
            else mock_assays_df
        )

        parser = create_parser
        result = parser.parse("dummy.xlsx")

        assert isinstance(result, dict)
        assert "holes" in result
        assert "assays" in result
        assert isinstance(result["holes"], list)
        assert isinstance(result["assays"], list)


    @patch('pandas.read_excel', side_effect=Exception("Excel read error"))
    def test_excel_read_error(self, mock_read_excel, create_parser):
        parser = create_parser
        with pytest.raises(Exception, match="Excel read error"):
            parser.parse("dummy.xlsx")
