import zipfile
import os
import tempfile
import io
import shutil


def insert_timing_points(zip_path, timing_points):
    timing_points_st = format_timing_points(timing_points)
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
        osu_files = [f for f in os.listdir(tmpdir) if f.endswith(".osu")]
        if not osu_files:
            raise ValueError("No .osu file found in the archive.")
        osu_path = os.path.join(tmpdir, osu_files[0])
        with open(osu_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            if line.strip() == "[TimingPoints]":
                i += 1
                new_lines.append(timing_points_st + "\n")
                while i < len(lines):
                    if (
                        lines[i].strip().startswith("[")
                        and lines[i].strip() != "[TimingPoints]"
                    ):
                        break
                    i += 1
                break
            i += 1
        new_lines.extend(lines[i:])
        with open(osu_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        with zipfile.ZipFile(zip_path, "w") as zip_write:
            for file_name in os.listdir(tmpdir):
                file_path = os.path.join(tmpdir, file_name)
                zip_write.write(file_path, arcname=file_name)


def create_beatmap(audio_file, title, artist, timing_points):
    timing_points_st = format_timing_points(timing_points)
    osu_name = f"{artist} - {title} (ART) [].osu"

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Сохраняем аудиофайл во временную директорию
        audio_path = os.path.join(tmpdir, "audio.mp3")

        with open(audio_path, "wb") as f:
            # Проверяем, является ли audio_file строкой (путь к файлу) или объектом файла
            if isinstance(audio_file, str):
                # Если передан путь к файлу, открываем его
                with open(audio_file, "rb") as audio_f:
                    f.write(audio_f.read())
            else:
                # Если это объект файла (например, BytesIO), читаем его
                if hasattr(audio_file, "seek"):
                    audio_file.seek(0)
                f.write(audio_file.read())

        # 2. Копируем и редактируем .osu файл
        osu_template_path = "art/template/template.osu"
        osu_target_path = os.path.join(tmpdir, osu_name)
        shutil.copy(osu_template_path, osu_target_path)

        with open(osu_target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("Title:"):
                new_lines.append(f"Title:{title}\n")
            elif line.startswith("Artist:"):
                new_lines.append(f"Artist:{artist}\n")
            else:
                new_lines.append(line)
            if line.strip() == "[TimingPoints]":
                i += 1
                new_lines.append(timing_points_st)
                while i < len(lines):
                    if (
                        lines[i].strip().startswith("[")
                        and lines[i].strip() != "[TimingPoints]"
                    ):
                        break
                    i += 1
                continue
            i += 1
        new_lines.extend(lines[i:])

        with open(osu_target_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # 3. Создаем ZIP в памяти
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zipf:
            zipf.write(audio_path, arcname="audio.mp3")
            zipf.write(osu_target_path, arcname=osu_name)

        buffer.seek(0)
        return buffer


def format_timing_points(timing_points):
    result = []
    for interval in timing_points:
        start, bpm = interval
        start_ms = int(start * 1000)
        beat_length = 60000 / bpm
        result.append(f"{start_ms},{beat_length},4,1,0,100,1,0")
    return "\n".join(result) + "\n"
