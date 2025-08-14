import React, { useEffect, useState } from 'react';
import api from '../services/api';

function Stat({ label, value }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default function CRM() {
  const [status, setStatus] = useState(null);
  const [clients, setClients] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [clientForm, setClientForm] = useState({ company: '', contactName: '', contactEmail: '' });
  const [projectForm, setProjectForm] = useState({ client_id: '', services: '', budget: '' });
  const [selectedClientId, setSelectedClientId] = useState('');

  // Filters & pagination
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Edit forms
  const [editClient, setEditClient] = useState(null); // {client_id, company, contacts, billing_info}
  const [editProject, setEditProject] = useState(null); // {project_id, services, budget, status}

  const loadAll = async () => {
    try {
      setLoading(true);
      const [st, cl, pr] = await Promise.all([
        api.get('/api/crm/status'),
        api.get('/api/crm/clients', { params: { search: search || undefined, page, page_size: pageSize } }),
        selectedClientId
          ? api.get(`/api/crm/projects`, { params: { client_id: selectedClientId, page: 1, page_size: 20 } })
          : api.get('/api/crm/projects', { params: { page: 1, page_size: 20 } })
      ]);
      setStatus(st.data);
      setClients(cl.data);
      setProjects(pr.data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAll(); }, [selectedClientId, page, pageSize]);

  const createClient = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        company: clientForm.company,
        contacts: clientForm.contactEmail ? [{ name: clientForm.contactName, email: clientForm.contactEmail }] : [],
        projects: [],
        billing_info: null
      };
      await api.post('/api/crm/client', payload);
      setClientForm({ company: '', contactName: '', contactEmail: '' });
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const createProject = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        client_id: projectForm.client_id,
        services: projectForm.services ? projectForm.services.split(',').map(s => s.trim()) : [],
        budget: projectForm.budget ? parseFloat(projectForm.budget) : undefined
      };
      await api.post('/api/crm/project', payload);
      setProjectForm({ client_id: '', services: '', budget: '' });
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const startEditClient = async (cid) => {
    try {
      const res = await api.get(`/api/crm/client/${cid}`);
      const c = res.data;
      setEditClient({
        client_id: c.client_id,
        company: c.company,
        billing_info: c.billing_info || {},
        contactName: (c.contacts || [])[0]?.name || '',
        contactEmail: (c.contacts || [])[0]?.email || ''
      });
    } catch (e) { setError(e.message); }
  };

  const saveEditClient = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        company: editClient.company,
        billing_info: editClient.billing_info,
        contacts: editClient.contactEmail ? [{ name: editClient.contactName, email: editClient.contactEmail }] : []
      };
      await api.put(`/api/crm/client/${editClient.client_id}`, payload);
      setEditClient(null);
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const deleteClient = async (cid) => {
    if (!confirm('Supprimer ce client et ses projets liés ?')) return;
    try {
      await api.delete(`/api/crm/client/${cid}`);
      if (selectedClientId === cid) setSelectedClientId('');
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const startEditProject = (p) => {
    setEditProject({
      project_id: p.project_id,
      services: (p.services || []).join(', '),
      budget: p.budget || '',
      status: p.status || 'planned'
    });
  };

  const saveEditProject = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        services: editProject.services ? editProject.services.split(',').map(s => s.trim()) : [],
        budget: editProject.budget ? Number(editProject.budget) : undefined,
        status: editProject.status
      };
      await api.put(`/api/crm/project/${editProject.project_id}`, payload);
      setEditProject(null);
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const deleteProject = async (pid) => {
    if (!confirm('Supprimer ce projet ?')) return;
    try {
      await api.delete(`/api/crm/project/${pid}`);
      await loadAll();
    } catch (e) { setError(e.message); }
  };

  const resetPagination = () => { setPage(1); };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">CRM</h1>

      {error && <div className="bg-red-50 text-red-700 p-3 rounded">{error}</div>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat label="Clients" value={status?.counts?.clients ?? '—'} />
        <Stat label="Projets" value={status?.counts?.projects ?? '—'} />
      </div>

      <div className="bg-white p-4 rounded shadow flex flex-col md:flex-row gap-3 items-center">
        <div className="grow">
          <label className="text-sm text-gray-600 mr-2">Filtrer par client</label>
          <select className="border rounded p-2" value={selectedClientId} onChange={e => setSelectedClientId(e.target.value)}>
            <option value="">Tous</option>
            {clients.map(c => <option key={c.client_id} value={c.client_id}>{c.company}</option>)}
          </select>
        </div>
        <div className="grow">
          <input className="border rounded w-full p-2" placeholder="Recherche société" value={search} onChange={e => { setSearch(e.target.value); resetPagination(); }} />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Page</label>
          <button className="px-2 py-1 border rounded" disabled={page<=1} onClick={() => setPage(p => Math.max(1, p-1))}>Préc</button>
          <span className="px-2">{page}</span>
          <button className="px-2 py-1 border rounded" onClick={() => setPage(p => p+1)}>Suiv</button>
        </div>
        <div>
          <select className="border rounded p-2" value={pageSize} onChange={e => { setPageSize(Number(e.target.value)); resetPagination(); }}>
            {[5,10,20,50].map(sz => <option key={sz} value={sz}>{sz}/page</option>)}
          </select>
        </div>
        <button className="px-3 py-2 bg-gray-100 rounded" onClick={loadAll}>Actualiser</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <form onSubmit={createClient} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Nouveau Client</h2>
          <input className="border rounded w-full p-2" placeholder="Société" value={clientForm.company} onChange={e => setClientForm({ ...clientForm, company: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="border rounded w-full p-2" placeholder="Nom contact (optionnel)" value={clientForm.contactName} onChange={e => setClientForm({ ...clientForm, contactName: e.target.value })} />
            <input className="border rounded w-full p-2" placeholder="Email contact (optionnel)" value={clientForm.contactEmail} onChange={e => setClientForm({ ...clientForm, contactEmail: e.target.value })} />
          </div>
          <button type="submit" className="bg-blue-600 text-white px-3 py-2 rounded">Créer</button>
        </form>

        <form onSubmit={createProject} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Nouveau Projet</h2>
          <select className="border rounded w-full p-2" value={projectForm.client_id} onChange={e => setProjectForm({ ...projectForm, client_id: e.target.value })}>
            <option value="">Sélectionner un client</option>
            {clients.map(c => <option key={c.client_id} value={c.client_id}>{c.company}</option>)}
          </select>
          <input className="border rounded w-full p-2" placeholder="Services (séparés par virgules)" value={projectForm.services} onChange={e => setProjectForm({ ...projectForm, services: e.target.value })} />
          <input className="border rounded w-full p-2" placeholder="Budget (EUR)" type="number" value={projectForm.budget} onChange={e => setProjectForm({ ...projectForm, budget: e.target.value })} />
          <button type="submit" className="bg-blue-600 text-white px-3 py-2 rounded">Créer</button>
        </form>
      </div>

      {editClient && (
        <form onSubmit={saveEditClient} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Éditer Client</h2>
          <input className="border rounded w-full p-2" value={editClient.company} onChange={e => setEditClient({ ...editClient, company: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="border rounded w-full p-2" placeholder="Nom contact" value={editClient.contactName} onChange={e => setEditClient({ ...editClient, contactName: e.target.value })} />
            <input className="border rounded w-full p-2" placeholder="Email contact" value={editClient.contactEmail} onChange={e => setEditClient({ ...editClient, contactEmail: e.target.value })} />
          </div>
          <button className="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Enregistrer</button>
          <button type="button" className="ml-2 px-3 py-2 rounded border" onClick={() => setEditClient(null)}>Annuler</button>
        </form>
      )}

      {editProject && (
        <form onSubmit={saveEditProject} className="bg-white rounded shadow p-4 space-y-3">
          <h2 className="font-semibold text-lg">Éditer Projet</h2>
          <input className="border rounded w-full p-2" placeholder="Services" value={editProject.services} onChange={e => setEditProject({ ...editProject, services: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="border rounded w-full p-2" type="number" placeholder="Budget" value={editProject.budget} onChange={e => setEditProject({ ...editProject, budget: e.target.value })} />
            <select className="border rounded w-full p-2" value={editProject.status} onChange={e => setEditProject({ ...editProject, status: e.target.value })}>
              <option value="planned">planned</option>
              <option value="active">active</option>
              <option value="completed">completed</option>
              <option value="on_hold">on_hold</option>
            </select>
          </div>
          <button className="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Enregistrer</button>
          <button type="button" className="ml-2 px-3 py-2 rounded border" onClick={() => setEditProject(null)}>Annuler</button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded shadow p-4">
          <h2 className="font-semibold mb-3">Clients</h2>
          <ul className="divide-y">
            {clients.map(c => (
              <li key={c.client_id} className="py-3">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium">{c.company}</div>
                    <div className="text-sm text-gray-500">{(c.contacts||[]).map(x => x.email).join(', ') || '—'}</div>
                  </div>
                  <div className="flex gap-2">
                    <button className="text-blue-600" onClick={() => setSelectedClientId(c.client_id)}>Projets</button>
                    <button className="text-gray-700" onClick={() => startEditClient(c.client_id)}>Éditer</button>
                    <button className="text-red-600" onClick={() => deleteClient(c.client_id)}>Supprimer</button>
                  </div>
                </div>
              </li>
            ))}
            {!clients.length && <li className="py-2 text-gray-500">Aucun client</li>}
          </ul>
        </div>

        <div className="bg-white rounded shadow p-4">
          <h2 className="font-semibold mb-3">Projets</h2>
          <ul className="divide-y">
            {projects.map(p => (
              <li key={p.project_id} className="py-3">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium">Projet #{p.project_id.slice(0,8)}</div>
                    <div className="text-sm text-gray-500">Client: {p.client_id} • Budget: {p.budget ?? '—'} • Status: {p.status}</div>
                  </div>
                  <div className="flex gap-2">
                    <button className="text-gray-700" onClick={() => startEditProject(p)}>Éditer</button>
                    <button className="text-red-600" onClick={() => deleteProject(p.project_id)}>Supprimer</button>
                  </div>
                </div>
              </li>
            ))}
            {!projects.length && <li className="py-2 text-gray-500">Aucun projet</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}