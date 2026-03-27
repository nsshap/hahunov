"""
Скрипт загрузки медиафайлов из папки в Supabase.

Запуск:
  pip3 install -r requirements.txt
  python3 upload_export.py --export /путь/до/папки/с/файлами
"""

import argparse
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL         = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
SUPABASE_BUCKET      = os.environ.get("SUPABASE_BUCKET", "day-pins")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

SUPPORTED_PHOTO = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
SUPPORTED_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}


def detect_type(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext in SUPPORTED_PHOTO:
        return "photo"
    if ext in SUPPORTED_VIDEO:
        return "video"
    return None


def upload_file(local_path: Path) -> str:
    """Загружает файл в Supabase Storage и возвращает публичный URL."""
    mime, _ = mimetypes.guess_type(str(local_path))
    mime = mime or "application/octet-stream"
    remote_name = local_path.name

    with open(local_path, "rb") as f:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=remote_name,
            file=f.read(),
            file_options={"content-type": mime, "upsert": "true"},
        )

    return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(remote_name)


def insert_pin(media_url: str, media_type: str, filename: str):
    supabase.table("day_pins").insert({
        "media_url":  media_url,
        "media_type": media_type,
        "caption":    None,     # заполнить вручную в Supabase Dashboard
        "location":   None,     # заполнить вручную
        "lat":        None,     # заполнить вручную
        "lng":        None,     # заполнить вручную
    }).execute()


def main():
    parser = argparse.ArgumentParser(description="Загрузить медиафайлы из папки в Supabase")
    parser.add_argument("--export", required=True, help="Путь до папки с фото и видео")
    args = parser.parse_args()

    folder = Path(args.export)

    if not folder.exists():
        print(f"Ошибка: папка не найдена — {folder}")
        return

    files = sorted(folder.iterdir())
    media_files = [f for f in files if f.is_file() and detect_type(f)]

    print(f"Найдено файлов: {len(media_files)}")
    print()

    uploaded = 0
    skipped  = 0

    for file in media_files:
        media_type = detect_type(file)

        print(f"[{media_type}] {file.name} → загружаем...", end=" ", flush=True)
        try:
            url = upload_file(file)
            insert_pin(url, media_type, file.name)
            print("✓")
            uploaded += 1
        except Exception as e:
            print(f"✗ ошибка: {e}")
            skipped += 1

    print()
    print(f"Готово! Загружено: {uploaded}, ошибок: {skipped}")
    print()
    print("Откройте Supabase Dashboard → Table Editor → day_pins")
    print("и заполните поля location, lat, lng, caption для каждой строки.")


if __name__ == "__main__":
    main()
