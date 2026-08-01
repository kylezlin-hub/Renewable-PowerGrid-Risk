// Scenario construction: apply solar/wind multipliers to the base 2025 data and
// recompute net load. Mirrors notebook 04's scenario loop:
//   NET_LOAD = ERCOT.LOAD - m_solar * ERCOT.PVGR.GEN - m_wind * ERCOT.WIND.GEN
// Load is held constant; only renewables are scaled.

import { applyBattery } from './battery.js'

// First-difference over `lag` periods; first `lag` entries are NaN (pandas .diff).
export function diff(arr, lag = 1) {
  const out = new Array(arr.length)
  for (let i = 0; i < arr.length; i++) {
    out[i] = i < lag ? NaN : arr[i] - arr[i - lag]
  }
  return out
}

// Build a scenario. `data` is the parsed ercot_2025.json payload.
// opts: { solarMult, windMult, batteryPowerMW, batteryDurationH }
export function buildScenario(data, opts = {}) {
  const {
    solarMult = 1,
    windMult = 1,
    batteryPowerMW = 0,
    batteryDurationH = 0,
  } = opts

  const n = data.load.length
  let netLoad = new Array(n)
  for (let i = 0; i < n; i++) {
    netLoad[i] = data.load[i] - solarMult * data.solar[i] - windMult * data.wind[i]
  }

  const netLoadRaw = netLoad
  if (batteryPowerMW > 0 && batteryDurationH > 0) {
    netLoad = applyBattery(netLoad, batteryPowerMW, batteryDurationH)
  }

  return {
    n,
    hour: data.hour,
    month: data.month,
    timestamp: data.timestamp,
    load: data.load,
    solar: data.solar,
    wind: data.wind,
    solarMult,
    windMult,
    netLoad,
    netLoadRaw, // before battery smoothing (for comparison)
    ramp1h: diff(netLoad, 1),
    ramp3h: diff(netLoad, 3),
  }
}

// Group row indices by calendar day (robust to any hour alignment / gaps).
// Returns [{ date: 'YYYY-MM-DD', month, indices: number[] }] in chronological order.
export function groupDays(data) {
  const map = new Map()
  for (let i = 0; i < data.timestamp.length; i++) {
    const date = data.timestamp[i].slice(0, 10)
    if (!map.has(date)) map.set(date, { date, month: data.month[i], indices: [] })
    map.get(date).indices.push(i)
  }
  return Array.from(map.values())
}

// Extract one day's hourly points for the duck-curve view, given the row indices.
export function extractDay(scenario, indices) {
  return indices
    .map((i) => ({
      hour: scenario.hour[i],
      load: scenario.load[i],
      solar: scenario.solar[i] * scenario.solarMult,
      wind: scenario.wind[i] * scenario.windMult,
      netLoad: scenario.netLoad[i],
    }))
    .sort((a, b) => a.hour - b.hour)
}

// Index of the summer day with the largest baseline sunset ramp (NL@20 - NL@17).
export function peakSunsetDayIndex(scenario, days) {
  let best = 0, bestVal = -Infinity
  days.forEach((day, di) => {
    if (![5, 6, 7, 8, 9].includes(day.month)) return
    const byHour = {}
    for (const i of day.indices) byHour[scenario.hour[i]] = scenario.netLoad[i]
    if (17 in byHour && 20 in byHour) {
      const v = byHour[20] - byHour[17]
      if (v > bestVal) { bestVal = v; best = di }
    }
  })
  return best
}
