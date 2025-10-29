import React from 'react';
import './StyleSelector.css';

function StyleSelector({ styles, selected, onChange }) {
  const formatStyleName = (style) => {
    return style.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const styleDescriptions = {
    'lofi_chill': 'Laid-back hip-hop beats with jazz elements',
    'synthwave': '80s retro electronic with neon vibes',
    'neo_soul': 'Smooth R&B with jazz harmonies',
    'acoustic': 'Organic guitar-based arrangements',
    'edm': 'High-energy festival electronic',
    'jazz': 'Sophisticated swing with improvisation',
    'rock': 'Electric guitar-driven anthems',
    'orchestral': 'Cinematic strings and brass'
  };

  return (
    <div className="style-selector">
      <h3>Select Genre</h3>
      <p className="instruction">Click a genre to transform your song</p>
      <div className="style-grid">
        {styles.map(style => (
          <button
            key={style}
            className={`style-button ${selected === style ? 'selected' : ''}`}
            onClick={() => onChange(style)}
          >
            <div className="style-name">{formatStyleName(style)}</div>
            <div className="style-desc">{styleDescriptions[style]}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default StyleSelector;

