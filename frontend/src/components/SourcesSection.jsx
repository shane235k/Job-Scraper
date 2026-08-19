import React from 'react';
import { formatIST } from '../utils/date';

export default function SourcesSection({ sources, onRunIngestion, isRunning, cooldowns = {} }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="empty-state">
        <p className="empty-title">No sources configured</p>
        <p className="empty-desc">No job sources registered in database.</p>
      </div>
    );
  }

  return (
    <div className="section-block">
      <div className="section-header">
        <h2 className="section-title">Source Status</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {sources.map((src) => {
          const statusClass = src.health_status === 'HEALTHY' ? 'status-healthy' : src.health_status === 'DEGRADED' ? 'status-degraded' : 'status-unavailable';
          const cd = cooldowns[src.id] || 0;
          const isDisabled = isRunning || cd > 0;

          return (
            <div
              key={src.id}
              style={{
                border: '1px solid var(--border-color)',
                borderRadius: '4px',
                padding: '16px',
                background: 'var(--bg-primary)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: '600', fontSize: '15px' }}>{src.name}</span>
                <span className={`status-badge ${statusClass}`}>
                  <span className="dot"></span>
                  {src.health_status}
                </span>
              </div>

              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>
                <div>URL: {src.url}</div>
                <div>Type: {src.source_type === 'html' ? 'REAL HTML SCRAPING' : 'REAL API INGESTION'}</div>
                <div>Last Attempt: {formatIST(src.last_attempted_ingestion)}</div>
                <div>Last Success: {formatIST(src.last_successful_ingestion)}</div>
                {src.consecutive_failures > 0 && (
                  <div style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
                    Consecutive Failures: {src.consecutive_failures}
                  </div>
                )}
              </div>

              <button
                className="btn btn-secondary"
                style={{
                  width: '100%',
                  cursor: isDisabled ? 'not-allowed' : 'pointer',
                  opacity: isDisabled ? 0.6 : 1
                }}
                onClick={() => onRunIngestion(src.id)}
                disabled={isDisabled}
              >
                {isRunning
                  ? 'Running...'
                  : cd > 0
                  ? `Cooling Down (${cd}s)`
                  : 'Trigger Ingestion Run'}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
