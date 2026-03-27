-- Запустить в Supabase Dashboard → SQL Editor
-- Переносим video_url (text) → video_urls (text[])

ALTER TABLE congratulations
  ADD COLUMN IF NOT EXISTS video_urls text[];

-- Перенести старые данные: каждый старый video_url → массив из одного элемента
UPDATE congratulations
  SET video_urls = ARRAY[video_url]
  WHERE video_url IS NOT NULL AND (video_urls IS NULL OR video_urls = '{}');

ALTER TABLE congratulations
  DROP COLUMN IF EXISTS video_url;
