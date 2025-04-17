import zipfile
import os
import magic
import streamlit as st
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


def extract_cover(uploaded_file):
    # Проверяем, является ли uploaded_file объектом с атрибутом .name (например, файла)
    if hasattr(uploaded_file, "name"):
        file_name = uploaded_file.name
    else:
        file_name = ""  # Присваиваем пустую строку, если атрибута нет

    audio = File(uploaded_file, easy=False)
    if audio is None:
        return None
    if audio.tags is None:
        return None
    if file_name.endswith(".mp3") and hasattr(audio, "tags"):
        for tag in audio.tags.values():
            if tag.FrameID == "APIC":
                return tag.data
    if file_name.endswith(".flac") and isinstance(audio, FLAC):
        if audio.pictures:
            return audio.pictures[0].data
    if file_name.endswith((".m4a", ".mp4")) and isinstance(audio, MP4):
        covr = audio.tags.get("covr")
        if covr:
            return covr[0]
    return None


def extract_audio_from_zip(zip_path: str, audio_filename: str = "audio.mp3") -> str:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        file_list = zip_ref.namelist()
        if audio_filename not in file_list:
            raise FileNotFoundError(f"{audio_filename} not found in the archive.")
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        zip_ref.extract(audio_filename, temp_dir)
        return os.path.join(temp_dir, audio_filename)


def is_archive(uploaded_file):
    if isinstance(uploaded_file, str):
        _, ext = os.path.splitext(uploaded_file)
    elif hasattr(uploaded_file, "name"):
        _, ext = os.path.splitext(uploaded_file.name)
    else:
        return False
    return ext.lower() in [".olz", ".osz", ".osu"]
