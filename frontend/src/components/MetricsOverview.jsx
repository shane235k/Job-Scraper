import React from 'react';

export default function MetricsOverview({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="section-block">
      <div className="section-header">
        <h2 className="section-title">Ingestion Overview</h2>
      </div>

      <div className="metrics-bar">
        <div className="metric-item">
          <span className="metric-label">Total Jobs</span>
          <span className="metric-value">{metrics.total_jobs}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Latest Fetched</span>
          <span className="metric-value">{metrics.latest_fetched_count}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">New Created</span>
          <span className="metric-value">{metrics.new_jobs_latest}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Updated</span>
          <span className="metric-value">{metrics.updated_jobs_latest}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Duplicates</span>
          <span className="metric-value">{metrics.duplicates_latest}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">HTTP 429 Errors</span>
          <span className="metric-value">{metrics.http_429_count}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Parser Failures</span>
          <span className="metric-value">{metrics.parser_failures_count}</span>
        </div>
      </div>
    </div>
  );
}
