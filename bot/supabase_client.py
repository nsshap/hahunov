import os
import uuid
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)

BUCKET = "congratulations"


async def upload_video(video_bytes: bytes, original_filename: str) -> str:
    """Загружает видео в Supabase Storage, возвращает публичный URL."""
    ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "mp4"
    remote_name = f"{uuid.uuid4()}.{ext}"

    supabase.storage.from_(BUCKET).upload(
        path=remote_name,
        file=video_bytes,
        file_options={"content-type": "video/mp4", "upsert": "true"},
    )

    return supabase.storage.from_(BUCKET).get_public_url(remote_name)


async def upload_audio(audio_bytes: bytes, original_filename: str) -> str:
    """Загружает аудио в Supabase Storage, возвращает публичный URL."""
    ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "ogg"
    remote_name = f"{uuid.uuid4()}.{ext}"

    supabase.storage.from_(BUCKET).upload(
        path=remote_name,
        file=audio_bytes,
        file_options={"content-type": "audio/ogg", "upsert": "true"},
    )

    return supabase.storage.from_(BUCKET).get_public_url(remote_name)


async def save_congrats(data: dict) -> None:
    """Сохраняет поздравление в таблицу congratulations."""
    supabase.table("congratulations").insert(data).execute()
