import pytest

@pytest.fixture
def sample_hole_name() -> str:
    return "TestHole-123"

@pytest.fixture
def sample_coordinates() -> dict:
    return {"x": 100.0, "y": 200.0, "z": 50.0}


@pytest.fixture
def valid_hole_input_data(sample_hole_name, sample_coordinates):
    return {
        "name": sample_hole_name,
        **sample_coordinates,
        "lenght": 150.0,
        "_level": 10.0,
        "issue_date": 203032040402
    }


@pytest.fixture
def expected_hole_output_data(sample_hole_name, sample_coordinates):
    """Ожидаемый результат после model_dump(by_alias=True)"""
    return {
        "name": sample_hole_name,
        **sample_coordinates,
        "lenght": 150.0,
        "_level": 10.0,
        "issue_date": "203032040402"
    }

@pytest.fixture
def valid_assay_input_data(sample_hole_name):
    return {
        "name": sample_hole_name,
        "_from": 0.0,
        "_to": 10.0,
        "Au": 1.5
    }
