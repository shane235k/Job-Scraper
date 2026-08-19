import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import MetricsOverview from './components/MetricsOverview';
import SourcesSection from './components/SourcesSection';
import JobsSection from './components/JobsSection';
import RunsHistory from './components/RunsHistory';
import ErrorsSection from './components/ErrorsSection';
import ProductTour from './components/ProductTour';

import {
  fetchMetrics,
  fetchSources,
  fetchJobs,
  fetchRuns,
  triggerIngestion
} from './services/api';

const COOLDOWN_SECONDS = 45;

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('python_org');
  const [metrics, setMetrics] = useState(null);
  const [jobsData, setJobsData] = useState(null);
  const [runsData, setRunsData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [cooldowns, setCooldowns] = useState({});
  const [isTourOpen, setIsTourOpen] = useState(false);

  const [jobFilters, setJobFilters] = useState({
    title: '',
    location: '',
    source: '',
    page: 1,
    limit: 20
  });

  // Calculate remaining cooldowns based on last_attempted_ingestion
  const syncCooldowns = (srcItems) => {
    const newCooldowns = {};
    const now = Date.now();
    (srcItems || []).forEach((src) => {
      if (src.last_attempted_ingestion) {
        let lastTime = new Date(src.last_attempted_ingestion).getTime();
        if (typeof src.last_attempted_ingestion === 'string' && !src.last_attempted_ingestion.endsWith('Z') && !src.last_attempted_ingestion.includes('+')) {
          lastTime = new Date(src.last_attempted_ingestion + 'Z').getTime();
        }
        const elapsedSec = Math.floor((now - lastTime) / 1000);
        if (elapsedSec < COOLDOWN_SECONDS) {
          newCooldowns[src.id] = COOLDOWN_SECONDS - elapsedSec;
        }
      }
    });
    setCooldowns(newCooldowns);
  };

  // Live timer interval to count down remaining cooldown seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCooldowns((prev) => {
        let updated = false;
        const next = { ...prev };
        Object.keys(next).forEach((key) => {
          if (next[key] > 0) {
            next[key] -= 1;
            updated = true;
          }
        });
        return updated ? next : prev;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const loadData = async () => {
    try {
      const [srcs, mtrs, rns] = await Promise.all([
        fetchSources(),
        fetchMetrics(),
        fetchRuns({ page: 1, limit: 10 })
      ]);
      const srcItems = srcs.items || [];
      setSources(srcItems);
      setMetrics(mtrs);
      setRunsData(rns);
      syncCooldowns(srcItems);
    } catch (err) {
      console.error('Error loading initial data:', err);
      setErrorMsg('Failed to connect to backend server. Ensure FastAPI backend is running on port 8000.');
    }
  };

  const loadJobs = async () => {
    try {
      const data = await fetchJobs(jobFilters);
      setJobsData(data);
    } catch (err) {
      console.error('Error loading jobs:', err);
    }
  };

  useEffect(() => {
    loadData();
    loadJobs();
    
    // Auto-launch product tour on first visit
    if (!localStorage.getItem('job_ingestion_tour_seen')) {
      setIsTourOpen(true);
    }

    const pollInterval = setInterval(() => {
      loadData();
      loadJobs();
    }, 5000);
    return () => clearInterval(pollInterval);
  }, [jobFilters]);

  const handleRunIngestion = async (sourceId) => {
    const targetSource = sourceId || selectedSource;
    if (cooldowns[targetSource] > 0) return;

    setIsRunning(true);
    setErrorMsg(null);
    try {
      await triggerIngestion(targetSource);
      setCooldowns((prev) => ({ ...prev, [targetSource]: COOLDOWN_SECONDS }));
      await loadData();
      await loadJobs();
    } catch (err) {
      const match = err.message.match(/wait (\d+) seconds/i);
      if (match) {
        const rem = parseInt(match[1], 10);
        setCooldowns((prev) => ({ ...prev, [targetSource]: rem }));
      } else {
        setCooldowns((prev) => ({ ...prev, [targetSource]: COOLDOWN_SECONDS }));
      }
      setErrorMsg(`Ingestion run alert: ${err.message}`);
      await loadData();
    } finally {
      setIsRunning(false);
    }
  };

  const handleCloseTour = () => {
    localStorage.setItem('job_ingestion_tour_seen', 'true');
    setIsTourOpen(false);
  };

  const handleStartTour = () => {
    setIsTourOpen(true);
  };

  return (
    <div className="app">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onStartTour={handleStartTour}
      />

      <main className="main-content">
        <HeroSection
          onRunIngestion={handleRunIngestion}
          isRunning={isRunning}
          selectedSource={selectedSource}
          setSelectedSource={setSelectedSource}
          sources={sources}
          cooldowns={cooldowns}
        />

        <div className="container">
          {errorMsg && (
            <div className="error-box" style={{ marginTop: '24px' }}>
              <div className="error-title">SYSTEM ALERT</div>
              <div className="error-desc">{errorMsg}</div>
            </div>
          )}

          {activeTab === 'overview' && (
            <>
              <MetricsOverview metrics={metrics} />
              <SourcesSection
                sources={sources}
                onRunIngestion={handleRunIngestion}
                isRunning={isRunning}
                cooldowns={cooldowns}
              />
              <JobsSection
                jobsData={jobsData}
                filters={jobFilters}
                setFilters={setJobFilters}
                onPageChange={(page) => setJobFilters({ ...jobFilters, page })}
              />
            </>
          )}

          {activeTab === 'jobs' && (
            <JobsSection
              jobsData={jobsData}
              filters={jobFilters}
              setFilters={setJobFilters}
              onPageChange={(page) => setJobFilters({ ...jobFilters, page })}
            />
          )}

          {activeTab === 'runs' && (
            <>
              <RunsHistory runsData={runsData} />
              <ErrorsSection runsData={runsData} />
            </>
          )}

          {activeTab === 'sources' && (
            <SourcesSection
              sources={sources}
              onRunIngestion={handleRunIngestion}
              isRunning={isRunning}
              cooldowns={cooldowns}
            />
          )}
        </div>
      </main>

      <ProductTour
        isOpen={isTourOpen}
        onClose={handleCloseTour}
        onNavigateTab={setActiveTab}
      />
    </div>
  );
}
