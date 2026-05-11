import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { transcriptApi } from '../../services/api';
import styles from './Settings.module.scss';

interface FileStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'failed';
  error?: string;
  uuid?: string;
}

const BulkUploadTranscriptTab = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [type, setType] = useState<'voice' | 'digital'>('voice');
  const [uploading, setUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
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

    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = (newFiles: File[]) => {
    const txtFiles = newFiles.filter(file => file.name.endsWith('.txt'));
    const newFileStatuses: FileStatus[] = txtFiles.map(file => ({
      file,
      status: 'pending'
    }));

    setFiles(prev => {
      const combined = [...prev, ...newFileStatuses];
      // Limit to 20 files
      return combined.slice(0, 20);
    });

    setUploadComplete(false);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      return;
    }

    try {
      setUploading(true);
      setUploadComplete(false);

      // Update all to uploading status
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const })));

      const fileList = files.map(f => f.file);
      const result = await transcriptApi.bulkUpload(fileList, type);

      // Update file statuses based on results
      setFiles(prev => prev.map((fileStatus, index) => {
        const apiResult = result.results[index];
        return {
          ...fileStatus,
          status: apiResult.status as 'success' | 'failed',
          error: apiResult.error || undefined,
          uuid: apiResult.transcript?.uuid
        };
      }));

      setUploadComplete(true);
    } catch (err) {
      // Mark all as failed if there was a global error
      setFiles(prev => prev.map(f => ({
        ...f,
        status: 'failed' as const,
        error: err instanceof Error ? err.message : 'Upload failed'
      })));
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFiles([]);
    setUploadComplete(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusIcon = (status: FileStatus['status']) => {
    switch (status) {
      case 'pending': return '📄';
      case 'uploading': return '⏳';
      case 'success': return '✅';
      case 'failed': return '❌';
    }
  };

  const successCount = files.filter(f => f.status === 'success').length;
  const failedCount = files.filter(f => f.status === 'failed').length;

  return (
    <div className={styles.tabPanel}>
      <h2>Bulk Upload Transcripts</h2>
      <p className={styles.description}>
        Upload multiple .txt files at once (max 20 files, each max 10MB, UTF-8 encoded)
      </p>

      <form onSubmit={handleSubmit} className={styles.form}>
        {/* File Upload Dropzone */}
        <div className={styles.formGroup}>
          <label>Select Files ({files.length}/20)</label>
          <div
            className={`${styles.dropzone} ${dragActive ? styles.dragActive : ''} ${files.length > 0 ? styles.hasFile : ''}`}
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
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={files.length >= 20}
            />
            <div className={styles.dropzoneContent}>
              <p>📁 Drag and drop multiple .txt files here</p>
              <p>or click to browse</p>
              <p className={styles.hint}>
                {files.length >= 20 ? '⚠️ Maximum 20 files reached' : `${20 - files.length} more files allowed`}
              </p>
            </div>
          </div>
        </div>

        {/* Transcript Type */}
        <div className={styles.formGroup}>
          <label htmlFor="bulkType">Transcript Type (applies to ALL files) *</label>
          <select
            id="bulkType"
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
              ? 'All files will be analyzed as B2B sales call transcripts'
              : 'All files will be analyzed as digital user journey logs'}
          </small>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className={styles.formGroup}>
            <label>Selected Files</label>
            <div className={styles.fileList}>
              {files.map((fileStatus, index) => (
                <div key={index} className={`${styles.fileItem} ${styles[fileStatus.status]}`}>
                  <div className={styles.fileItemLeft}>
                    <span className={styles.statusIcon}>{getStatusIcon(fileStatus.status)}</span>
                    <div className={styles.fileItemInfo}>
                      <span className={styles.fileName}>{fileStatus.file.name}</span>
                      <span className={styles.fileSize}>
                        {(fileStatus.file.size / 1024).toFixed(2)} KB
                      </span>
                      {fileStatus.error && (
                        <span className={styles.fileError}>{fileStatus.error}</span>
                      )}
                    </div>
                  </div>
                  <div className={styles.fileItemActions}>
                    {fileStatus.status === 'success' && fileStatus.uuid && (
                      <button
                        type="button"
                        onClick={() => navigate(`/transcripts/${fileStatus.uuid}`)}
                        className={styles.viewButton}
                        title="View transcript"
                      >
                        👁️
                      </button>
                    )}
                    {!uploading && fileStatus.status === 'pending' && (
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className={styles.removeButton}
                        title="Remove file"
                      >
                        ×
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload Summary */}
        {uploadComplete && (
          <div className={styles.uploadSummary}>
            <h3>Upload Complete</h3>
            <div className={styles.summaryStats}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Total:</span>
                <span className={styles.statValue}>{files.length}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>✅ Successful:</span>
                <span className={styles.statValue}>{successCount}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>❌ Failed:</span>
                <span className={styles.statValue}>{failedCount}</span>
              </div>
            </div>
            <div className={styles.summaryActions}>
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
            disabled={files.length === 0 || uploading}
            className={styles.submitButton}
          >
            {uploading ? `Uploading ${files.length} files...` : `Upload ${files.length} Files`}
          </button>
          <button
            type="button"
            onClick={handleReset}
            disabled={uploading}
            className={styles.resetButton}
          >
            Clear All
          </button>
        </div>
      </form>
    </div>
  );
};

export default BulkUploadTranscriptTab;
