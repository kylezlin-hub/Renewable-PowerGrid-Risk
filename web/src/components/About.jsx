export default function About() {
  return (
    <section id="about">
      <h2>Method & data</h2>
      <p>
        The scenario explorer holds 2025 demand fixed and scales solar and wind output by
        multipliers, then recomputes net load hour by hour:
      </p>
      <p style={{ fontFamily: 'ui-monospace, monospace', color: 'var(--text-primary)', fontSize: 14 }}>
        net load = demand − (solar × m<sub>solar</sub>) − (wind × m<sub>wind</sub>)
      </p>
      <p>
        Ramps are hour-to-hour changes in net load. Extreme-ramp <strong>tail probability</strong> is
        the share of hours whose ramp exceeds a fixed baseline threshold (6,033 MW, the 2025 95th
        percentile), so scenarios stay comparable. The <strong>sunset ramp</strong> is the 17:00→20:00
        net-load change on summer days. <strong>Capacity exceedance</strong> counts hours whose ramp
        beats an estimated dispatchable ramp capacity — 23,250 MW/hr by default, and adjustable in the
        explorer because it is an assumption, not a measured value.
      </p>
      <p>
        All computation runs in your browser. The JavaScript metrics are validated against the
        project’s Python code (<code>src/metrics.py</code>): a build-time self-test confirms they
        match to floating-point tolerance across every scenario.
      </p>

      <div className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>Data sources</h3>
          <p style={{ fontSize: 14 }}>
            Historical: ERCOT hourly load, wind, and solar output, 2023–2025.<br />
            Live: U.S. Energy Information Administration (EIA) Open Data API v2, ERCOT balancing
            authority.
          </p>
        </div>
        <div className="card">
          <h3>Limitations</h3>
          <p style={{ fontSize: 14 }}>
            Scenarios scale historical output multiplicatively (preserving weather shape, not new
            siting). Battery dispatch is an approximate ramp-smoothing proxy. The capacity threshold
            is an estimate. Results describe risk, and do not prove any specific outcome.
          </p>
        </div>
      </div>

      <p className="note">
        Part of an independent research project on renewable-penetration grid risk in ERCOT.
        Built as a static site; source and full methodology live in the project repository.
      </p>
    </section>
  )
}
