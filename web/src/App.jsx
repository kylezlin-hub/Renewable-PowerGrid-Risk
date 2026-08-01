import { useEffect, useState } from 'react'
import { loadData } from './lib/data.js'
import Hero from './components/Hero.jsx'
import ExplainerGrid from './components/ExplainerGrid.jsx'
import ScenarioExplorer from './components/ScenarioExplorer.jsx'
import LiveGridPanel from './components/LiveGridPanel.jsx'
import Findings from './components/Findings.jsx'
import About from './components/About.jsx'

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'auto')

  useEffect(() => {
    loadData().then(setData).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'auto') root.removeAttribute('data-theme')
    else root.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  function cycleTheme() {
    setTheme((t) => (t === 'auto' ? 'light' : t === 'light' ? 'dark' : 'auto'))
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand">⚡ ERCOT Grid Risk Simulator</span>
        <nav>
          <a href="#explorer">Explorer</a>
          <a href="#explainer">Explainer</a>
          <a href="#live">Live grid</a>
          <a href="#findings">Findings</a>
          <a href="#about">Method</a>
          <a className="btn-link" href="https://kylezlin-hub.github.io/" target="_blank" rel="noreferrer">
            My Personal Page ↗
          </a>
          <button className="theme-toggle" onClick={cycleTheme} title="Toggle color theme">
            {theme === 'auto' ? 'Theme: Auto' : theme === 'light' ? 'Theme: Light' : 'Theme: Dark'}
          </button>
        </nav>
      </header>

      <Hero />

      {error && (
        <section>
          <div className="card">
            <h3>Couldn’t load the dataset</h3>
            <p>{error}. Make sure <code>public/data/ercot_2025.json</code> exists (run
            {' '}<code>npm run export-data</code>).</p>
          </div>
        </section>
      )}

      {!data && !error && (
        <section><div className="card">Loading ERCOT 2025 dataset…</div></section>
      )}

      {data && (
        <>
          <ScenarioExplorer data={data} />
          <ExplainerGrid data={data} />
        </>
      )}

      <LiveGridPanel />

      {data && <Findings />}
      <About />

      <div className="footer">
        Independent research · ERCOT 2023–2025 data · Live data from EIA. All figures are estimates
        for education and research, not operational guidance.
      </div>
    </div>
  )
}
