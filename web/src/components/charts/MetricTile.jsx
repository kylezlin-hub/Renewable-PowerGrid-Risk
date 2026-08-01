// Stat tile: a headline number with an optional delta-vs-baseline line.
// `tone` colors the delta: 'up' (worse → critical), 'down' (better → good),
// 'flat' (neutral). The arrow points in the direction of change.

export default function MetricTile({ label, value, delta, tone = 'flat' }) {
  const arrow = tone === 'up' ? '▲' : tone === 'down' ? '▼' : '→'
  return (
    <div className="tile">
      <div className="k">{label}</div>
      <div className="v">{value}</div>
      {delta ? (
        <div className={`d ${tone}`}>
          {arrow} {delta} vs baseline
        </div>
      ) : (
        <div className="d flat">baseline</div>
      )}
    </div>
  )
}
