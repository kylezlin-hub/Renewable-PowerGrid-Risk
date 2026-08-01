// Faithful JavaScript port of src/metrics.py::compute_risk_metrics, plus the
// sunset-ramp and capacity-exceedance analyses from notebook 04.
// Verified against the Python-exported baseline_metrics.json (see selftest.js).

import { quantile, variance, mean } from './quantile.js'

export const FIXED_THRESHOLD = 6033 // baseline P95 |ramp_1h|, MW
export const TOTAL_RAMP_CAPACITY = 23250 // estimated dispatchable ramp capacity, MW/hr
export const SUNSET_HOURS = [17, 18, 19, 20]
export const SUMMER_MONTHS = [5, 6, 7, 8, 9]

// scenario: output of buildScenario(). fixedThreshold defaults to 6033.
export function computeRiskMetrics(scenario, fixedThreshold = FIXED_THRESHOLD) {
  const { ramp1h, ramp3h, netLoad } = scenario
  const n = netLoad.length

  const abs1h = ramp1h.map((v) => Math.abs(v))
  const abs3h = ramp3h.map((v) => Math.abs(v))

  const threshold = fixedThreshold != null ? fixedThreshold : quantile(abs1h, 0.95)

  // max_ramp_up / max_ramp_down operate on signed ramps.
  let maxUp = -Infinity
  let maxDown = Infinity
  let exceedCount = 0
  const exceedAbs = []
  for (let i = 0; i < n; i++) {
    const r = ramp1h[i]
    if (Number.isNaN(r)) continue
    if (r > 0 && r > maxUp) maxUp = r
    if (r < 0 && r < maxDown) maxDown = r
    if (Math.abs(r) > threshold) {
      exceedCount += 1
      exceedAbs.push(Math.abs(r))
    }
  }

  return {
    max_ramp_up: maxUp === -Infinity ? NaN : maxUp,
    max_ramp_down: maxDown === Infinity ? NaN : maxDown,
    threshold_P95: threshold,
    // pandas (abs>thr).mean(): denominator is the full series length (the NaN
    // first diff compares False), so divide by n, not by the non-NaN count.
    tail_probability: exceedCount / n,
    conditional_tail: exceedAbs.length ? mean(exceedAbs) : NaN,
    p99_ramp_1h: quantile(abs1h, 0.99),
    mean_abs_ramp_1h: mean(abs1h),
    std_abs_ramp_1h: Math.sqrt(variance(abs1h, 1)),
    max_ramp_3h: Math.max(...abs3h.filter((v) => !Number.isNaN(v))),
    p95_ramp_3h: quantile(abs3h, 0.95),
    ramp_variance_1h: variance(ramp1h, 0),
    ramp_variance_3h: variance(ramp3h, 0),
  }
}

// Max daily sunset ramp (NET_LOAD@20 - NET_LOAD@17) and days exceeding 20 GW,
// May-September only. Requires all four sunset hours present in a day.
export function sunsetMetrics(scenario) {
  const byDay = new Map()
  for (let i = 0; i < scenario.n; i++) {
    if (!SUMMER_MONTHS.includes(scenario.month[i])) continue
    if (!SUNSET_HOURS.includes(scenario.hour[i])) continue
    const day = scenario.timestamp[i].slice(0, 10)
    if (!byDay.has(day)) byDay.set(day, {})
    byDay.get(day)[scenario.hour[i]] = scenario.netLoad[i]
  }
  const ramps = []
  for (const hours of byDay.values()) {
    if (SUNSET_HOURS.every((h) => h in hours)) {
      ramps.push(hours[20] - hours[17])
    }
  }
  return {
    max_sunset_ramp: ramps.length ? Math.max(...ramps) : 0,
    days_over_20GW: ramps.filter((r) => r > 20000).length,
    sunset_ramps: ramps,
  }
}

// Hours where |1h ramp| exceeds dispatchable capacity, and the worst shortfall.
export function capacityMetrics(scenario, capacity = TOTAL_RAMP_CAPACITY) {
  let hours = 0
  let maxShortfall = 0
  for (const r of scenario.ramp1h) {
    if (Number.isNaN(r)) continue
    const shortfall = Math.max(Math.abs(r) - capacity, 0)
    if (shortfall > 0) hours += 1
    if (shortfall > maxShortfall) maxShortfall = shortfall
  }
  return { hours_exceeding_capacity: hours, max_shortfall: maxShortfall }
}

// Annual energy penetration = (wind + solar) / load, with multipliers applied.
export function annualPenetration(scenario) {
  let load = 0
  let renew = 0
  for (let i = 0; i < scenario.n; i++) {
    load += scenario.load[i]
    renew += scenario.solarMult * scenario.solar[i] + scenario.windMult * scenario.wind[i]
  }
  return load ? renew / load : NaN
}

// Everything the UI needs, in one call.
export function fullSummary(scenario, capacity = TOTAL_RAMP_CAPACITY) {
  return {
    ...computeRiskMetrics(scenario),
    ...sunsetMetrics(scenario),
    ...capacityMetrics(scenario, capacity),
    annual_penetration: annualPenetration(scenario),
  }
}
