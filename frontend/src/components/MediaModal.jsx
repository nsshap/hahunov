import './MediaModal.css'

export default function MediaModal({ items, tab, onClose }) {
  const firstPin = items[0]
  const location = firstPin?.location || firstPin?.city || 'Неизвестное место'

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        <button className="modal-close" onClick={onClose}>✕</button>

        {/* Заголовок */}
        <div className="modal-header">
          <span className="modal-location">{location}</span>
        </div>

        {/* Лента медиа */}
        <div className="modal-videos">
          {items.map((item, i) => {
            const videoUrls = item.video_urls?.length
              ? item.video_urls
              : item.video_url
              ? [item.video_url]
              : []
            const audioUrls = item.audio_urls ?? []

            return (
              <div key={item.id ?? i} className="modal-media-item">
                {/* day_pins */}
                {tab === 'day' && (
                  item.media_type === 'video'
                    ? <video src={item.media_url} controls playsInline className="modal-video" />
                    : <img src={item.media_url} alt={location} className="modal-image" />
                )}

                {/* congratulations */}
                {tab === 'congrats' && (
                  <>
                    {videoUrls.map((url, j) => (
                      <video key={j} src={url} controls playsInline className="modal-video" />
                    ))}
                    {audioUrls.map((url, j) => (
                      <audio key={j} src={url} controls className="modal-audio" />
                    ))}
                  </>
                )}

                {/* Подписи */}
                {tab === 'day' && item.caption && (
                  <p className="modal-caption">{item.caption}</p>
                )}
                {tab === 'congrats' && (
                  <div className="modal-congrats-meta">
                    {item.name && <span className="modal-name">{item.name}</span>}
                    {item.message && <p className="modal-caption">{item.message}</p>}
                    {item.advice && (
                      <div className="modal-advice">
                        <span className="modal-advice-label">непрошеный совет</span>
                        <p>{item.advice}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

      </div>
    </div>
  )
}
