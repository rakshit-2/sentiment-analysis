import { Link, useLocation } from 'react-router-dom';
import styles from './Sidebar.module.scss';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Backdrop overlay */}
      <div 
        className={`${styles.backdrop} ${isOpen ? styles.backdropOpen : ''}`}
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${isOpen ? styles.sidebarOpen : ''}`}>
        <div className={styles.sidebarHeader}>
          <h2>Menu</h2>
          <button 
            className={styles.closeButton} 
            onClick={onClose}
            aria-label="Close sidebar"
          >
            ×
          </button>
        </div>
        
        <nav className={styles.sidebarNav}>
          <ul>
            <li>
              <Link 
                to="/dashboard" 
                className={isActive('/dashboard') ? styles.active : ''}
                onClick={onClose}
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link 
                to="/analysis" 
                className={isActive('/analysis') ? styles.active : ''}
                onClick={onClose}
              >
                Analysis
              </Link>
            </li>
            <li>
              <Link 
                to="/transcripts" 
                className={isActive('/transcripts') ? styles.active : ''}
                onClick={onClose}
              >
                Transcripts
              </Link>
            </li>
            <li>
              <Link 
                to="/settings" 
                className={isActive('/settings') ? styles.active : ''}
                onClick={onClose}
              >
                Settings
              </Link>
            </li>
          </ul>
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
