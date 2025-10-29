import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import StyleSelector from './components/StyleSelector';
import ParameterControls from './components/ParameterControls';
import StatusDisplay from './components/StatusDisplay';
import AudioPlayer from './components/AudioPlayer';
import SystemInfo from './components/SystemInfo';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [fileId, setFileId] = useState(null);
  const [fileName, setFileName] = useState('');
  const [styles, setStyles] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState('');
  const [energy, setEnergy] = useState(1.0);
  const [brightness, setBrightness] = useState(1.0);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [outputUrl, setOutputUrl] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/styles`).then(res => {
      setStyles(res.data.styles);
      if (res.data.styles.length > 0) {
        setSelectedStyle(res.data.styles[0]);
      }
    });
  }, []);

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/status/${jobId}`);
        setStatus(res.data);

        if (res.data.status === 'completed') {
          setOutputUrl(`${API_BASE}/download/${jobId}`);
          clearInterval(interval);
        } else if (res.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Status check failed:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE}/upload`, formData);
      setFileId(res.data.file_id);
      setFileName(res.data.filename);
    } catch (err) {
      alert('Upload failed: ' + err.message);
    }
  };

  const handleRemix = async () => {
    if (!fileId || !selectedStyle) return;

    try {
      const res = await axios.post(`${API_BASE}/remix`, {
        file_id: fileId,
        style: selectedStyle,
        energy,
        brightness
      });
      setJobId(res.data.job_id);
      setStatus(res.data);
      setOutputUrl(null);
    } catch (err) {
      alert('Remix failed: ' + err.message);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header>
          <h1>Neural Remix Engine</h1>
          <p>Multi-model AI platform for intelligent music transformation</p>
        </header>

        <SystemInfo />

        <FileUpload onUpload={handleUpload} fileName={fileName} />

        {fileId && (
          <>
            <StyleSelector
              styles={styles}
              selected={selectedStyle}
              onChange={setSelectedStyle}
            />

            <ParameterControls
              energy={energy}
              brightness={brightness}
              onEnergyChange={setEnergy}
              onBrightnessChange={setBrightness}
            />

            <button
              className="remix-button"
              onClick={handleRemix}
              disabled={!selectedStyle || status?.status === 'processing'}
            >
              {status?.status === 'processing' ? 'Processing...' : 'Generate Remix'}
            </button>
          </>
        )}

        {status && <StatusDisplay status={status} />}

        {outputUrl && <AudioPlayer url={outputUrl} />}
      </div>
    </div>
  );
}

export default App;

