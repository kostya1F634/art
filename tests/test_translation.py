import pytest
import tempfile
import json
from translation import translation, translation_json


@pytest.fixture
def temp_translation_file():
    data = {
        "en": {"hello": "Hello"},
        "ru": {"hello": "Привет"},
    }
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        yield f.name


def test_translation_json(temp_translation_file):
    result = translation_json(temp_translation_file)
    assert result["en"]["hello"] == "Hello"
    assert result["ru"]["hello"] == "Привет"


def test_translation_existing_language(temp_translation_file):
    result = translation("ru", path=temp_translation_file)
    assert result["hello"] == "Привет"


def test_translation_fallback_language(temp_translation_file):
    result = translation("de", path=temp_translation_file)
    assert result["hello"] == "Hello"
