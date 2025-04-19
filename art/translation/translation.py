import json
import streamlit as st
from typing import Dict


@st.cache_data
def translation_json(path) -> Dict[str, Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def translation(
    lang: str, path: str = "art/translation/translation.json"
) -> Dict[str, str]:
    translations = translation_json(path)
    return translations.get(lang, translations["en"])
