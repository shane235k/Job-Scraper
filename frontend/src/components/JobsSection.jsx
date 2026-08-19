import React from 'react';
import { formatIST, formatDateIST } from '../utils/date';

export default function JobsSection({ jobsData, filters, setFilters, onPageChange }) {
  const items = jobsData?.items || [];
  const total = jobsData?.total || 0;
  const page = jobsData?.page || 1;
  const pages = jobsData?.pages || 1;

  return (
    <div className="section-block">
      <div className="section-header">
        <h2 className="section-title">Latest Scraped Jobs ({total})</h2>
      </div>

      <div className="filter-bar">
        <input
          type="text"
          className="input-field"
          placeholder="Filter by title..."
          value={filters.title || ''}
          onChange={(e) => setFilters({ ...filters, title: e.target.value, page: 1 })}
        />
        <input
          type="text"
          className="input-field"
          placeholder="Filter by location..."
          value={filters.location || ''}
          onChange={(e) => setFilters({ ...filters, location: e.target.value, page: 1 })}
        />
        <select
          className="input-field"
          value={filters.source || ''}
          onChange={(e) => setFilters({ ...filters, source: e.target.value, page: 1 })}
        >
          <option value="">All Sources</option>
          <option value="python_org">Python.org Jobs (HTML Scraper)</option>
          <option value="linkedin">LinkedIn Jobs (Public Scraper)</option>
          <option value="muse">The Muse (API)</option>
        </select>
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-title">No jobs have been ingested yet.</p>
          <p className="empty-desc">Run an ingestion to retrieve current listings from Python.org, LinkedIn, or The Muse.</p>
        </div>
      ) : (
        <>
          <div className="jobs-list">
            {items.map((job) => (
              <div key={job.id} className="job-item">
                <div className="job-main">
                  <div className="job-title">{job.title}</div>
                  <div className="job-company-loc">
                    {job.company} · {job.location || 'Remote / Unspecified'}
                  </div>
                  <div className="job-meta">
                    <span>Source: {job.source === 'python_org' ? 'Python.org Jobs' : job.source === 'linkedin' ? 'LinkedIn Jobs' : job.source}</span>
                    {job.posted_at && <span>Posted: {formatDateIST(job.posted_at)}</span>}
                    <span>First Seen: {formatIST(job.first_seen_at)}</span>
                  </div>
                </div>

                <div className="job-action">
                  {job.job_url ? (
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '12px' }}
                    >
                      View listing →
                    </a>
                  ) : (
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>No URL</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
              <button
                className="btn btn-secondary"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
              >
                ← Previous
              </button>
              <span className="font-mono" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Page {page} of {pages}
              </span>
              <button
                className="btn btn-secondary"
                onClick={() => onPageChange(page + 1)}
                disabled={page >= pages}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
