export default function Hero() {
  return (
    <section id="top">
      <span className="pill">ERCOT · 2023–2025 data</span>
      <h1>What happens to the Texas grid<br />as we add more solar and wind?</h1>
      <p className="lead">
        Grid operators must match electricity supply to demand every second of every day.
        Solar and wind make that harder — not because they are unreliable, but because their
        output swings on the clock and the calendar. This tool lets you turn the dials and watch
        the risk respond, using real ERCOT data behind the same math from the research paper.
      </p>
      <p style={{ marginTop: 16 }}>
        Start with the <a className="inline" href="#explainer">explainer</a> to see how a grid
        balances supply and demand, then open the{' '}
        <a className="inline" href="#explorer">scenario explorer</a> to test high-renewable
        futures yourself. A <a className="inline" href="#live">live panel</a> shows the ERCOT grid
        right now.
      </p>
    </section>
  )
}
