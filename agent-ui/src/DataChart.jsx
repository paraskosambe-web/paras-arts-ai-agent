const palette = ["#f0a64e", "#e57c39", "#d45d52", "#bb75c8", "#708ce8", "#5ab5a0", "#c5b65c"];

function formatValue(value, currency) {
  if (currency === "INR") {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);
  }
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 }).format(value);
}

export default function DataChart({ chart }) {
  const rows = Array.isArray(chart.data) ? chart.data : [];
  if (!rows.length) return null;

  const max = Math.max(...rows.map((row) => Number(row.value) || 0), 1);
  const total = rows.reduce((sum, row) => sum + (Number(row.value) || 0), 0);

  if (chart.type === "donut") {
    let cursor = 0;
    const gradient = rows.map((row, index) => {
      const portion = total > 0 ? (Math.max(0, Number(row.value) || 0) / total) * 100 : 0;
      const start = cursor;
      cursor += portion;
      return `${palette[index % palette.length]} ${start}% ${cursor}%`;
    }).join(", ");

    return (
      <section className="chart-card" aria-label={chart.title}>
        <div className="chart-heading">
          <div>
            <span className="chart-eyebrow">DATABASE BREAKDOWN</span>
            <h3>{chart.title}</h3>
          </div>
          <span className="chart-total">{formatValue(total, chart.currency)} <small>total</small></span>
        </div>
        <div className="donut-layout">
          <div className="donut-visual" style={{ background: `conic-gradient(${gradient})` }}>
            <div className="donut-center"><strong>{formatValue(total, chart.currency)}</strong><span>{chart.value_label}</span></div>
          </div>
          <div className="chart-legend">
            {rows.map((row, index) => (
              <div className="legend-row" key={`${row.label}-${index}`}>
                <span className="legend-name"><i style={{ background: palette[index % palette.length] }} />{row.label}</span>
                <strong>{formatValue(Number(row.value) || 0, chart.currency)}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (chart.type === "line") {
    const points = rows.map((row, index) => {
      const x = rows.length === 1 ? 50 : 8 + (index / (rows.length - 1)) * 84;
      const y = 74 - ((Number(row.value) || 0) / max) * 62;
      return { x, y, ...row };
    });
    const path = points.map((point, index) => `${index ? "L" : "M"}${point.x},${point.y}`).join(" ");
    return (
      <section className="chart-card" aria-label={chart.title}>
        <div className="chart-heading">
          <div><span className="chart-eyebrow">TREND</span><h3>{chart.title}</h3></div>
          <span className="chart-total">{formatValue(total, chart.currency)} <small>in range</small></span>
        </div>
        <div className="line-chart-wrap">
          <svg className="line-chart" viewBox="0 0 100 84" preserveAspectRatio="none" role="img" aria-label={chart.title}>
            <defs><linearGradient id="lineFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#efa451" stopOpacity=".28" /><stop offset="100%" stopColor="#efa451" stopOpacity="0" /></linearGradient></defs>
            {[20, 45, 70].map((y) => <line key={y} x1="4" x2="96" y1={y} y2={y} className="line-grid" />)}
            <path d={`${path} L${points.at(-1).x},82 L${points[0].x},82 Z`} fill="url(#lineFill)" />
            <path d={path} className="line-path" />
            {points.map((point, index) => <circle key={index} cx={point.x} cy={point.y} r="1.55" className="line-point"><title>{`${point.label}: ${formatValue(Number(point.value) || 0, chart.currency)}`}</title></circle>)}
          </svg>
          <div className="line-labels"><span>{rows[0]?.label}</span><span>{rows.at(-1)?.label}</span></div>
        </div>
        <div className="line-legend"><span><i />{chart.value_label}</span><strong>Peak {formatValue(max, chart.currency)}</strong></div>
      </section>
    );
  }

  return (
    <section className="chart-card" aria-label={chart.title}>
      <div className="chart-heading">
        <div><span className="chart-eyebrow">DATA COMPARISON</span><h3>{chart.title}</h3></div>
        <span className="chart-total">{rows.length} <small>items</small></span>
      </div>
      <div className="bar-chart">
        {rows.map((row, index) => {
          const value = Number(row.value) || 0;
          return (
            <div className="bar-row" key={`${row.label}-${index}`}>
              <div className="bar-meta"><span title={row.label}>{row.label}</span><strong>{formatValue(value, chart.currency)}</strong></div>
              <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.max(2, (value / max) * 100)}%`, "--bar-color": palette[index % palette.length] }} /></div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
