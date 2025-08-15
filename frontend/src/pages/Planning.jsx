import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function Planning() {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState(null);
  const [form, setForm] = useState({ title: '', start: '', end: '' });
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null); // {event_id, title, start, end, assigned_to, tags}

  // Filters & pagination
  const [assigned, setAssigned] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const load = async () => {
    try {
      const [st, ev] = await Promise.all([
        api.get('/api/planning/status'),
        api.get('/api/planning/events', { params: { assigned_to: assigned || undefined, page, page_size: pageSize } })
      ]);
      setStatus(st.data);
      setEvents(ev.data);
      setError(null);
    } catch (e) { setError(e.message); }
  };

  useEffect(() => { load(); }, [page, pageSize, assigned]);

  const createEvent = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/planning/event', form);
      setForm({ title: '', start: '', end: '' });
      await load();
    } catch (e) { setError(e.message); }
  };

  const startEdit = (ev) => {
    setEditing({ ...ev, tags: (ev.tags || []).join(', ') });
  };

  const saveEdit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        title: editing.title,
        start: editing.start,
        end: editing.end,
        assigned_to: editing.assigned_to,
        tags: editing.tags ? editing.tags.split(',').map(t => t.trim()) : []
      };
      await api.put(`/api/planning/event/${editing.event_id}`, payload);
      setEditing(null);
      await load();
    } catch (e) { setError(e.message); }
  };

  const deleteEvent = async (event_id) => {
    if (!confirm('Supprimer cet événement ?')) return;
    try {
      await api.delete(`/api/planning/event/${event_id}`);
      await load();
    } catch (e) { setError(e.message); }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Planning</h1>
      {error && <div className="bg-red-50 text-red-700 p-3 rounded">{error}</div>}

      <div className="bg-white rounded shadow p-4 flex flex-col md:flex-row gap-3 items-center">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-500">Événements</div>
            <div className="text-2xl font-semibold">{status?.counts?.events ?? '—'}</div>
          </div>
        </div>
        <div className="grow" />
        <div className="flex items-center gap-2">
          <input className="border rounded p-2" placeholder="Filtre assigné à (user)" value={assigned} onChange={e => { setAssigned(e.target.value); setPage(1); }} />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Page</label>
          <button className="px-2 py-1 border rounded" disabled={page<=1} onClick={() => setPage(p => Math.max(1, p-1))}>Préc</button>
          <span className="px-2">{page}</span>
          <button className="px-2 py-1 border rounded" onClick={() => setPage(p => p+1)}>Suiv</button>
        </div>
        <div>
          <select className="border rounded p-2" value={pageSize} onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}>
            {[10,20,50,100].map(sz => <option key={sz} value={sz}>{sz}/page</option>)}
          </select>
        </div>
        <button className="px-3 py-2 bg-gray-100 rounded" onClick={load}>Actualiser</button>
      </div>

      <form onSubmit={createEvent} className="bg-white rounded shadow p-4 space-y-3">
        <h2 className="font-semibold text-lg">Nouvel Événement</h2>
        <input className="border rounded w-full p-2" placeholder="Titre" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
        <div className="grid grid-cols-2 gap-3">
          <input className="border rounded w-full p-2" type="datetime-local" value={form.start} onChange={e => setForm({ ...form, start: e.target.value })} />
          <input className="border rounded w-full p-2" type="datetime-local" value={form.end} onChange={e => setForm({ ...form, end: e.target.value })} />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-3 py-2 rounded">Créer</button>
      </form>

      {editing && (
        <form onSubmit={saveEdit} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Éditer Événement</h2>
          <input className="border rounded w-full p-2" placeholder="Titre" value={editing.title} onChange={e => setEditing({ ...editing, title: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="border rounded w-full p-2" type="datetime-local" value={editing.start?.slice(0,16) || ''} onChange={e => setEditing({ ...editing, start: e.target.value })} />
            <input className="border rounded w-full p-2" type="datetime-local" value={editing.end?.slice(0,16) || ''} onChange={e => setEditing({ ...editing, end: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input className="border rounded w-full p-2" placeholder="Assigné à (ex: user1)" value={editing.assigned_to || ''} onChange={e => setEditing({ ...editing, assigned_to: e.target.value })} />
            <input className="border rounded w-full p-2" placeholder="Tags (séparés par virgules)" value={editing.tags} onChange={e => setEditing({ ...editing, tags: e.target.value })} />
          </div>
          <div className="flex gap-2">
            <button className="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Enregistrer</button>
            <button type="button" className="px-3 py-2 rounded border" onClick={() => setEditing(null)}>Annuler</button>
          </div>
        </form>
      )}

      <div className="bg-white rounded shadow p-4">
        <h2 className="font-semibold mb-3">Calendrier</h2>
        <ul className="divide-y">
          {events.map(ev => (
            <li key={ev.event_id} className="py-2">
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium">{ev.title}</div>
                  <div className="text-sm text-gray-500">{ev.start} → {ev.end || '—'}</div>
                </div>
                <div className="flex gap-2">
                  <button className="text-gray-700" onClick={() => startEdit(ev)}>Éditer</button>
                  <button className="text-red-600" onClick={() => deleteEvent(ev.event_id)}>Supprimer</button>
                </div>
              </div>
            </li>
          ))}
          {!events.length && <li className="py-2 text-gray-500">Aucun événement</li>}
        </ul>
      </div>
    </div>
  );
}