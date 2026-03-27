import './MediaModal.css'

export default function MediaModal({ pin, tab, onClose }) {
  const isVideo = pin.media_type === 'video'

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        <button className="modal-close" onClick={onClose}>✕</button>

        {/* Заголовок */}
        <div className="modal-header">
          <span className="modal-location">
            {pin.location || 'Неизвестное место'}
          </span>
          {tab === 'congrats' && pin.name && (
            <span className="modal-name">{pin.name}</span>
          )}
          {tab === 'congrats' && pin.relation && (
            <span className="modal-relation">{pin.relation}</span>
          )}
        </div>

        {/* Медиа */}
        <div className="modal-media">
          {isVideo ? (
            <video
              src={pin.media_url}
              controls
              autoPlay
              playsInline
              className="modal-video"
            />
          ) : (
            <img
              src={pin.media_url}
              alt={pin.location}
              className="modal-image"
            />
          )}
        </div>

        {/* Текст */}
        {pin.caption && (
          <p className="modal-caption">{pin.caption}</p>
        )}

        {/* Непрошеный совет (только поздравления) */}
        {tab === 'congrats' && pin.advice && (
          <div className="modal-advice">
            <span className="modal-advice-label">непрошеный совет</span>
            <p>{pin.advice}</p>
          </div>
        )}

      </div>
    </div>
  )
}
