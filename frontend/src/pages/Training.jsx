import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function Training() {
  const [courses, setCourses] = useState([]);
  const [status, setStatus] = useState(null);
  const [form, setForm] = useState({ title: '', description: '', level: 'beginner' });
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null); // {course_id, title, description, level, tags}

  // Filters & pagination
  const [level, setLevel] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const load = async () => {
    try {
      const [st, list] = await Promise.all([
        api.get('/api/training/status'),
        api.get('/api/training/courses', { params: { level: level || undefined, search: search || undefined, page, page_size: pageSize } })
      ]);
      setStatus(st.data);
      setCourses(list.data);
      setError(null);
    } catch (e) { setError(e.message); }
  };

  useEffect(() => { load(); }, [level, search, page, pageSize]);

  const createCourse = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/training/course', form);
      setForm({ title: '', description: '', level: 'beginner' });
      await load();
    } catch (e) { setError(e.message); }
  };

  const startEdit = (c) => setEditing({ ...c, tags: (c.tags || []).join(', ') });

  const saveEdit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        title: editing.title,
        description: editing.description,
        level: editing.level,
        tags: editing.tags ? editing.tags.split(',').map(t => t.trim()) : []
      };
      await api.put(`/api/training/course/${editing.course_id}`, payload);
      setEditing(null);
      await load();
    } catch (e) { setError(e.message); }
  };

  const deleteCourse = async (course_id) => {
    if (!confirm('Supprimer ce cours ?')) return;
    try {
      await api.delete(`/api/training/course/${course_id}`);
      await load();
    } catch (e) { setError(e.message); }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Training</h1>
      {error && <div className="bg-red-50 text-red-700 p-3 rounded">{error}</div>}
      <div className="bg-white rounded shadow p-4 flex flex-col md:flex-row gap-3 items-center">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-500">Cours</div>
            <div className="text-2xl font-semibold">{status?.counts?.courses ?? '—'}</div>
          </div>
        </div>
        <div className="grow" />
        <div className="flex items-center gap-2">
          <select className="border rounded p-2" value={level} onChange={e => { setLevel(e.target.value); setPage(1); }}>
            <option value="">Tous les niveaux</option>
            <option value="beginner">Débutant</option>
            <option value="intermediate">Intermédiaire</option>
            <option value="advanced">Avancé</option>
          </select>
          <input className="border rounded p-2" placeholder="Recherche titre" value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} />
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

      <form onSubmit={createCourse} className="bg-white rounded shadow p-4 space-y-3">
        <h2 className="font-semibold text-lg">Nouveau Cours</h2>
        <input className="border rounded w-full p-2" placeholder="Titre" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
        <textarea className="border rounded w-full p-2" placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
        <select className="border rounded w-full p-2" value={form.level} onChange={e => setForm({ ...form, level: e.target.value })}>
          <option value="beginner">Débutant</option>
          <option value="intermediate">Intermédiaire</option>
          <option value="advanced">Avancé</option>
        </select>
        <button type="submit" className="bg-blue-600 text-white px-3 py-2 rounded">Créer</button>
      </form>

      {editing && (
        <form onSubmit={saveEdit} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Éditer Cours</h2>
          <input className="border rounded w-full p-2" placeholder="Titre" value={editing.title} onChange={e => setEditing({ ...editing, title: e.target.value })} />
          <textarea className="border rounded w-full p-2" placeholder="Description" value={editing.description} onChange={e => setEditing({ ...editing, description: e.target.value })} />
          <select className="border rounded w-full p-2" value={editing.level} onChange={e => setEditing({ ...editing, level: e.target.value })}>
            <option value="beginner">Débutant</option>
            <option value="intermediate">Intermédiaire</option>
            <option value="advanced">Avancé</option>
          </select>
          <input className="border rounded w-full p-2" placeholder="Tags (séparés par virgules)" value={editing.tags} onChange={e => setEditing({ ...editing, tags: e.target.value })} />
          <div className="flex gap-2">
            <button className="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Enregistrer</button>
            <button type="button" className="px-3 py-2 rounded border" onClick={() => setEditing(null)}>Annuler</button>
          </div>
        </form>
      )}

      <div className="bg-white rounded shadow p-4">
        <h2 className="font-semibold mb-3">Catalogue</h2>
        <ul className="divide-y">
          {courses.map(c => (
            <li key={c.course_id} className="py-2">
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium">{c.title} <span className="text-xs text-gray-500">({c.level})</span></div>
                  <div className="text-sm text-gray-500">{c.description || '—'}</div>
                </div>
                <div className="flex gap-2">
                  <button className="text-gray-700" onClick={() => startEdit(c)}>Éditer</button>
                  <button className="text-red-600" onClick={() => deleteCourse(c.course_id)}>Supprimer</button>
                </div>
              </div>
            </li>
          ))}
          {!courses.length && <li className="py-2 text-gray-500">Aucun cours</li>}
        </ul>
      </div>
    </div>
  );
}