import { useMemo, useState } from 'react'
import { buildScenario, groupDays, extractDay, peakSunsetDayIndex } from '../lib/netload.js'
import { fmtGW, fmtMW } from '../lib/format.js'
import LineChart from './charts/LineChart.jsx'

// Educational section: how supply/demand balance works, what "net load" is, and
// why the evening sunset transition is the hard part. A one-day chart (the duck
// curve) responds to a solar-scaling slider so the concept is felt, not just told.

export default function ExplainerGrid({ data }) {
  const days = useMemo(() => groupDays(data), [data])
  const baseline = useMemo(() => buildScenario(data, { solarMult: 1 }), [data])
  const defaultDay = useMemo(() => peakSunsetDayIndex(baseline, days), [baseline, days])

  const [dayIndex, setDayIndex] = useState(defaultDay)
  const [solarMult, setSolarMult] = useState(1)

  const scenario = useMemo(() => buildScenario(data, { solarMult }), [data, solarMult])
  const day = days[Math.min(dayIndex, days.length - 1)]
  const pts = useMemo(() => extractDay(scenario, day.indices), [scenario, day])

  const byHour = Object.fromEntries(pts.map((p) => [p.hour, p]))
  const sunsetRamp =
    byHour[20] && byHour[17] ? byHour[20].netLoad - byHour[17].netLoad : null

  const series = [
    { name: 'Demand (load)', color: 'var(--series-1)', points: pts.map((p) => ({ x: p.hour, y: p.load })) },
    { name: 'Solar output', color: 'var(--series-4)', points: pts.map((p) => ({ x: p.hour, y: p.solar })) },
    { name: 'Net load (what firm plants must serve)', color: 'var(--series-2)', points: pts.map((p) => ({ x: p.hour, y: p.netLoad })) },
  ]

  return (
    <section id="explainer">
      <h2>How a power grid stays balanced</h2>
      <p>
        Electricity is produced and consumed at the same instant. To keep the lights on, grid
        operators continuously match generation to <strong>demand</strong> (the load). Solar and
        wind are <strong>must-take</strong>: when the sun shines or the wind blows, that energy is
        used first. What is left over — demand minus renewable output — is the{' '}
        <strong>net load</strong>, and it is what gas, nuclear, hydro, and batteries have to cover.
      </p>
      <p>
        The challenge is not the average; it is the <strong>ramp</strong> — how fast net load
        changes. On a sunny day, solar floods the grid at noon and then disappears at dusk, right
        as people come home and demand peaks. Firm plants must ramp up thousands of megawatts in a
        few hours. This is the <strong>sunset ramp</strong>, and it is the heart of this study.
      </p>

      <div className="card" style={{ marginTop: 20 }}>
        <div className="chart-title">One day in ERCOT — {day.date}</div>
        <div className="chart-sub">
          Drag the solar slider to see the “duck curve” deepen and the sunset ramp steepen.
        </div>

        <LineChart
          series={series}
          height={340}
          xTicks={[0, 4, 8, 12, 16, 20]}
          xFormat={(h) => `${String(Math.round(h)).padStart(2, '0')}:00`}
          yFormat={(v) => fmtGW(v)}
          yLabel="GW"
          xLabel="Hour of day"
        />

        <div className="controls" style={{ marginTop: 18 }}>
          <div className="control">
            <label>
              <span>Solar output multiplier</span>
              <span className="val">{solarMult.toFixed(1)}×</span>
            </label>
            <input type="range" min="1" max="2.5" step="0.1" value={solarMult}
              onChange={(e) => setSolarMult(parseFloat(e.target.value))} />
            <div className="hint">1.0× = today’s installed solar. Higher = future build-out.</div>
          </div>
          <div className="control">
            <label>
              <span>Day of year</span>
              <span className="val">{day.date}</span>
            </label>
            <input type="range" min="0" max={days.length - 1} step="1" value={dayIndex}
              onChange={(e) => setDayIndex(parseInt(e.target.value, 10))} />
            <div className="hint">Defaults to the summer day with the largest sunset ramp.</div>
          </div>
        </div>

        {sunsetRamp != null && (
          <div className="note">
            Sunset ramp on this day (17:00 → 20:00 net-load change): <strong>{fmtMW(sunsetRamp)}</strong>
            {' '}at {solarMult.toFixed(1)}× solar. Firm generation must rise by this much in three hours.
          </div>
        )}
      </div>
    </section>
  )
}
