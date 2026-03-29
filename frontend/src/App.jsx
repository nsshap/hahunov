import { useState } from 'react'
import MapView from './components/MapView'
import './App.css'

export default function App() {
  const [tab, setTab] = useState('day')

  return (
    <div className="app">
      <header className="header">
        <h1 className="header-title">Варвара</h1>
        <nav className="tabs">
          <button
            className={`tab ${tab === 'day' ? 'tab--active' : ''}`}
            onClick={() => setTab('day')}
          >
            <span className="tab__icon">🌍</span>
            <span className="tab__content">
              <span className="tab__label">20 марта 2026</span>
              <span className="tab__sub">Мир в день рождения</span>
            </span>
          </button>
          <button
            className={`tab ${tab === 'congrats' ? 'tab--active' : ''}`}
            onClick={() => setTab('congrats')}
          >
            <span className="tab__icon">💌</span>
            <span className="tab__content">
              <span className="tab__label">Поздравления</span>
              <span className="tab__sub">От тех, кто тебя любит</span>
            </span>
          </button>
        </nav>
      </header>

      <main className="main">
        <MapView tab={tab} />
      </main>
    </div>
  )
}
