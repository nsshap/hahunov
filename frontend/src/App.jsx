import { useState } from 'react'
import MapView from './components/MapView'
import './App.css'

export default function App() {
  const [tab, setTab] = useState('day')

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <span className="header-date">20 марта 2026</span>
          <h1 className="header-title">Барбара</h1>
        </div>
        <nav className="tabs">
          <button
            className={`tab ${tab === 'day' ? 'tab--active' : ''}`}
            onClick={() => setTab('day')}
          >
            День рождения
          </button>
          <button
            className={`tab ${tab === 'congrats' ? 'tab--active' : ''}`}
            onClick={() => setTab('congrats')}
          >
            Поздравления
          </button>
        </nav>
      </header>

      <main className="main">
        <MapView tab={tab} />
      </main>
    </div>
  )
}
