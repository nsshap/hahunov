import io
import os

from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states import CongratsFlow
from geocode import geocode_city, reverse_geocode
from supabase_client import upload_video, save_congrats

router = Router()

WEBSITE_URL = os.environ.get("WEBSITE_URL", "")
MAX_VIDEO_BYTES = 20 * 1024 * 1024  # 20 МБ — лимит Telegram Bot API
DONE_BTN = "Готово ✅"


# ── Клавиатуры ──────────────────────────────────────────────────────────────

def skip_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить →")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def location_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Поделиться геолокацией", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def done_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=DONE_BTN)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# ── Шаг 1 — /start ──────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! 20 марта у Лёши и Алины родилась дочка Варвара 🌸\n\n"
        "Давай запишем твоё поздравление для неё и её родителей — "
        "оно появится на карте мира.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Как тебя зовут? (имя и фамилия или просто имя — как хочешь)"
    )
    await state.set_state(CongratsFlow.name)


# ── Шаг 2 — Имя ─────────────────────────────────────────────────────────────

@router.message(CongratsFlow.name, F.text)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer(
        "Из какого ты города и страны?\n"
        "Напиши или нажми кнопку ниже 👇",
        reply_markup=location_kb(),
    )
    await state.set_state(CongratsFlow.city)


# ── Шаг 3 — Город (геолокация) ──────────────────────────────────────────────

@router.message(CongratsFlow.city, F.location)
async def step_city_geo(message: Message, state: FSMContext):
    lat = message.location.latitude
    lng = message.location.longitude
    city = await reverse_geocode(lat, lng)

    await state.update_data(city=city, lat=lat, lng=lng)
    await message.answer(f"📍 {city}", reply_markup=ReplyKeyboardRemove())
    await ask_videos(message, state)


# ── Шаг 3 — Город (текст) ───────────────────────────────────────────────────

@router.message(CongratsFlow.city, F.text)
async def step_city_text(message: Message, state: FSMContext):
    city_text = message.text.strip()
    coords = await geocode_city(city_text)

    if coords:
        lat, lng = coords
        await state.update_data(city=city_text, lat=lat, lng=lng)
    else:
        await state.update_data(city=city_text, lat=None, lng=None)

    await ask_videos(message, state)


async def ask_videos(message: Message, state: FSMContext):
    await state.update_data(video_urls=[])
    await message.answer(
        "Запиши видеопоздравление для Вари и её родителей 🎥\n"
        "_(до 2 минут, можно отправить несколько)_",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CongratsFlow.videos)


# ── Шаг 4 — Видео (несколько) ───────────────────────────────────────────────

@router.message(CongratsFlow.videos, F.video | F.video_note)
async def step_video(message: Message, state: FSMContext, bot: Bot):
    video = message.video or message.video_note

    if video.file_size and video.file_size > MAX_VIDEO_BYTES:
        await message.answer(
            "Видео слишком большое (больше 20 МБ) 😔\n"
            "Попробуй записать покороче или сжать перед отправкой."
        )
        return

    await message.answer("Загружаем видео… ⏳")

    file = await bot.get_file(video.file_id)
    buf = io.BytesIO()
    await bot.download_file(file.file_path, buf)
    buf.seek(0)

    url = await upload_video(buf.read(), f"{video.file_id}.mp4")

    data = await state.get_data()
    video_urls = data.get("video_urls", [])
    video_urls.append(url)
    await state.update_data(video_urls=video_urls)

    count = len(video_urls)
    await message.answer(
        f"Видео {count} принято ✅\nМожешь отправить ещё или нажми кнопку ниже.",
        reply_markup=done_kb(),
    )


@router.message(CongratsFlow.videos, F.text == DONE_BTN)
async def step_videos_done(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("video_urls"):
        await message.answer("Сначала отправь хотя бы одно видео 🎥")
        return
    await ask_message(message, state)


@router.message(CongratsFlow.videos)
async def step_videos_wrong(message: Message):
    await message.answer("Пожалуйста, отправь видео 🎥 или нажми «Готово ✅».")


# ── Шаг 5 — Пожелание текстом ───────────────────────────────────────────────

async def ask_message(message: Message, state: FSMContext):
    await message.answer(
        "Напиши пару слов — это будет подпись под твоим пином на карте 🗺️",
        reply_markup=skip_kb(),
    )
    await state.set_state(CongratsFlow.message)


@router.message(CongratsFlow.message, F.text)
async def step_message(message: Message, state: FSMContext):
    text = None if message.text == "Пропустить →" else message.text.strip()
    await state.update_data(message=text)

    await message.answer(
        "Твой непрошеный совет — родителям или Варе, на твой выбор 😄",
        reply_markup=skip_kb(),
    )
    await state.set_state(CongratsFlow.advice)


# ── Шаг 6 — Непрошеный совет ────────────────────────────────────────────────

@router.message(CongratsFlow.advice, F.text)
async def step_advice(message: Message, state: FSMContext):
    advice = None if message.text == "Пропустить →" else message.text.strip()

    data = await state.get_data()
    await save_congrats({
        "name":       data.get("name"),
        "city":       data.get("city"),
        "lat":        data.get("lat"),
        "lng":        data.get("lng"),
        "video_urls": data.get("video_urls", []),
        "message":    data.get("message"),
        "advice":     advice,
    })

    website_line = f"\n\n🌍 Посмотреть на карте: {WEBSITE_URL}" if WEBSITE_URL else ""
    await message.answer(
        f"Спасибо! Твоё поздравление уже на карте 🗺️{website_line}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
