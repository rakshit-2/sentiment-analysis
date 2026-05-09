import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const USERNAME_KEY = 'auth_username';
const LOGIN_TIME_KEY = 'auth_login_time';
const SESSION_DURATION = 60 * 60 * 1000; // 1 hour in milliseconds

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check if session is still valid
  const isSessionValid = (): boolean => {
    const loginTime = sessionStorage.getItem(LOGIN_TIME_KEY);
    if (!loginTime) return false;

    const elapsed = Date.now() - parseInt(loginTime);
    return elapsed < SESSION_DURATION;
  };

  // Auto-logout timer
  useEffect(() => {
    if (isAuthenticated) {
      const loginTime = sessionStorage.getItem(LOGIN_TIME_KEY);
      if (loginTime) {
        const elapsed = Date.now() - parseInt(loginTime);
        const remaining = SESSION_DURATION - elapsed;

        if (remaining > 0) {
          const timer = setTimeout(() => {
            logout();
            alert('Session expired. Please login again.');
          }, remaining);

          return () => clearTimeout(timer);
        } else {
          logout();
        }
      }
    }
  }, [isAuthenticated]);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      const token = sessionStorage.getItem(TOKEN_KEY);
      const storedUsername = sessionStorage.getItem(USERNAME_KEY);

      if (token && storedUsername && isSessionValid()) {
        setIsAuthenticated(true);
        setUsername(storedUsername);
      } else {
        // Clear invalid session
        sessionStorage.removeItem(TOKEN_KEY);
        sessionStorage.removeItem(USERNAME_KEY);
        sessionStorage.removeItem(LOGIN_TIME_KEY);
        setIsAuthenticated(false);
        setUsername(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();

      // Store token and user info in sessionStorage
      sessionStorage.setItem(TOKEN_KEY, data.access_token);
      sessionStorage.setItem(USERNAME_KEY, data.username);
      sessionStorage.setItem(LOGIN_TIME_KEY, Date.now().toString());

      setIsAuthenticated(true);
      setUsername(data.username);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USERNAME_KEY);
    sessionStorage.removeItem(LOGIN_TIME_KEY);
    setIsAuthenticated(false);
    setUsername(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const getAuthToken = (): string | null => {
  return sessionStorage.getItem(TOKEN_KEY);
};
