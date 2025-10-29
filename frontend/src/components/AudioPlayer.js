import React from 'react';
import './AudioPlayer.css';

function AudioPlayer({ url }) {
  return (
    <div className="audio-player">
      <div className="player-header">Your Remix</div>
      <audio controls src={url}>
        Your browser does not support audio playback.
      </audio>
      <a href={url} download className="download-link">
        Download
      </a>
    </div>
  );
}

export default AudioPlayer;

