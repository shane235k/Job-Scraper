import React from 'react';
import { formatIST } from '../utils/date';

export default function ErrorsSection({ runsData }) {
  const runsWithErrors = (runsData?.items || []).filter((r) => r.errors && r.errors.length > 0);

  if (runsWithErrors.length === 0) {
    return null;
  }

  return (
    <div className="section-block">
      <div className="section-header">
        <h2 className="section-title">Transparent Error Logs</h2>
      </div>

      {runsWithErrors.map((run) => (
        <div key={run.id} className="error-box">
          <div className="error-title">
            INGESTION FAILURE · {run.source_id.toUpperCase()} · STATUS: {run.status}
          </div>
          {run.errors.map((err) => (
            <div key={err.id} style={{ marginBottom: '8px' }}>
              <div style={{ fontWeight: '600', fontSize: '12px' }}>
                [{err.error_type}] HTTP {err.http_status || 'N/A'} - {err.message}
              </div>
              {err.details && <div className="error-desc">{err.details}</div>}
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Occurred: {formatIST(err.timestamp)}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
