import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { Login } from './components/Auth';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import AnalysisList from './components/AnalysisList';
import AnalysisDetail from './components/AnalysisDetail';
import TranscriptsList from './components/TranscriptsList';
import TranscriptDetail from './components/TranscriptDetail';
import Settings from './components/Settings';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analysis"
            element={
              <ProtectedRoute>
                <Layout>
                  <AnalysisList />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analysis/:uuid"
            element={
              <ProtectedRoute>
                <Layout>
                  <AnalysisDetail />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/transcripts"
            element={
              <ProtectedRoute>
                <Layout>
                  <TranscriptsList />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/transcripts/:uuid"
            element={
              <ProtectedRoute>
                <Layout>
                  <TranscriptDetail />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Layout>
                  <Settings />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
