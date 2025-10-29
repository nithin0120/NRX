import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SystemInfo.css';

const API_BASE = 'http://localhost:8000/api';

function SystemInfo() {
  const [info, setInfo] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE}/system`).then(res => {
      setInfo(res.data);
    });
  }, []);

  if (!info) return null;

  return (
    <div className="system-info">
      <button 
        className="info-toggle" 
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? '▼' : '▶'} System Info
      </button>
      
      {expanded && (
        <div className="info-content">
          <div className="info-header">
            <h3>{info.platform}</h3>
            <span className={`mode-badge ${info.mode}`}>{info.mode.toUpperCase()}</span>
          </div>
          
          <p className="info-description">{info.description}</p>
          
          <div className="subsystems">
            <h4>AI Subsystems ({Object.keys(info.ai_subsystems).length})</h4>
            {Object.entries(info.ai_subsystems).map(([key, system]) => (
              <div key={key} className="subsystem">
                <div className="subsystem-header">
                  <span className="subsystem-name">{system.model}</span>
                  <span className={`status ${system.status}`}>{system.status}</span>
                </div>
                <p className="subsystem-purpose">{system.purpose}</p>
              </div>
            ))}
          </div>
          
          <div className="distinction">
            <strong>Platform vs Model:</strong> {info.distinction}
          </div>
        </div>
      )}
    </div>
  );
}

export default SystemInfo;

