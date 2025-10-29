import React from 'react';
import './StatusDisplay.css';

function StatusDisplay({ status }) {
  const getStageMessage = () => {
    if (status.result && status.result.stage) {
      return status.result.stage;
    }
    if (status.status === 'processing') {
      return 'Processing your remix...';
    }
    if (status.status === 'completed') {
      const mode = status.result?.mode;
      if (mode === 'real') {
        return 'Remix complete! Using real AI models.';
      } else if (mode === 'mock') {
        return 'Remix complete! (Mock mode - install ML dependencies for real AI)';
      }
      return 'Remix complete!';
    }
    return '';
  };

  return (
    <div className={`status-display ${status.status}`}>
      <div className="status-header">
        <span className="status-label">{status.status}</span>
        {status.status === 'processing' && (
          <span className="status-progress">{status.progress}%</span>
        )}
      </div>
      
      {getStageMessage() && (
        <div className="status-message">{getStageMessage()}</div>
      )}
      
      {status.status === 'processing' && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${status.progress}%` }} />
        </div>
      )}
      
      {status.error && (
        <div className="status-error">{status.error}</div>
      )}
    </div>
  );
}

export default StatusDisplay;

