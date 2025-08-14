import React, { useEffect, useState } from 'react';
import api from '../services/api';

function BarChart({ data }) {
  // data: [{date, revenue_total}]
  const max = Math.max(1, ...data.map(d => d.revenue_total));
  return (
    <div className="flex items-end gap-2 h-32">
      {data.map((d, i) => (
        <div key={i} title={`€ ${d.revenue_total} — ${d.date}`} className="bg-blue-500 rounded-t" style={{ height: `${(d.revenue_total / max) * 100}%`, width: '24px' }} />
      ))}
    </div>
  );
}

export default function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [daily, setDaily] = useState([]);
  const [error, setError] = useState(null);

  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');

  const load = async () => {
    try {
      const params = { from_date: fromDate || undefined, to_date: toDate || undefined };
      const [m, d] = await Promise.all([
        api.get('/api/analytics/metrics', { params }),
        api.get('/api/analytics/metrics/daily', { params: { days: 7, ...params } })
      ]);
      setMetrics(m.data);
      setDaily(d.data);
      setError(null);
    } catch (e) { setError(e.message); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      {error && <div className="bg-red-50 text-red-700 p-3 rounded">{error}</div>}

      <div className="bg-white rounded shadow p-4 flex flex-col md:flex-row gap-3 items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Du</label>
          <input type="date" className="border rounded p-2" value={fromDate} onChange={e => setFromDate(e.target.value)} />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Au</label>
          <input type="date" className="border rounded p-2" value={toDate} onChange={e => setToDate(e.target.value)} />
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-2 bg-gray-100 rounded" onClick={load}>Appliquer</button>
          <button className="px-3 py-2 border rounded" onClick={() => { setFromDate(''); setToDate(''); setTimeout(load, 0); }}>Réinitialiser</button>
        </div>
      </div>

      {!metrics ? (
        <div>Chargement...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded shadow p-4">
            <div className="text-sm text-gray-500">Clients</div>
            <div className="text-2xl font-semibold">{metrics.totals.clients}</div>
          </div>
          <div className="bg-white rounded shadow p-4">
            <div className="text-sm text-gray-500">Projets</div>
            <div className="text-2xl font-semibold">{metrics.totals.projects}</div>
          </div>
          <div className="bg-white rounded shadow p-4">
            <div className="text-sm text-gray-500">Factures</div>
            <div className="text-2xl font-semibold">{metrics.totals.invoices}</div>
          </div>
          <div className="bg-white rounded shadow p-4">
            <div className="text-sm text-gray-500">Revenu total</div>
            <div className="text-2xl font-semibold">€ {metrics.revenue.total}</div>
          </div>
          <div className="bg-white rounded shadow p-4">
            <div className="text-sm text-gray-500">Revenu payé</div>
            <div className="text-2xl font-semibold">€ {metrics.revenue.paid}</div>
          </div>
        </div>
      )}

      {!!daily.length && (
        <div className="bg-white rounded shadow p-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">Revenu sur 7 jours</h2>
            <div className="text-sm text-gray-500">Somme des montants de factures par jour</div>
          </div>
          <div className="mt-4">
            <BarChart data={daily.map(d => ({ date: d.date, revenue_total: d.revenue_total }))} />
          </div>
          <div className="mt-2 grid grid-cols-7 text-xs text-gray-500">
            {daily.map((d, i) => (
              <div key={i} className="truncate" title={d.date}>{d.date.slice(5)}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}