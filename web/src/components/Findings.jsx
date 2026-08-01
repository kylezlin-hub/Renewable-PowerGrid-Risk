import MetricTile from './charts/MetricTile.jsx'

// Static summary of the paper's headline (verified) results — the same numbers
// the explorer reproduces at 2.5× solar.

export default function Findings() {
  return (
    <section id="findings">
      <h2>What the data shows</h2>
      <p>
        Scaling ERCOT’s 2025 solar output toward a high-penetration future (2.5×, about 57%
        renewable energy) does not raise ramping risk in proportion — it accelerates. The stress
        concentrates in the evening sunset window, and beyond roughly 2× solar the grid begins to
        cross the ramping capability of today’s dispatchable fleet.
      </p>

      <div className="tiles" style={{ marginTop: 16 }}>
        <MetricTile label="Max sunset ramp" value="57,545 MW" delta="≈3.0× baseline (19,421)" tone="up" />
        <MetricTile label="Tail probability" value="20.7%" delta="+15.7 pp vs 5.0%" tone="up" />
        <MetricTile label="P99 1-hour ramp" value="27,037 MW" delta="+170% vs 10,003" tone="up" />
        <MetricTile label="Hours over capacity / yr" value="240" delta="from 0" tone="up" />
        <MetricTile label="Onset of shortfalls" value="~2.0× solar" delta="≈50% penetration" tone="flat" />
        <MetricTile label="Weather vs. solar effect" value="Solar dominates" delta="weather 2nd-order" tone="flat" />
      </div>

      <p style={{ marginTop: 20 }}>
        A weather-robustness check (perturbing load with a 2023 heat-year profile, then amplifying
        that effect up to 3×) moves the risk metrics only slightly compared with the solar-driven
        jump — so solar penetration, not weather variability, is the first-order driver of the
        nonlinear escalation seen here.
      </p>
      <p className="note">
        These are the paper’s verified figures. The explorer above recomputes them live from the
        same data, so you can confirm the 2.5×-solar column yourself.
      </p>
    </section>
  )
}
