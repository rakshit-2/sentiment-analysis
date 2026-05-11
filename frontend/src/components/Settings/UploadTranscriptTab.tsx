import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { transcriptApi } from '../../services/api';
import type { Transcript } from '../../types/api.types';
import styles from './Settings.module.scss';

const UploadTranscriptTab = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [file, setFile] = useState<File | null>(null);
  const [type, setType] = useState<'voice' | 'digital'>('voice');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<Transcript | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.txt')) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Only .txt files are allowed');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith('.txt')) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Only .txt files are allowed');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setSuccess(null);

      const result = await transcriptApi.upload(
        file,
        type,
        title || undefined,
        description || undefined
      );

      setSuccess(result);
      // Reset form
      setFile(null);
      setType('voice');
      setTitle('');
      setDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setTitle('');
    setDescription('');
    setError(null);
    setSuccess(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={styles.tabPanel}>
      <h2>Upload Transcript</h2>
      <p className={styles.description}>
        Upload a .txt file containing the conversation transcript (max 10MB, UTF-8 encoded)
      </p>

      <form onSubmit={handleSubmit} className={styles.form}>
        {/* File Upload Dropzone */}
        <div className={styles.formGroup}>
          <label>Transcript File *</label>
          <div
            className={`${styles.dropzone} ${dragActive ? styles.dragActive : ''} ${file ? styles.hasFile : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            {file ? (
              <div className={styles.fileInfo}>
                <span className={styles.fileName}>📄 {file.name}</span>
                <span className={styles.fileSize}>
                  ({(file.size / 1024).toFixed(2)} KB)
                </span>
              </div>
            ) : (
              <div className={styles.dropzoneContent}>
                <p>📁 Drag and drop your .txt file here</p>
                <p>or click to browse</p>
              </div>
            )}
          </div>
        </div>

        {/* Transcript Type */}
        <div className={styles.formGroup}>
          <label htmlFor="type">Transcript Type *</label>
          <select
            id="type"
            value={type}
            onChange={(e) => setType(e.target.value as 'voice' | 'digital')}
            className={styles.input}
            disabled={uploading}
          >
            <option value="voice">🎤 Voice Call (B2B Sales Conversation)</option>
            <option value="digital">🌐 Digital Journey (Website User Interaction)</option>
          </select>
          <small className={styles.helpText}>
            {type === 'voice' 
              ? 'Select this for B2B sales call transcripts - analyzes tone, buying signals, objections'
              : 'Select this for digital user journey logs - analyzes engagement, conversion signals, time investment'}
          </small>
        </div>

        {/* Title */}
        <div className={styles.formGroup}>
          <label htmlFor="title">Title (optional)</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Sales Call with Client XYZ"
            className={styles.input}
          />
        </div>

        {/* Description */}
        <div className={styles.formGroup}>
          <label htmlFor="description">Description (optional)</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Additional context or notes about this transcript"
            className={styles.textarea}
            rows={4}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className={styles.errorMessage}>
            ❌ {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className={styles.successMessage}>
            ✅ Transcript uploaded successfully!
            <div className={styles.successActions}>
              <button
                type="button"
                onClick={() => navigate(`/transcripts/${success.uuid}`)}
                className={styles.linkButton}
              >
                View Transcript
              </button>
              <button
                type="button"
                onClick={() => navigate('/transcripts')}
                className={styles.linkButton}
              >
                View All Transcripts
              </button>
            </div>
          </div>
        )}

        {/* Buttons */}
        <div className={styles.formActions}>
          <button
            type="submit"
            disabled={!file || uploading}
            className={styles.submitButton}
          >
            {uploading ? 'Uploading...' : 'Upload Transcript'}
          </button>
          <button
            type="button"
            onClick={handleReset}
            disabled={uploading}
            className={styles.resetButton}
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  );
};

export default UploadTranscriptTab;
