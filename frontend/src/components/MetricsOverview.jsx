import React from 'react';

export default function MetricsOverview({ metrics }) {
  if (!metrics) return null;

  const totalJobs = metrics.total_jobs ?? 0;
  const latestFetched = metrics.latest_fetched_count ?? metrics.latest_fetched ?? 0;
  const newCreated = metrics.new_jobs_latest ?? metrics.new_created ?? 0;
  const updated = metrics.updated_jobs_latest ?? metrics.updated ?? 0;
  const duplicates = metrics.duplicates_latest ?? metrics.duplicates ?? 0;
  const http429Errors = metrics.http_429_count ?? metrics.http_429_errors ?? 0;
  const parserFailures = metrics.parser_failures_count ?? metrics.parser_failures ?? 0;

  return (
    <div className="section-block" data-tour="metrics-overview">
      <div className="section-header">
        <h2 className="section-title">Ingestion Overview</h2>
      </div>

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '36px',
          rowGap: '16px',
          padding: '20px 24px',
          border: '1px solid var(--border-color)',
          borderRadius: '4px',
          background: 'var(--bg-primary)'
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '100px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Total Jobs</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{totalJobs}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '100px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Latest Fetched</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{latestFetched}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '100px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>New Created</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{newCreated}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '100px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Updated</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{updated}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '100px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Duplicates</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{duplicates}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '110px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>HTTP 429 Errors</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{http429Errors}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', minWidth: '110px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Parser Failures</div>
          <div style={{ fontSize: '22px', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>{parserFailures}</div>
        </div>
      </div>
    </div>
  );
}
