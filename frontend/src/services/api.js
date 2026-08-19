const API_BASE = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.MODE === 'production' 
    ? 'https://job-injestion-backend.onrender.com/api' 
    : '/api');

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  return res.json();
}

export async function fetchSources() {
  const res = await fetch(`${API_BASE}/sources`);
  return res.json();
}

export async function fetchJobs(params = {}) {
  const query = new URLSearchParams();
  if (params.source) query.set('source', params.source);
  if (params.title) query.set('title', params.title);
  if (params.company) query.set('company', params.company);
  if (params.location) query.set('location', params.location);
  if (params.page) query.set('page', params.page);
  if (params.limit) query.set('limit', params.limit || 20);

  const res = await fetch(`${API_BASE}/jobs?${query.toString()}`);
  return res.json();
}

export async function fetchRuns(params = {}) {
  const query = new URLSearchParams();
  if (params.source_id) query.set('source_id', params.source_id);
  if (params.page) query.set('page', params.page);
  if (params.limit) query.set('limit', params.limit || 20);

  const res = await fetch(`${API_BASE}/ingestion/runs?${query.toString()}`);
  return res.json();
}

export async function triggerIngestion(sourceId) {
  const res = await fetch(`${API_BASE}/ingestion/run/${sourceId}`, {
    method: 'POST'
  });
  if (!res.ok) {
    const errData = await res.json();
    throw new Error(errData.detail || 'Ingestion run failed');
  }
  return res.json();
}
