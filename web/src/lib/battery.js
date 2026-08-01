// Battery as a ramp-smoothing factor (matches the project's modeling choice:
// storage reduces net-load ramp rates rather than adding bulk energy).
//
// Simple state-of-charge model: each hour, the battery pushes back against the
// hour-to-hour change in net load by up to `powerMW`, limited by its energy
// budget (powerMW * durationH). When net load is ramping UP, the battery
// discharges (lowering net load); when ramping DOWN, it charges (raising net
// load). This clips large ramps in both directions.
//
// This is an intentionally approximate operational proxy, not an optimized
// dispatch — surface it in the UI as such.

export function applyBattery(netLoad, powerMW, durationH) {
  const energyCap = powerMW * durationH // MWh
  if (energyCap <= 0 || powerMW <= 0) return netLoad.slice()

  const out = new Array(netLoad.length)
  let soc = energyCap / 2 // start half-charged
  out[0] = netLoad[0]

  for (let i = 1; i < netLoad.length; i++) {
    const rawRamp = netLoad[i] - out[i - 1]
    if (rawRamp > 0) {
      // Net load rising: discharge to shave the ramp.
      const discharge = Math.min(powerMW, rawRamp, soc)
      out[i] = netLoad[i] - discharge
      soc -= discharge
    } else if (rawRamp < 0) {
      // Net load falling: charge to fill the trough.
      const charge = Math.min(powerMW, -rawRamp, energyCap - soc)
      out[i] = netLoad[i] + charge
      soc += charge
    } else {
      out[i] = netLoad[i]
    }
  }
  return out
}
