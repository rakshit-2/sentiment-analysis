import type {
  Analysis,
  Transcript,
  RecentAnalysesResponse,
  TrendsResponse,
  DetailedMetricsResponse,
} from '../types/api.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Get auth token from sessionStorage
function getAuthToken(): string | null {
  return sessionStorage.getItem('auth_token');
}

// Generic fetch wrapper with error handling
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle unauthorized responses
      if (response.status === 401) {
        // Clear session and redirect to login
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_username');
        sessionStorage.removeItem('auth_login_time');
        window.location.href = '/login';
      }
      
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Analysis API
export const analysisApi = {
  // Get recent analyses (last N hours)
  getRecent: async (hours: number = 24): Promise<RecentAnalysesResponse> => {
    return fetchApi<RecentAnalysesResponse>(`/analyses/stats/recent?hours=${hours}`);
  },

  // Get analysis trends (weekly aggregation)
  getTrends: async (weeks: number = 8): Promise<TrendsResponse> => {
    return fetchApi<TrendsResponse>(`/analyses/stats/trends?weeks=${weeks}`);
  },

  // Get detailed metrics trends
  getDetailedMetrics: async (weeks: number = 8): Promise<DetailedMetricsResponse> => {
    return fetchApi<DetailedMetricsResponse>(`/analyses/stats/detailed-metrics?weeks=${weeks}`);
  },

  // Get single analysis by UUID
  getById: async (uuid: string): Promise<Analysis> => {
    return fetchApi<Analysis>(`/analyses/${uuid}`);
  },

  // List all analyses with pagination
  list: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<Analysis[]> => {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);

    const query = queryParams.toString();
    return fetchApi<Analysis[]>(`/analyses${query ? `?${query}` : ''}`);
  },

  // Get analyses for a transcript
  getByTranscript: async (transcriptUuid: string): Promise<Analysis[]> => {
    return fetchApi<Analysis[]>(`/analyses/transcript/${transcriptUuid}`);
  },
};

// Transcript API
export const transcriptApi = {
  // Get single transcript by UUID
  getById: async (uuid: string): Promise<Transcript> => {
    return fetchApi<Transcript>(`/transcripts/${uuid}`);
  },

  // List all transcripts with pagination
  list: async (params?: {
    skip?: number;
    limit?: number;
    source?: string;
  }): Promise<Transcript[]> => {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.source) queryParams.append('source', params.source);

    const query = queryParams.toString();
    return fetchApi<Transcript[]>(`/transcripts${query ? `?${query}` : ''}`);
  },

  // Upload transcript
  upload: async (file: File, title?: string, description?: string): Promise<Transcript> => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);

    const token = getAuthToken();
    const url = `${API_BASE_URL}/transcripts/upload`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      
      if (response.status === 401) {
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_username');
        sessionStorage.removeItem('auth_login_time');
        window.location.href = '/login';
      }
      
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  },
};

// Trigger Analysis API
export const triggerApi = {
  // Trigger analysis for unprocessed transcripts
  triggerAnalysis: async (batchSize?: number): Promise<{
    message: string;
    task_id: string;
    batch_size: number;
    status: string;
    monitor_url: string;
  }> => {
    const params = batchSize ? `?batch_size=${batchSize}` : '';
    const url = `${API_BASE_URL}/analyses/trigger${params}`;
    const token = getAuthToken();
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Trigger failed' }));
      
      if (response.status === 401) {
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_username');
        sessionStorage.removeItem('auth_login_time');
        window.location.href = '/login';
      }
      
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  },
};
