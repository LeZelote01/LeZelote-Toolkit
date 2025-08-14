import React, { useEffect, useState, useMemo } from 'react';
import api from '../services/api';

function Stat({ label, value }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default function Billing() {
  const [status, setStatus] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [form, setForm] = useState({ client_id: '', items: [{ description: '', quantity: 1, unit_price: 0 }] });
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null); // {invoice_id, status}

  const total = useMemo(() => form.items.reduce((s, it) => s + Number(it.quantity || 0) * Number(it.unit_price || 0), 0), [form.items]);

  const loadAll = async () => {
    try {
      const [st, inv] = await Promise.all([
        api.get('/api/billing/status'),
        api.get('/api/billing/invoices')
      ]);
      setStatus(st.data);
      setInvoices(inv.data);
      setError(null);
    } catch (e) { setError(e.message); }
  };

  useEffect(() => { loadAll(); }, []);

  const addItem = () => setForm({ ...form, items: [...form.items, { description: '', quantity: 1, unit_price: 0 }] });
  const updateItem = (i, key, value) => {
    const items = form.items.map((it, idx) => idx === i ? { ...it, [key]: value } : it);
    setForm({ ...form, items });
  };

  const createInvoice = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/billing/invoice', {
        client_id: form.client_id || 'unknown',
        items: form.items.map(it => ({ ...it, quantity: Number(it.quantity), unit_price: Number(it.unit_price) }))
      });
      setForm({ client_id: '', items: [{ description: '', quantity: 1, unit_price: 0 }] });
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const markPaid = async (invoice_id) => {
    try {
      await api.post(`/api/billing/invoice/${invoice_id}/mark-paid`);
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const startEdit = async (invoice_id) => {
    try {
      const res = await api.get(`/api/billing/invoice/${invoice_id}`);
      setEditing({ invoice_id, status: res.data.status, due_date: res.data.due_date });
    } catch (e) { setError(e.message); }
  };

  const saveEdit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/api/billing/invoice/${editing.invoice_id}`, { status: editing.status, due_date: editing.due_date });
      setEditing(null);
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const downloadPdf = (invoice_id) => {
    const base = (import.meta?.env?.REACT_APP_BACKEND_URL && import.meta.env.REACT_APP_BACKEND_URL.trim()) ? import.meta.env.REACT_APP_BACKEND_URL.trim() : '';
    const url = `${base}/api/billing/invoice/${invoice_id}/pdf`;
    window.open(url, '_blank');
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Billing</h1>
      {error && <div className="bg-red-50 text-red-700 p-3 rounded">{error}</div>}

      <div className="grid grid-cols-4 gap-4">
        <Stat label="Factures" value={status?.counts?.invoices ?? '—'} />
        <Stat label="Payées" value={status?.counts?.paid ?? '—'} />
        <Stat label="En retard" value={status?.counts?.overdue ?? '—'} />
        <Stat label="Revenu total (€)" value={status?.revenue?.total ?? '—'} />
      </div>

      <form onSubmit={createInvoice} className="bg-white rounded shadow p-4 space-y-3">
        <h2 className="font-semibold text-lg">Nouvelle Facture</h2>
        <input className="border rounded w-full p-2" placeholder="Client ID" value={form.client_id} onChange={e => setForm({ ...form, client_id: e.target.value })} />
        <div className="space-y-2">
          {form.items.map((it, i) => (
            <div key={i} className="grid grid-cols-6 gap-2">
              <input className="col-span-3 border rounded p-2" placeholder="Description" value={it.description} onChange={e => updateItem(i, 'description', e.target.value)} />
              <input className="col-span-1 border rounded p-2" type="number" min="1" value={it.quantity} onChange={e => updateItem(i, 'quantity', e.target.value)} />
              <input className="col-span-2 border rounded p-2" type="number" step="0.01" value={it.unit_price} onChange={e => updateItem(i, 'unit_price', e.target.value)} />
            </div>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <button type="button" onClick={addItem} className="px-3 py-2 bg-gray-100 rounded">+ Ajouter un item</button>
          <div className="ml-auto text-gray-700">Total: <span className="font-semibold">€ {total.toFixed(2)}</span></div>
          <button type="submit" className="px-3 py-2 bg-blue-600 text-white rounded">Créer</button>
        </div>
      </form>

      {editing && (
        <form onSubmit={saveEdit} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Éditer Facture</h2>
          <div className="grid grid-cols-2 gap-3">
            <select className="border rounded p-2" value={editing.status} onChange={e => setEditing({ ...editing, status: e.target.value })}>
              <option value="draft">draft</option>
              <option value="sent">sent</option>
              <option value="paid">paid</option>
              <option value="overdue">overdue</option>
            </select>
            <input className="border rounded p-2" type="datetime-local" value={editing.due_date?.slice(0,16) || ''} onChange={e => setEditing({ ...editing, due_date: e.target.value })} />
          </div>
          <div className="flex gap-2">
            <button className="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Enregistrer</button>
            <button type="button" className="px-3 py-2 rounded border" onClick={() => setEditing(null)}>Annuler</button>
          </div>
        </form>
      )}

      <div className="bg-white rounded shadow p-4">
        <h2 className="font-semibold mb-3">Factures</h2>
        <ul className="divide-y">
          {invoices.map(inv => (
            <li key={inv.invoice_id} className="py-2 flex justify-between items-center">
              <div>
                <div className="font-medium">{inv.invoice_id.slice(0,8)} — {inv.currency} {inv.amount}</div>
                <div className="text-sm text-gray-500">Client: {inv.client_id} • Status: {inv.status} • Échéance: {inv.due_date || '—'}</div>
              </div>
              <div className="flex gap-2">
                <button className="text-gray-700" onClick={() => startEdit(inv.invoice_id)}>Éditer</button>
                {inv.status !== 'paid' && (
                  <button className="text-green-700" onClick={() => markPaid(inv.invoice_id)}>Marquer payé</button>
                )}
                <button className="text-blue-700" onClick={() => downloadPdf(inv.invoice_id)}>Télécharger PDF</button>
              </div>
            </li>
          ))}
          {!invoices.length && <li className="py-2 text-gray-500">Aucune facture</li>}
        </ul>
      </div>
    </div>
  );
}