import React, { useState, useEffect, useCallback } from 'react';

const TOUR_STEPS = [
  {
    id: 'step-welcome',
    target: null,
    title: 'Welcome to Job Ingestion Engine',
    desc: 'This application demonstrates real-time, resilient job listing acquisition using BeautifulSoup HTML DOM scraping and JSON API adapters. All listings are 100% real data stored directly in PostgreSQL with zero fake mocking.'
  },
  {
    id: 'step-live-sync',
    target: '[data-tour="live-sync"]',
    title: 'Automatic 5-Minute Indian Job Scheduler',
    desc: 'An automated background loop runs every 5 minutes, dynamically rotating tech keywords (python, react, devops) across Indian tech hubs (Bengaluru, Hyderabad, India) with human-like request pacing (1.5s–3.0s delays).'
  },
  {
    id: 'step-hero-actions',
    target: '[data-tour="hero-actions"]',
    title: 'Manual Triggers & 45-Second Cooldown Lock',
    desc: 'You can trigger manual scraping runs for any registered source. To prevent rapid-click bot detection flags, the engine automatically locks the button for 45 seconds with a live countdown timer.'
  },
  {
    id: 'step-metrics',
    target: '[data-tour="metrics-overview"]',
    title: 'Aggregated System Observability',
    desc: 'Provides real-time visibility into Total Jobs, Latest Fetched, New Created, Updated, Duplicates, and transparent HTTP 429 rate limit or Parser Failure metrics.'
  },
  {
    id: 'step-sources',
    target: '[data-tour="sources-section"]',
    title: 'Multi-Source Adapter Registry & Health',
    desc: 'Tracks source health states (HEALTHY, DEGRADED, UNAVAILABLE). If a source hits 3 consecutive failures, the engine halts access, preserves database records, and triggers Plan B fallback routes.'
  },
  {
    id: 'step-jobs',
    target: '[data-tour="jobs-section"]',
    title: 'SHA-256 Deduplication & Search Filters',
    desc: 'Raw listings pass through a deterministic SHA-256 content hasher. Repeated runs never duplicate database rows. Filter real Indian job listings by title, location, or source.'
  },
  {
    id: 'step-runs',
    target: '[data-tour="nav-runs"]',
    title: 'Transparent Error & Audit Logs',
    desc: 'Click on Runs History to inspect every execution record, exact HTTP status codes, and raw exception details logged transparently in PostgreSQL.'
  },
  {
    id: 'step-finish',
    target: null,
    title: 'Evaluator Tour Complete!',
    desc: 'You are ready to explore the dashboard live! You can restart this interactive walkthrough anytime by clicking "↺ Product Tour" in the top header bar.'
  }
];

