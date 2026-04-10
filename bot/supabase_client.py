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


async def log_session(user: object) -> None:
    supabase.table("bot_sessions").insert({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": user.language_code,
        "is_premium": bool(user.is_premium),
    }).execute()


async def get_stats() -> dict:
    rows = supabase.table("bot_sessions").select("user_id, first_name, last_name, username, started_at, language_code, is_premium").execute().data
    if not rows:
        return {"total": 0, "unique": 0, "today": 0, "premium": 0, "languages": {}, "recent": []}

    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date()

    unique_users = {r["user_id"] for r in rows}
    today_users = {r["user_id"] for r in rows if r["started_at"][:10] == str(today)}
    premium_count = sum(1 for r in rows if r.get("is_premium"))

    langs: dict = {}
    for r in rows:
        lc = r.get("language_code") or "?"
        langs[lc] = langs.get(lc, 0) + 1

    recent = sorted(rows, key=lambda r: r["started_at"], reverse=True)[:5]

    return {
        "total": len(rows),
        "unique": len(unique_users),
        "today": len(today_users),
        "premium": premium_count,
        "languages": langs,
        "recent": recent,
    }
