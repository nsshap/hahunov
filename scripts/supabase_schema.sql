-- Запустить в Supabase Dashboard → SQL Editor

create table day_pins (
  id         bigserial primary key,
  lat        double precision,
  lng        double precision,
  location   text,                   -- название места, например "Лондон"
  caption    text,                   -- текст подписи из Telegram (опционально)
  media_url  text not null,
  media_type text not null check (media_type in ('photo', 'video')),
  created_at timestamptz default now()
);

-- Разрешить публичное чтение (для сайта)
alter table day_pins enable row level security;

create policy "Public read" on day_pins
  for select using (true);


-- ── Поздравления из Telegram бота ───────────────────────────────────────────

create table congratulations (
  id         bigserial primary key,
  lat        double precision,
  lng        double precision,
  name       text,                   -- имя отправителя
  city       text,                   -- город (текст)
  video_urls text[],                 -- видео в Supabase Storage (массив)
  audio_urls text[],                 -- голосовые сообщения (массив)
  message    text,                   -- пожелание (опционально)
  advice     text,                   -- непрошеный совет (опционально)
  created_at timestamptz default now()
);

alter table congratulations enable row level security;

create policy "Public read" on congratulations
  for select using (true);

create policy "Service insert" on congratulations
  for insert with check (true);
