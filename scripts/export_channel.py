"""
Скрипт выгрузки медиа из Telegram-канала в Supabase.

Что делает:
  1. Проходит по всем сообщениям канала
  2. Скачивает фото и видео во временную папку
  3. Загружает их в Supabase Storage
  4. Создаёт строку в таблице day_pins (lat/lng остаются пустыми — заполнить вручную)

Запуск:
  pip install -r requirements.txt
  cp .env.example .env   # заполнить .env
  python export_channel.py
"""

import asyncio
import mimetypes
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

load_dotenv()

TG_API_ID    = int(os.environ["TG_API_ID"])
TG_API_HASH  = os.environ["TG_API_HASH"]
TG_PHONE     = os.environ["TG_PHONE"]
TG_CHANNEL   = os.environ["TG_CHANNEL"]

SUPABASE_URL         = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
SUPABASE_BUCKET      = os.environ.get("SUPABASE_BUCKET", "day-pins")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def is_video(document) -> bool:
    if document.mime_type and document.mime_type.startswith("video/"):
        return True
    return False


def get_extension(media) -> str:
    if isinstance(media, MessageMediaPhoto):
        return ".jpg"
    doc = media.document
    ext = mimetypes.guess_extension(doc.mime_type or "")
    # guess_extension иногда возвращает странные расширения
    if ext in (None, ".jpe"):
        ext = ".jpg"
    return ext


def upload_to_supabase(local_path: Path, remote_name: str, mime: str) -> str:
    """Загружает файл в Supabase Storage и возвращает публичный URL."""
    with open(local_path, "rb") as f:
        data = f.read()

    supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=remote_name,
        file=data,
        file_options={"content-type": mime, "upsert": "true"},
    )

    result = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(remote_name)
    return result


def insert_pin(media_url: str, media_type: str, title: str):
    """Создаёт строку в day_pins. lat/lng = NULL — заполнить вручную."""
    supabase.table("day_pins").insert({
        "media_url": media_url,
        "media_type": media_type,
        "title": title,
        "lat": None,
        "lng": None,
    }).execute()


async def main():
    async with TelegramClient("session_export", TG_API_ID, TG_API_HASH) as client:
        await client.start(phone=TG_PHONE)

        print(f"Подключились. Читаем канал: {TG_CHANNEL}\n")

        with tempfile.TemporaryDirectory() as tmp_dir:
            async for message in client.iter_messages(TG_CHANNEL, reverse=True):
                media = message.media

                # Пропускаем сообщения без медиа
                if not isinstance(media, (MessageMediaPhoto, MessageMediaDocument)):
                    continue

                # Определяем тип
                if isinstance(media, MessageMediaPhoto):
                    media_type = "photo"
                    mime = "image/jpeg"
                elif is_video(media.document):
                    media_type = "video"
                    mime = media.document.mime_type
                else:
                    # Другие документы (gif, audio и т.д.) — пропускаем
                    print(f"  [skip] msg {message.id}: не фото и не видео")
                    continue

                ext = get_extension(media)
                remote_name = f"{message.id}{ext}"
                local_path = Path(tmp_dir) / remote_name

                # Подпись из текста сообщения (если есть)
                title = (message.text or "").strip() or f"Без подписи (msg {message.id})"

                print(f"[{media_type}] msg {message.id}: скачиваем...")
                await client.download_media(message, file=str(local_path))

                print(f"  → загружаем в Supabase Storage...")
                public_url = upload_to_supabase(local_path, remote_name, mime)

                print(f"  → сохраняем в day_pins...")
                insert_pin(public_url, media_type, title)

                print(f"  ✓ готово: {public_url}\n")

        print("Готово! Теперь откройте таблицу day_pins в Supabase Dashboard")
        print("и заполните поля lat/lng для каждой строки.")


if __name__ == "__main__":
    asyncio.run(main())