export default function ProductTour({ isOpen, onClose, onNavigateTab }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState(null);

  const step = TOUR_STEPS[currentStep] || TOUR_STEPS[0];

  const measureTarget = useCallback((targetSel) => {
    if (!targetSel) {
      setTargetRect(null);
      return;
    }
    const el = document.querySelector(targetSel);
    if (el) {
      const rect = el.getBoundingClientRect();
      setTargetRect({
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
      });
    } else {
      setTargetRect(null);
    }
  }, []);

  // Synchronously switch step and update target rect immediately to prevent laggy jumps
  const goToStep = useCallback((nextIndex) => {
    const nextStep = TOUR_STEPS[nextIndex];
    if (!nextStep) return;

    if (nextStep.id === 'step-runs' && onNavigateTab) {
      onNavigateTab('runs');
    } else if ((nextStep.id === 'step-sources' || nextStep.id === 'step-jobs' || nextStep.id === 'step-metrics') && onNavigateTab) {
      onNavigateTab('overview');
    }

    if (nextStep.target) {
      const el = document.querySelector(nextStep.target);
      if (el) {
        const rect = el.getBoundingClientRect();
        setTargetRect({
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height
        });
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        setTargetRect(null);
      }
    } else {
      setTargetRect(null);
    }

    setCurrentStep(nextIndex);
  }, [onNavigateTab]);

  // Reset to Step 1 whenever tour opens
  useEffect(() => {
    if (isOpen) {
      goToStep(0);
    }
  }, [isOpen, goToStep]);

  useEffect(() => {
    if (!isOpen) return;

    // Refresh rect after smooth scroll finishes
    const timer = setTimeout(() => {
      measureTarget(step.target);
    }, 250);

    const handleScrollOrResize = () => measureTarget(step.target);
    window.addEventListener('resize', handleScrollOrResize);
    window.addEventListener('scroll', handleScrollOrResize, true);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', handleScrollOrResize);
      window.removeEventListener('scroll', handleScrollOrResize, true);
    };
  }, [currentStep, isOpen, step, measureTarget]);

  if (!isOpen) return null;

  const isFirst = currentStep === 0;
  const isLast = currentStep === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      onClose();
    } else {
      goToStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (!isFirst) {
      goToStep(currentStep - 1);
    }
  };

  // Dynamically position tour card OUTSIDE the highlighted area
  let cardPositionStyle = {};
  if (targetRect) {
    const cardHeight = 240;
    const cardWidth = 440;

    // For huge sections (like Step 6 jobs section), pin to bottom-right corner
    if (step.id === 'step-jobs' || targetRect.height > 350) {
      cardPositionStyle = {
        position: 'fixed',
        bottom: '32px',
        right: '32px',
        top: 'auto',
        left: 'auto'
      };
    } else {
      // For standard elements (Steps 2, 3, 4, 5, 7): place card 16px BELOW the element
      let topPos = targetRect.top + targetRect.height + 16;

      // If room below is insufficient, place card 16px ABOVE the element
      if (topPos + cardHeight > window.innerHeight - 20) {
        topPos = targetRect.top - cardHeight - 16;
      }

      // Clamp inside viewport
      topPos = Math.max(16, Math.min(window.innerHeight - cardHeight - 16, topPos));

      let leftPos = Math.min(
        Math.max(16, targetRect.left),
        window.innerWidth - cardWidth - 24
      );

      cardPositionStyle = {
        position: 'fixed',
        top: `${topPos}px`,
        left: `${leftPos}px`,
        bottom: 'auto',
        right: 'auto'
      };
    }
  }

  return (
    <div className="tour-overlay">
      {/* Spotlight Ring Highlight */}
      {targetRect && (
        <div
          className="tour-spotlight"
          style={{
            position: 'fixed',
            top: targetRect.top - 6,
            left: targetRect.left - 6,
            width: targetRect.width + 12,
            height: targetRect.height + 12
          }}
        />
      )}

      {/* Tour Card Modal */}
      <div
        className={`tour-card ${!targetRect ? 'tour-card-center' : ''}`}
        style={targetRect ? cardPositionStyle : {}}
      >
        <div className="tour-header">
          <span className="tour-step-badge">STEP {currentStep + 1} OF {TOUR_STEPS.length}</span>
          <button className="tour-close-btn" onClick={onClose}>×</button>
        </div>

        <h3 className="tour-title">{step.title}</h3>
        <p className="tour-desc">{step.desc}</p>

        <div className="tour-footer">
          <button
            className="btn btn-secondary"
            style={{ padding: '4px 10px', fontSize: '12px' }}
            onClick={onClose}
          >
            Skip Tour
          </button>

          <div style={{ display: 'flex', gap: '8px' }}>
            {!isFirst && (
              <button
                className="btn btn-secondary"
                style={{ padding: '4px 12px', fontSize: '12px' }}
                onClick={handleBack}
              >
                ← Back
              </button>
            )}
            <button
              className="btn btn-primary"
              style={{ padding: '4px 14px', fontSize: '12px' }}
              onClick={handleNext}
            >
              {isLast ? 'Finish Tour ✓' : 'Next →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
