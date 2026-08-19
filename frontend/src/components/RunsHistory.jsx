import React from 'react';
import { formatIST } from '../utils/date';

export default function RunsHistory({ runsData }) {
  const items = runsData?.items || [];

  return (
    <div className="section-block">
      <div className="section-header">
        <h2 className="section-title">Recent Ingestion Runs</h2>
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-title">No ingestion runs yet.</p>
          <p className="empty-desc">Run history will appear here once an ingestion run is triggered.</p>
        </div>
      ) : (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Start Time</th>
                <th>Source</th>
                <th>Status</th>
                <th>Fetched</th>
                <th>New</th>
                <th>Updated</th>
                <th>Duplicates</th>
                <th>Errors</th>
              </tr>
            </thead>
            <tbody>
              {items.map((run) => {
                const isSuccess = run.status === 'SUCCESS';
                const isPartial = run.status === 'PARTIAL';
                return (
                  <tr key={run.id}>
                    <td className="font-mono">{formatIST(run.start_time)}</td>
                    <td className="font-mono">{run.source_id}</td>
                    <td>
                      <span
                        className="font-mono"
                        style={{
                          fontWeight: '600',
                          color: isSuccess ? 'var(--text-primary)' : isPartial ? 'var(--text-secondary)' : 'var(--text-dark)',
                          borderBottom: isSuccess ? '1px solid var(--text-primary)' : '1px dashed var(--text-secondary)'
                        }}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className="font-mono">{run.jobs_fetched}</td>
                    <td className="font-mono">{run.jobs_created}</td>
                    <td className="font-mono">{run.jobs_updated}</td>
                    <td className="font-mono">{run.duplicates}</td>
                    <td className="font-mono" style={{ fontSize: '11px', color: run.error_summary ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                      {run.error_summary || 'None'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
