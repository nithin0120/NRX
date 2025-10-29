import React from 'react';
import './ParameterControls.css';

function ParameterControls({ energy, brightness, onEnergyChange, onBrightnessChange }) {
  const getEnergyLabel = (val) => {
    if (val < 0.8) return 'Calm';
    if (val > 1.2) return 'Intense';
    return 'Normal';
  };

  const getBrightnessLabel = (val) => {
    if (val < 0.8) return 'Dark/Warm';
    if (val > 1.2) return 'Bright/Clear';
    return 'Balanced';
  };

  return (
    <div className="parameter-controls">
      <h3>Fine-Tune Your Remix</h3>
      <p className="instruction">Adjust how the AI transforms your song</p>
      
      <div className="parameter">
        <div className="parameter-header">
          <label>
            <span>Energy Level</span>
            <span className="value">{energy.toFixed(1)} - {getEnergyLabel(energy)}</span>
          </label>
        </div>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={energy}
          onChange={(e) => onEnergyChange(parseFloat(e.target.value))}
        />
        <div className="parameter-desc">
          Controls intensity: drums hit harder, tempo feels faster (0.5 = mellow, 2.0 = powerful)
        </div>
      </div>

      <div className="parameter">
        <div className="parameter-header">
          <label>
            <span>Brightness</span>
            <span className="value">{brightness.toFixed(1)} - {getBrightnessLabel(brightness)}</span>
          </label>
        </div>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={brightness}
          onChange={(e) => onBrightnessChange(parseFloat(e.target.value))}
        />
        <div className="parameter-desc">
          Controls tone: high frequencies, clarity (0.5 = warm/dark, 2.0 = bright/crisp)
        </div>
      </div>

      <div className="info-box">
        <strong>🎤 Smart Vocal Sync</strong>
        <p>Vocals are analyzed and automatically adjusted to match the AI-generated instrumental - perfect timing every time!</p>
      </div>
    </div>
  );
}

export default ParameterControls;

