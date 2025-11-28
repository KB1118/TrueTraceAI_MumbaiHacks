/**
 * API client and authentication helpers.
 */
import axios, { AxiosInstance } from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with credentials to send cookies
const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // Important: send cookies with requests
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear cookies and redirect to login
      if (typeof window !== 'undefined') {
        Cookies.remove('user_id');
        Cookies.remove('username');
        // Only redirect if not already on login page
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/auth/register', { email, username, password });
    return response.data;
  },

  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    const { user_id, username: user } = response.data;
    
    // Store session info in cookies so the frontend can detect auth state immediately.
    // These cookies share the localhost domain, so they'll be sent to the FastAPI backend too.
    Cookies.set('user_id', user_id.toString(), {
      expires: 7,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/'
    });
    Cookies.set('username', user, { 
      expires: 7,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/'
    });
    
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
    Cookies.remove('user_id');
    Cookies.remove('username');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Crisis API
export const crisisAPI = {
  list: async (status?: string, page: number = 1, pageSize: number = 20) => {
    const params: any = { page, page_size: pageSize };
    if (status) params.status_filter = status;
    const response = await api.get('/crises', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await api.get(`/crises/${id}`);
    return response.data;
  },
};

// Cluster API
export const clusterAPI = {
  listByCrisis: async (crisisId: number) => {
    const response = await api.get(`/crises/${crisisId}/clusters`);
    return response.data;
  },
};

// Claim API
export const claimAPI = {
  list: async (crisisId?: number, verdict?: string, page: number = 1, pageSize: number = 20) => {
    const params: any = { page, page_size: pageSize };
    if (crisisId) params.crisis_id = crisisId;
    if (verdict) params.verdict = verdict;
    const response = await api.get('/claims', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await api.get(`/claims/${id}`);
    return response.data;
  },
};

// Verification API
export const verifyAPI = {
  verify: async (text: string) => {
    const response = await api.post('/verify', { text });
    return response.data;
  },
};

// Pipeline API
export const pipelineAPI = {
  trigger: async () => {
    const response = await api.post('/pipeline/trigger', { force: false });
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/pipeline/status');
    return response.data;
  },
};

export default api;

