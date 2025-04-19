import zipfile
import os
import tempfile
import shutil
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


def cover_from_audio(file):
    if hasattr(file, "name"):
        file_name = file.name
    else:
        file_name = ""
    audio = File(file, easy=False)
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


def audio_from_zip(zip_path: str, audio_filename: str = "audio.mp3") -> str:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        file_list = zip_ref.namelist()
        if audio_filename not in file_list:
            raise FileNotFoundError(f"{audio_filename} not found in the archive.")

        with zip_ref.open(audio_filename) as audio_file:
            suffix = f".{audio_filename.split('.')[-1]}"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(audio_file, tmp)
                return tmp.name


def is_archive(file):
    if isinstance(file, str):
        _, ext = os.path.splitext(file)
    elif hasattr(file, "name"):
        _, ext = os.path.splitext(file.name)
    else:
        return False
    return ext.lower() in [".olz", ".osz", ".osu"]


def save_file(file):
    suffix = f".{file.name.split('.')[-1]}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file, tmp)
        return tmp.name
