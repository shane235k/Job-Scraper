import React from 'react';

export default function Header({ activeTab, setActiveTab, onStartTour }) {
  return (
    <header className="header-nav">
      <div className="container header-flex">
        <div className="brand-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>JOB INGESTION</span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', border: '1px solid var(--border-color)', padding: '1px 6px', borderRadius: '3px' }}>
            v1.0.0
          </span>
          <span data-tour="live-sync" className="status-badge status-healthy" style={{ fontSize: '10px', padding: '2px 8px' }}>
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
            data-tour="nav-runs"
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
          <li>
            <button
              className="btn btn-primary"
              style={{
                fontSize: '13px',
                fontWeight: '600',
                padding: '6px 14px',
                borderRadius: '4px',
                marginLeft: '12px',
                background: '#111111',
                color: '#FFFFFF',
                border: '1px solid #333333',
                cursor: 'pointer',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}
              onClick={onStartTour}
            >
              ↺ Product Tour
            </button>
          </li>
        </ul>
      </div>
    </header>
  );
}
