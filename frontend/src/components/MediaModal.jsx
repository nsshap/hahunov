import { useState } from 'react'
import './MediaModal.css'

export default function MediaModal({ items, tab, onClose }) {
  const [idx, setIdx] = useState(0)
  const pin = items[idx]
  const total = items.length

  // Совместимость: старые записи имеют video_url, новые — video_urls[]
  const videoUrls = pin.video_urls?.length
    ? pin.video_urls
    : pin.video_url
    ? [pin.video_url]
    : []
  const audioUrls = pin.audio_urls ?? []

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        <button className="modal-close" onClick={onClose}>✕</button>

        {/* Заголовок */}
        <div className="modal-header">
          <span className="modal-location">
            {pin.location || pin.city || 'Неизвестное место'}
          </span>
          {tab === 'congrats' && pin.name && (
            <span className="modal-name">{pin.name}</span>
          )}
          {total > 1 && (
            <span className="modal-count">{idx + 1} / {total}</span>
          )}
        </div>

        {/* Медиа */}
        {tab === 'day' ? (
          <div className="modal-media">
            {pin.media_type === 'video' ? (
              <video src={pin.media_url} controls autoPlay playsInline className="modal-video" />
            ) : (
              <img src={pin.media_url} alt={pin.location} className="modal-image" />
            )}
          </div>
        ) : (
          <div className="modal-videos">
            {videoUrls.map((url, i) => (
              <video key={i} src={url} controls playsInline className="modal-video" />
            ))}
            {audioUrls.map((url, i) => (
              <audio key={i} src={url} controls className="modal-audio" />
            ))}
          </div>
        )}

        {/* Текстовое поздравление */}
        {tab === 'congrats' && pin.message && (
          <p className="modal-caption">{pin.message}</p>
        )}

        {/* caption для day_pins */}
        {tab === 'day' && pin.caption && (
          <p className="modal-caption">{pin.caption}</p>
        )}

        {/* Непрошеный совет */}
        {tab === 'congrats' && pin.advice && (
          <div className="modal-advice">
            <span className="modal-advice-label">непрошеный совет</span>
            <p>{pin.advice}</p>
          </div>
        )}

        {/* Навигация между поздравлениями */}
        {total > 1 && (
          <div className="modal-nav">
            <button
              className="modal-nav-btn"
              onClick={() => setIdx(i => Math.max(0, i - 1))}
              disabled={idx === 0}
            >←</button>
            <button
              className="modal-nav-btn"
              onClick={() => setIdx(i => Math.min(total - 1, i + 1))}
              disabled={idx === total - 1}
            >→</button>
          </div>
        )}

      </div>
    </div>
  )
}
