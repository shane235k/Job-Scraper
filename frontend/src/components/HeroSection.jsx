import React from 'react';

export default function HeroSection({ onRunIngestion, isRunning, selectedSource, setSelectedSource, sources, cooldowns = {} }) {
  const cd = cooldowns[selectedSource] || 0;
  const isDisabled = isRunning || cd > 0;

  return (
    <section className="hero-section">
      <div className="container">
        <h1 className="hero-title">Job Ingestion System</h1>
        <p className="hero-subtitle">
          Real-time job listing acquisition, BeautifulSoup HTML scraping, deduplication, and resilience monitoring.
        </p>

        <div className="hero-actions" data-tour="hero-actions">
          <button
            className="btn btn-primary"
            onClick={() => onRunIngestion(selectedSource)}
            disabled={isDisabled}
            style={{
              cursor: isDisabled ? 'not-allowed' : 'pointer',
              opacity: isDisabled ? 0.65 : 1
            }}
          >
            {isRunning
              ? 'Running Ingestion...'
              : cd > 0
              ? `Cooling Down (${cd}s)`
              : `Run Ingestion (${selectedSource})`}
          </button>

          <select
            className="input-field"
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            disabled={isRunning}
            style={{ width: 'auto' }}
          >
            {sources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.source_type.toUpperCase()})
              </option>
            ))}
          </select>
        </div>
      </div>
    </section>
  );
}
