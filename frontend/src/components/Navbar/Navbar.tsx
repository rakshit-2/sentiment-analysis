import { useAuth } from '../../contexts/AuthContext';
import styles from './Navbar.module.scss';

interface NavbarProps {
  onToggleSidebar: () => void;
}

const Navbar = ({ onToggleSidebar }: NavbarProps) => {
  const { username, logout } = useAuth();

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarContainer}>
        <button 
          className={styles.toggleButton} 
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <span className={styles.hamburger}></span>
          <span className={styles.hamburger}></span>
          <span className={styles.hamburger}></span>
        </button>

        <div className={styles.navRight}>
          {username && (
            <div className={styles.userSection}>
              <span className={styles.username}>👤 {username}</span>
              <button 
                className={styles.logoutButton}
                onClick={logout}
                title="Logout"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
