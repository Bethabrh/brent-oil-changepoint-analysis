import { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer
} from 'recharts';
import './App.css';

const API_BASE = 'http://127.0.0.1:5001/api';

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function StatBadge({ label, value }) {
  return (
    <div className="stat-badge">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
    </div>
  );
}

function ChangePointCard({ cp, isActive, onClick }) {
  const isPositive = cp.pct_change >= 0;
  return (
    <button
      className={`cp-card ${isActive ? 'cp-card--active' : ''}`}
      onClick={onClick}
    >
      <div className="cp-card__gauge" style={{
        borderColor: isPositive ? 'var(--green)' : 'var(--rust)'
      }}>
        <span className="cp-card__pct" style={{
          color: isPositive ? 'var(--green)' : 'var(--rust)'
        }}>
          {isPositive ? '+' : ''}{cp.pct_change}%
        </span>
      </div>
      <div className="cp-card__body">
        <span className="cp-card__label">{cp.label}</span>
        <span className="cp-card__event">{cp.matched_event}</span>
        <span className="cp-card__date">{formatDate(cp.detected_date)}</span>
        <span className="cp-card__price">
          ${cp.price_before} &rarr; ${cp.price_after}
        </span>
      </div>
    </button>
  );
}

export default function App() {
  const [prices, setPrices] = useState([]);
  const [changepoints, setChangepoints] = useState([]);
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [activeCp, setActiveCp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadAll() {
      try {
        const [pricesRes, cpRes, eventsRes, summaryRes] = await Promise.all([
          fetch(`${API_BASE}/prices`),
          fetch(`${API_BASE}/changepoints`),
          fetch(`${API_BASE}/events`),
          fetch(`${API_BASE}/summary`),
        ]);

        if (!pricesRes.ok || !cpRes.ok || !eventsRes.ok || !summaryRes.ok) {
          throw new Error('One or more API endpoints failed to respond.');
        }

        const pricesData = await pricesRes.json();
        const cpData = await cpRes.json();
        const eventsData = await eventsRes.json();
        const summaryData = await summaryRes.json();

        // Downsample prices for chart performance (every 5th point)
        const sampled = pricesData.data.filter((_, i) => i % 5 === 0);

        setPrices(sampled);
        setChangepoints(cpData.changepoints || []);
        setEvents(eventsData.data || []);
        setSummary(summaryData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  if (loading) {
    return (
      <div className="status-screen">
        <span className="status-screen__text">Loading market data&hellip;</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-screen">
        <span className="status-screen__text status-screen__text--error">
          Could not reach the API. Make sure the Flask backend is running on port 5001.
        </span>
        <span className="status-screen__detail">{error}</span>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header__title-block">
          <span className="header__eyebrow">Birhan Energies</span>
          <h1 className="header__title">Brent Crude &mdash; Structural Break Monitor</h1>
        </div>
        <div className="header__stats">
          <StatBadge label="Range" value={`${formatDate(summary.date_range.start)} \u2013 ${formatDate(summary.date_range.end)}`} />
          <StatBadge label="Observations" value={summary.total_observations.toLocaleString()} />
          <StatBadge label="Breaks Detected" value={summary.total_changepoints_detected} />
        </div>
      </header>

      <section className="chart-panel">
        <h2 className="panel-title">Price History with Detected Change Points</h2>
        <ResponsiveContainer width="100%" height={380}>
          <LineChart data={prices} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#2A3B47" strokeDasharray="2 4" vertical={false} />
<XAxis
  dataKey="Date"
  stroke="#8FA3AD"
  tick={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, fill: '#8FA3AD' }}
  tickFormatter={(d) => d.slice(0, 4)}
  minTickGap={60}
/>
<YAxis
  stroke="#8FA3AD"
  tick={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, fill: '#8FA3AD' }}
  tickFormatter={(v) => `$${v}`}
  width={50}
/>
          <Tooltip
  contentStyle={{
    background: '#16232E',
    border: '1px solid #2A3B47',
    borderRadius: 4,
    fontFamily: 'IBM Plex Mono, monospace',
    fontSize: 12,
  }}
  labelStyle={{ color: '#8FA3AD' }}
  formatter={(value) => [`$${value}`, 'Price']}
/>
            {changepoints.map((cp) => (
  <ReferenceLine
    key={cp.label}
    x={cp.detected_date}
    stroke={activeCp === cp.label ? '#D9A441' : '#C1502E'}
    strokeWidth={activeCp === cp.label ? 2 : 1}
    strokeDasharray={activeCp === cp.label ? undefined : '3 3'}
  />
))}
<Line
  type="monotone"
  dataKey="Price"
  stroke="#D9A441"
  strokeWidth={1.5}
  dot={false}
  isAnimationActive={false}
/>
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section className="cp-panel">
        <h2 className="panel-title">Detected Structural Breaks &amp; Associated Events</h2>
        <div className="cp-grid">
          {changepoints.map((cp) => (
            <ChangePointCard
              key={cp.label}
              cp={cp}
              isActive={activeCp === cp.label}
              onClick={() => setActiveCp(activeCp === cp.label ? null : cp.label)}
            />
          ))}
        </div>
      </section>

      <section className="events-panel">
        <h2 className="panel-title">Full Event Timeline ({events.length} events)</h2>
        <div className="events-table-wrap">
          <table className="events-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Event</th>
                <th>Category</th>
                <th>Expected Direction</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => (
                <tr key={ev.Event_ID}>
                  <td className="mono">{ev.Event_Date}</td>
                  <td>{ev.Event_Name}</td>
                  <td><span className="category-pill">{ev.Category}</span></td>
                  <td className={ev.Expected_Price_Direction === 'Increase' ? 'text-green' : 'text-rust'}>
                    {ev.Expected_Price_Direction}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="footer">
        <span>Birhan Energies Data Science Challenge &middot; Bayesian Change Point Analysis &middot; PyMC</span>
      </footer>
    </div>
  );
}