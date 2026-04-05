import { useEffect, useState, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet'
import L from 'leaflet'
import { supabase } from '../lib/supabase'
import MediaModal from './MediaModal'
import './MapView.css'

// Кастомные маркеры
function makeIcon(color) {
  return L.divIcon({
    className: '',
    html: `<div class="pin pin--${color}"><div class="pin__dot"></div><div class="pin__pulse"></div></div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  })
}

function makeIconCount(color, count) {
  return L.divIcon({
    className: '',
    html: `<div class="pin pin--${color}"><div class="pin__dot"></div><div class="pin__pulse"></div><div class="pin__count">${count}</div></div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  })
}

const iconRose = makeIcon('rose')
const iconGold = makeIcon('gold')

function MapController({ pins }) {
  const map = useMap()
  useEffect(() => {
    if (pins.length === 0) return
    const valid = pins.filter(p => p.lat && p.lng)
    if (valid.length === 0) return
    const bounds = L.latLngBounds(valid.map(p => [p.lat, p.lng]))
    map.fitBounds(bounds, { padding: [60, 60], maxZoom: 5 })
  }, [pins])
  return null
}

export default function MapView({ tab }) {
  const [dayPins, setDayPins]   = useState([])
  const [congrats, setCongrats] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const [{ data: d }, { data: c }] = await Promise.all([
        supabase.from('day_pins').select('*').not('lat', 'is', null),
        supabase.from('congratulations').select('*').not('lat', 'is', null),
      ])
      setDayPins(d || [])
      setCongrats(c || [])
      setLoading(false)
    }
    load()
  }, [])

  // Группируем day_pins по локации (одинаковые lat/lng → один пин)
  const groupedDayPins = useMemo(() => {
    const groups = {}
    dayPins.forEach(p => {
      const key = `${p.lat},${p.lng}`
      if (!groups[key]) groups[key] = { lat: p.lat, lng: p.lng, items: [] }
      groups[key].items.push(p)
    })
    return Object.values(groups)
  }, [dayPins])

  // Группируем поздравления по локации с округлением до 0.1° (~11 км)
  // чтобы GPS-координата и геокодированный адрес одного города попадали в один пин
  const groupedCongrats = useMemo(() => {
    const round = x => Math.floor(x * 10) / 10
    const groups = {}
    congrats.forEach(c => {
      const key = `${round(c.lat)},${round(c.lng)}`
      if (!groups[key]) groups[key] = { lat: c.lat, lng: c.lng, items: [] }
      groups[key].items.push(c)
    })
    return Object.values(groups)
  }, [congrats])

  const isDay = tab === 'day'

  return (
    <div className="map-wrap">
      {loading && (
        <div className="map-loading">
          <span>Загружаем карту…</span>
        </div>
      )}

      <MapContainer
        center={[30, 10]}
        zoom={2}
        zoomControl={true}
        className="map"
        minZoom={2}
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        />
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
          attribution=""
        />

        <MapController pins={isDay ? dayPins : congrats} />

        {isDay && groupedDayPins.map((group, i) => (
          <Marker
            key={i}
            position={[group.lat, group.lng]}
            icon={group.items.length > 1
              ? makeIconCount('rose', group.items.length)
              : iconRose}
            eventHandlers={{ click: () => setSelected(group.items) }}
          />
        ))}

        {!isDay && groupedCongrats.map((group, i) => (
          <Marker
            key={i}
            position={[group.lat, group.lng]}
            icon={group.items.length > 1
              ? makeIconCount('gold', group.items.length)
              : iconGold}
            eventHandlers={{ click: () => setSelected(group.items) }}
          />
        ))}
      </MapContainer>

      {!isDay && congrats.length === 0 && !loading && (
        <div className="map-empty">
          <p>Поздравления скоро появятся здесь</p>
          <span>Поделитесь ботом с гостями</span>
        </div>
      )}

      {selected && (
        <MediaModal items={selected} tab={tab} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}
