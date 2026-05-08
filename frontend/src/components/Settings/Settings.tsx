import { useState } from 'react';
import UploadTranscriptTab from './UploadTranscriptTab';
import TriggerAnalysisTab from './TriggerAnalysisTab';
import styles from './Settings.module.scss';

type TabType = 'upload' | 'trigger';

const Settings = () => {
  const [activeTab, setActiveTab] = useState<TabType>('upload');

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Settings</h1>
        <p className={styles.subtitle}>Manage transcripts and trigger analysis</p>
      </header>

      {/* Tab Navigation */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'upload' ? styles.active : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Transcript
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'trigger' ? styles.active : ''}`}
          onClick={() => setActiveTab('trigger')}
        >
          Trigger Analysis
        </button>
      </div>

      {/* Tab Content */}
      <div className={styles.tabContent}>
        {activeTab === 'upload' && <UploadTranscriptTab />}
        {activeTab === 'trigger' && <TriggerAnalysisTab />}
      </div>
    </div>
  );
};

export default Settings;
