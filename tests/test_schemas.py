import pytest
from pydantic import BaseModel

from src.core.schemas import EmptyFieldMixin, HoleSchema, AssaySchema


class TestEmptyFieldMixin:
    class TestModel(BaseModel, EmptyFieldMixin):
        __test__ = False

        field1: str
        field2: int

    def test_valid_data_passes(self):
        model = self.TestModel(field1="valid", field2=123)
        assert model.field1 == "valid"
        assert model.field2 == 123

    def test_empty_string_raises_error(self):
        with pytest.raises(ValueError, match="Поле не может быть пустым"):
            self.TestModel(field1="", field2=123)

    def test_whitespace_string_raises_error(self):
        with pytest.raises(ValueError, match="Поле не может быть пустым"):
            self.TestModel(field1="   ", field2=123)

    def test_none_for_string_field_raises_error(self):
        with pytest.raises(ValueError, match="Поле не может быть пустым"):
            self.TestModel(field1=None, field2=123)

    def test_zero_for_int_field_passes(self):
        model = self.TestModel(field1="valid", field2=0)
        assert model.field2 == 0

    def test_empty_string_with_spaces_only_raises_error(self):
        with pytest.raises(ValueError):
            self.TestModel(field1="\t\n\r ", field2=123)

class TestHoleSchema:
    def test_hole_schema_creation(self, valid_hole_input_data):
        hole = HoleSchema(**valid_hole_input_data)

        assert hole.name == "TestHole-123"
        assert hole.x == 100.0
        assert hole.y == 200.0
        assert hole.z == 50.0
        assert hole.level_ == 10.0


    def test_hole_model_dump_with_aliases(self, valid_hole_input_data, expected_hole_output_data):
        hole = HoleSchema(**valid_hole_input_data)

        result_dict = hole.model_dump(by_alias=True)

        assert result_dict == expected_hole_output_data

        assert "_level" in result_dict
        assert "level_" not in result_dict

    def test_hole_with_negative_length(self, sample_hole_name, sample_coordinates):
        with pytest.raises(ValueError):
            HoleSchema(
                name=sample_hole_name,
                **sample_coordinates,
                lenght=-150.0,
                level_=10.0,
                issue_date="2024-01-15"
            )


class TestAssaySchema:
    def test_assay_schema_creation(self, valid_assay_input_data):
        assay = AssaySchema(**valid_assay_input_data)

        assert assay.name == "TestHole-123"
        assert assay.from_ == 0.0
        assert assay.to_ == 10.0
        assert assay.Au == 1.5


    def test_assay_model_dump_with_aliases(self, valid_assay_input_data):
        assay = AssaySchema(**valid_assay_input_data)
        result_dict = assay.model_dump(by_alias=True)

        assert result_dict == valid_assay_input_data
        assert "_from" in result_dict
        assert "_to" in result_dict

    def test_assay_with_zero_au(self, sample_hole_name):
        with pytest.raises(ValueError):
            AssaySchema(
                name=sample_hole_name,
                from_=0.0,
                to_=10.0,
                Au=0.0
            )


def test_hole_and_assay_connection(valid_hole_input_data, valid_assay_input_data):
    hole = HoleSchema(**valid_hole_input_data)
    assay = AssaySchema(**valid_assay_input_data)

    assert hole.name == assay.name

    hole_dict = hole.model_dump(by_alias=True)
    assay_dict = assay.model_dump(by_alias=True)

    assert hole_dict["name"] == assay_dict["name"]




