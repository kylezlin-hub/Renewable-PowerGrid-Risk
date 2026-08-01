import { useEffect, useState } from 'react'
import { hasKey, fetchDemand, fetchFuelMix } from '../lib/eia.js'
import { fmtGW, fmtPct, fmtMW } from '../lib/format.js'
import Donut from './charts/Donut.jsx'

// Live "current ERCOT grid" panel. Degrades gracefully when the API key is
// missing or the request fails — the rest of the site works regardless.

export default function LiveGridPanel() {
  const [state, setState] = useState({ status: 'loading' })

  useEffect(() => {
    if (!hasKey()) {
      setState({ status: 'nokey' })
      return
    }
    let cancelled = false
    ;(async () => {
      try {
        const [demand, mix] = await Promise.all([fetchDemand(24), fetchFuelMix()])
        if (cancelled) return
        const last = demand[demand.length - 1]
        const prev = demand[demand.length - 2]
        const ramp = last && prev ? last.value - prev.value : null
        setState({ status: 'ok', demand, mix, last, ramp })
      } catch (e) {
        if (!cancelled) setState({ status: 'error', message: e.message })
      }
    })()
    return () => { cancelled = true }
  }, [])

  return (
    <section id="live">
      <h2>The ERCOT grid right now</h2>
      <p>
        Live data from the U.S. Energy Information Administration (EIA) for the ERCOT balancing
        authority. This is the real grid the scenario explorer above is modeling.
      </p>

      {state.status === 'loading' && <div className="card">Loading live grid data…</div>}

      {state.status === 'nokey' && (
        <div className="card">
          <h3>Live panel not configured</h3>
          <p>
            Add a free EIA API key to enable this panel. Get one at{' '}
            <a className="inline" href="https://www.eia.gov/opendata/register.php" target="_blank" rel="noreferrer">
              eia.gov/opendata
            </a>{' '}
            and set <code>VITE_EIA_API_KEY</code> (see <code>.env.example</code>). The rest of the
            simulator works without it.
          </p>
        </div>
      )}

      {state.status === 'error' && (
        <div className="card">
          <h3>Live data unavailable</h3>
          <p>Couldn’t reach the EIA API ({state.message}). The historical simulator above is unaffected.</p>
        </div>
      )}

      {state.status === 'ok' && (
        <div className="grid cols-2" style={{ marginTop: 16 }}>
          <div className="card">
            <div className="tiles" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="tile">
                <div className="k">Current demand</div>
                <div className="v">{fmtGW(state.last.value)}</div>
                <div className="d flat">{formatPeriod(state.last.period)}</div>
              </div>
              <div className="tile">
                <div className="k">Renewable share of generation</div>
                <div className="v">{fmtPct(state.mix?.renewableShare ?? NaN, 0)}</div>
                <div className="d flat">wind + solar + hydro</div>
              </div>
              <div className="tile">
                <div className="k">Last 1-hour demand change</div>
                <div className="v">{state.ramp != null ? fmtMW(Math.abs(state.ramp)) : '—'}</div>
                <div className={`d ${state.ramp > 0 ? 'up' : 'down'}`}>
                  {state.ramp > 0 ? '▲ rising' : '▼ falling'}
                </div>
              </div>
              <div className="tile">
                <div className="k">Total generation</div>
                <div className="v">{fmtGW(state.mix?.total ?? NaN)}</div>
                <div className="d flat">all fuels</div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="chart-title">Current generation mix</div>
            <div className="chart-sub">{state.mix ? formatPeriod(state.mix.period) : ''}</div>
            {state.mix && (
              <Donut
                segments={state.mix.segments}
                centerTop={fmtPct(state.mix.renewableShare, 0)}
                centerBottom="renewable"
              />
            )}
          </div>
        </div>
      )}

      <div className="note">
        Source: EIA Open Data API v2, ERCOT balancing authority (respondent code ERCO). Values are
        typically delayed by a few hours.
      </div>
    </section>
  )
}

function formatPeriod(p) {
  if (!p) return ''
  // EIA hourly period looks like "2026-07-30T14"
  const [date, hour] = p.split('T')
  return `${date} ${hour}:00 (hour-ending, local)`
}
