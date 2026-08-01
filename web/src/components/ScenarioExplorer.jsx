import { useMemo, useState } from 'react'
import { buildScenario } from '../lib/netload.js'
import { fullSummary, computeRiskMetrics, sunsetMetrics, capacityMetrics, annualPenetration } from '../lib/metrics.js'
import { fmtMW, fmtGW, fmtPct, fmtInt, fmtDelta } from '../lib/format.js'
import LineChart from './charts/LineChart.jsx'
import MetricTile from './charts/MetricTile.jsx'

const N_WORST = 600 // hours shown on the duration curve

function sortedAbsRamp(ramp1h, k = N_WORST) {
  const abs = ramp1h.filter((v) => !Number.isNaN(v)).map(Math.abs).sort((a, b) => b - a)
  return abs.slice(0, k).map((y, x) => ({ x, y }))
}

export default function ScenarioExplorer({ data }) {
  const [solarMult, setSolarMult] = useState(2.0)
  const [windMult, setWindMult] = useState(1.0)
  const [batteryPowerMW, setBatteryPowerMW] = useState(0)
  const [batteryDurationH, setBatteryDurationH] = useState(4)
  const [capacity, setCapacity] = useState(23250)

  const baseSummary = useMemo(() => {
    const s = buildScenario(data, { solarMult: 1, windMult: 1 })
    return { summary: fullSummary(s, capacity), ramp: s.ramp1h }
  }, [data, capacity])

  const scen = useMemo(
    () => buildScenario(data, { solarMult, windMult, batteryPowerMW, batteryDurationH }),
    [data, solarMult, windMult, batteryPowerMW, batteryDurationH],
  )
  const summary = useMemo(() => ({
    ...computeRiskMetrics(scen),
    ...sunsetMetrics(scen),
    ...capacityMetrics(scen, capacity),
    annual_penetration: annualPenetration(scen),
  }), [scen, capacity])

  const b = baseSummary.summary

  const durationSeries = useMemo(() => ([
    { name: 'Baseline (today)', color: 'var(--series-1)', points: sortedAbsRamp(baseSummary.ramp) },
    { name: 'Your scenario', color: 'var(--series-2)', points: sortedAbsRamp(scen.ramp1h) },
  ]), [baseSummary.ramp, scen.ramp1h])

  const tiles = [
    { label: 'Renewable penetration', value: fmtPct(summary.annual_penetration),
      delta: fmtDelta(summary.annual_penetration - b.annual_penetration, 'pct'), tone: 'flat' },
    { label: 'Tail probability (extreme-ramp hours)', value: fmtPct(summary.tail_probability),
      delta: fmtDelta(summary.tail_probability - b.tail_probability, 'pct'),
      tone: toneUpWorse(summary.tail_probability, b.tail_probability) },
    { label: 'Max sunset ramp (17–20h)', value: fmtMW(summary.max_sunset_ramp),
      delta: fmtDelta(summary.max_sunset_ramp - b.max_sunset_ramp, 'mw'),
      tone: toneUpWorse(summary.max_sunset_ramp, b.max_sunset_ramp) },
    { label: 'P99 1-hour ramp', value: fmtMW(summary.p99_ramp_1h),
      delta: fmtDelta(summary.p99_ramp_1h - b.p99_ramp_1h, 'mw'),
      tone: toneUpWorse(summary.p99_ramp_1h, b.p99_ramp_1h) },
    { label: 'Hours exceeding ramp capacity / yr', value: fmtInt(summary.hours_exceeding_capacity),
      delta: fmtDelta(summary.hours_exceeding_capacity - b.hours_exceeding_capacity, 'int'),
      tone: toneUpWorse(summary.hours_exceeding_capacity, b.hours_exceeding_capacity) },
    { label: 'Max ramp shortfall', value: fmtMW(summary.max_shortfall),
      delta: fmtDelta(summary.max_shortfall - b.max_shortfall, 'mw'),
      tone: toneUpWorse(summary.max_shortfall, b.max_shortfall) },
  ]

  return (
    <section id="explorer">
      <h2>Scenario explorer</h2>
      <p>
        Scale solar and wind, add battery storage, and watch net-load ramping risk respond. Every
        number is computed live in your browser from ERCOT’s 2025 hourly data, using the same risk
        metrics as the paper. “Baseline” is 2025 as it actually happened.
      </p>

      <div className="grid cols-2" style={{ marginTop: 20 }}>
        <div className="card">
          <h3>Controls</h3>
          <div className="controls">
            <Slider label="Solar multiplier" val={solarMult} unit="×" min={0.5} max={2.5} step={0.1}
              onChange={setSolarMult} hint="Scales 2025 solar output. 2.0× ≈ 51% renewable penetration." />
            <Slider label="Wind multiplier" val={windMult} unit="×" min={0.5} max={2.0} step={0.1}
              onChange={setWindMult} hint="Scales 2025 wind output." />
            <Slider label="Battery power" val={batteryPowerMW} unit=" MW" min={0} max={15000} step={500}
              onChange={setBatteryPowerMW} hint="Storage smooths ramps (approximate model)." fmt={fmtInt} />
            <Slider label="Battery duration" val={batteryDurationH} unit=" h" min={0} max={8} step={1}
              onChange={setBatteryDurationH} hint="Hours of energy at rated power." />
            <Slider label="Dispatchable ramp capacity" val={capacity} unit=" MW/hr" min={18000} max={28000} step={250}
              onChange={setCapacity} hint="An assumption (paper uses 23,250). Adjust to test sensitivity." fmt={fmtInt} />
          </div>
        </div>

        <div className="card">
          <div className="chart-title">Ramping duration curve — worst {N_WORST} hours</div>
          <div className="chart-sub">
            How many hours per year the 1-hour ramp exceeds what firm plants can deliver.
          </div>
          <LineChart
            series={durationSeries}
            height={300}
            markers={false}
            xTicks={[0, 100, 200, 300, 400, 500, 600]}
            xFormat={(v) => fmtInt(v)}
            yFormat={(v) => fmtGW(v)}
            yLabel="Required ramp (GW/hr)"
            xLabel="Hours per year (sorted by ramp size)"
            refLines={[{ y: capacity, label: `capacity ${fmtInt(capacity)} MW/hr`, color: 'var(--status-critical)' }]}
          />
          <div className="note">
            Where “your scenario” rises above the dashed capacity line, the grid faces a ramping
            shortfall it cannot meet with today’s fleet.
          </div>
        </div>
      </div>

      <h3 style={{ marginTop: 28 }}>Risk metrics vs. baseline</h3>
      <div className="tiles" style={{ marginTop: 12 }}>
        {tiles.map((t, i) => <MetricTile key={i} {...t} />)}
      </div>

      <div className="note">
        Battery is modeled as a ramp-smoothing resource (it shaves hour-to-hour swings up to its
        rated power, limited by its energy budget), not as bulk generation — matching the paper’s
        treatment. The capacity line is an estimate; use its slider to see how much the
        “hours exceeding capacity” result depends on that assumption.
      </div>
    </section>
  )
}

function toneUpWorse(v, base) {
  if (v > base + 1e-9) return 'up'
  if (v < base - 1e-9) return 'down'
  return 'flat'
}

function Slider({ label, val, unit, min, max, step, onChange, hint, fmt }) {
  const shown = fmt ? fmt(val) : val.toFixed(step < 1 ? 1 : 0)
  return (
    <div className="control">
      <label>
        <span>{label}</span>
        <span className="val">{shown}{unit}</span>
      </label>
      <input type="range" min={min} max={max} step={step} value={val}
        onChange={(e) => onChange(parseFloat(e.target.value))} />
      {hint && <div className="hint">{hint}</div>}
    </div>
  )
}
