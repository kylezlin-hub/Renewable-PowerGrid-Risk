// Dev-only self-test: recompute metrics in JS for baseline / 1.5x / 2.0x / 2.5x
// solar and compare against the Python-exported targets in baseline_metrics.json.
// Logs a pass/fail table to the console. This is how we know the JS port of
// src/metrics.py is faithful without running Python in the browser.

import { loadData, loadBaselineMetrics } from './data.js'
import { buildScenario } from './netload.js'
import { fullSummary } from './metrics.js'

const CASES = [
  { key: 'baseline', solarMult: 1.0 },
  { key: 'solar_1_5x', solarMult: 1.5 },
  { key: 'solar_2_0x', solarMult: 2.0 },
  { key: 'solar_2_5x', solarMult: 2.5 },
]

// Continuous metrics: relative tolerance. Counts: must match exactly.
const CONTINUOUS = [
  'max_ramp_up', 'max_ramp_down', 'threshold_P95', 'tail_probability',
  'conditional_tail', 'p99_ramp_1h', 'mean_abs_ramp_1h', 'std_abs_ramp_1h',
  'max_ramp_3h', 'p95_ramp_3h', 'ramp_variance_1h', 'ramp_variance_3h',
  'max_sunset_ramp', 'max_shortfall', 'annual_penetration',
]
const COUNTS = ['days_over_20GW', 'hours_exceeding_capacity']
const RTOL = 1e-6

export async function runSelfTest() {
  try {
    const [data, targets] = await Promise.all([loadData(), loadBaselineMetrics()])
    const rows = []
    let allPass = true

    for (const c of CASES) {
      const scenario = buildScenario(data, { solarMult: c.solarMult, windMult: 1.0 })
      const got = fullSummary(scenario)
      const want = targets[c.key]

      for (const m of CONTINUOUS) {
        const g = got[m]
        const w = want[m]
        const denom = Math.max(Math.abs(w), 1e-9)
        const ok = Math.abs(g - w) / denom < RTOL
        if (!ok) {
          allPass = false
          rows.push({ case: c.key, metric: m, js: g, python: w, status: 'FAIL' })
        }
      }
      for (const m of COUNTS) {
        const ok = got[m] === want[m]
        if (!ok) {
          allPass = false
          rows.push({ case: c.key, metric: m, js: got[m], python: want[m], status: 'FAIL' })
        }
      }
    }

    if (allPass) {
      console.log(
        '%c[self-test] JS math matches Python export across all 4 scenarios ✓',
        'color:#0ca30c;font-weight:bold',
      )
    } else {
      console.error('[self-test] Mismatches vs Python export:')
      console.table(rows)
    }
  } catch (e) {
    console.warn('[self-test] skipped:', e.message)
  }
}
