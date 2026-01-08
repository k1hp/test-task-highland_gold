import pytest
import sqlite3
from unittest.mock import patch
from src.core.db_manager import SQLiteDataManager


class TestSQLiteDataManager:


    def test_save_holes(self, in_memory_db, sample_holes):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager._save_holes(sample_holes)

        cursor = in_memory_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM holes")
        count = cursor.fetchone()[0]
        assert count == 2

    def test_save_assays_with_existing_hole(self, in_memory_db, sample_holes, sample_assays):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager._save_holes(sample_holes)
        manager._save_assays(sample_assays)

        cursor = in_memory_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM assay")
        count = cursor.fetchone()[0]
        assert count == 3

    def test_save_assays_without_hole(self, in_memory_db, sample_assays):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager._save_assays(sample_assays)

        cursor = in_memory_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM assay")
        count = cursor.fetchone()[0]
        assert count == 0

    def test_save_import_data_transaction(self, in_memory_db, sample_holes, sample_assays):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager.save_import_data(sample_holes, sample_assays)

        cursor = in_memory_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM holes")
        holes_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM assay")
        assays_count = cursor.fetchone()[0]

        assert holes_count == 2
        assert assays_count == 3

    def test_get_all_holes(self, in_memory_db, sample_holes, sample_assays):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager.save_import_data(sample_holes, sample_assays)
        result = manager.get_all_holes()

        assert isinstance(result, list)
        assert len(result) == 3  # сколько записей в assay соответствуют holes
        assert "Имя скважины" in result[0]
        assert "ОТ" in result[0]
        assert "ДО" in result[0]
        assert "Au" in result[0]

    def test_get_all_holes_empty(self, in_memory_db):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        result = manager.get_all_holes()
        assert result == []

    def test_save_empty_data(self, in_memory_db):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager.save_import_data([], [])

        cursor = in_memory_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM holes")
        holes_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM assay")
        assays_count = cursor.fetchone()[0]

        assert holes_count == 0
        assert assays_count == 0

    @patch('sqlite3.connect')
    def test_connection_error(self, mock_connect):
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        with pytest.raises(sqlite3.Error):
            SQLiteDataManager("test.db")

    def test_data_integrity(self, in_memory_db, sample_holes, sample_assays):
        manager = SQLiteDataManager(":memory:")
        manager.connection = in_memory_db

        manager.save_import_data(sample_holes, sample_assays)

        cursor = in_memory_db.cursor()
        cursor.execute("""
            SELECT h.name, a._from, a._to, a.Au
            FROM holes h
            JOIN assay a ON h.id = a.hole_id
            ORDER BY h.name, a._from
        """)

        results = cursor.fetchall()
        assert len(results) == 3
        assert results[0][0] == "Hole1"
        assert results[2][0] == "Hole2"