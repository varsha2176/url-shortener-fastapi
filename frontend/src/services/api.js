import axios from 'axios';

// ✅ Always use environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: false,
});

/* REQUEST INTERCEPTOR */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* RESPONSE INTERCEPTOR */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

/* AUTH APIs */
export const authAPI = {
  register: (data) => api.post('/api/v1/auth/register', data),
  
  login: ({ username, password }) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  
  getCurrentUser: () => api.get('/api/v1/auth/me'),
};

/* URL APIs */
export const urlAPI = {
  create: (data) => api.post('/api/v1/urls/', data),
  getAll: (skip = 0, limit = 100) => api.get(`/api/v1/urls/?skip=${skip}&limit=${limit}`),
  getOne: (shortCode) => api.get(`/api/v1/urls/${shortCode}`),
  update: (shortCode, data) => api.patch(`/api/v1/urls/${shortCode}`, data),
  delete: (shortCode) => api.delete(`/api/v1/urls/${shortCode}`),
};

/* ANALYTICS APIs */
export const analyticsAPI = {
  getClicks: (shortCode, skip = 0, limit = 100) => 
    api.get(`/api/v1/analytics/${shortCode}/clicks?skip=${skip}&limit=${limit}`),
  getSummary: (shortCode, days = 30) => 
    api.get(`/api/v1/analytics/${shortCode}/summary?days=${days}`),
  getEnhanced: (shortCode) => 
    api.get(`/api/v1/analytics/${shortCode}/enhanced`),
  getTopUrls: (limit = 10, days = 30) => 
    api.get(`/api/v1/analytics/top?limit=${limit}&days=${days}`),
  getDashboard: () => 
    api.get('/api/v1/analytics/dashboard'),
};

export default api;