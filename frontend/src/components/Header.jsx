import React from 'react';

export default function Header({ activeTab, setActiveTab }) {
  return (
    <header className="header-nav">
      <div className="container header-flex">
        <div className="brand-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>JOB INGESTION</span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', border: '1px solid var(--border-color)', padding: '1px 6px', borderRadius: '3px' }}>
            v1.0.0
          </span>
          <span className="status-badge status-healthy" style={{ fontSize: '10px', padding: '2px 8px' }}>
            <span className="dot"></span>
            LIVE SYNC ACTIVE
          </span>
        </div>
        <ul className="nav-links">
          <li
            className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </li>
          <li
            className={`nav-link ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
          >
            Jobs
          </li>
          <li
            className={`nav-link ${activeTab === 'runs' ? 'active' : ''}`}
            onClick={() => setActiveTab('runs')}
          >
            Runs History
          </li>
          <li
            className={`nav-link ${activeTab === 'sources' ? 'active' : ''}`}
            onClick={() => setActiveTab('sources')}
          >
            Sources
          </li>
        </ul>
      </div>
    </header>
  );
}
