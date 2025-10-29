import React, { useRef } from 'react';
import './FileUpload.css';

function FileUpload({ onUpload, fileName }) {
  const inputRef = useRef();

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="file-upload">
      <input
        ref={inputRef}
        type="file"
        accept="audio/*"
        onChange={handleChange}
        style={{ display: 'none' }}
      />
      <div className="upload-area" onClick={handleClick}>
        {fileName ? (
          <div className="uploaded">
            <div className="file-icon">♫</div>
            <div className="file-name">{fileName}</div>
            <div className="change-text">Click to change file</div>
          </div>
        ) : (
          <div className="prompt">
            <div className="upload-icon">↑</div>
            <div className="upload-text">Click to upload audio file</div>
            <div className="upload-formats">MP3, WAV, FLAC, M4A</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileUpload;

