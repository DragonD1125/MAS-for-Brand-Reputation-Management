import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Monitoring API
export const monitoringApi = {
  getMetrics: () => api.get('/monitoring/metrics'),
  getSystemHealth: () => api.get('/monitoring/health'),
  getAlerts: () => api.get('/monitoring/alerts'),
  getPerformance: () => api.get('/monitoring/performance'),
};

// Mentions API  
export const mentionsApi = {
  getMentions: (params?: any) => api.get('/mentions/', { params }),
  getMentionById: (id: string) => api.get(`/mentions/${id}`),
  updateMention: (id: string, data: any) => api.put(`/mentions/${id}`, data),
};

// Analytics API
export const analyticsApi = {
  getSentimentTrends: (params?: any) => api.get('/analytics/sentiment-trends', { params }),
  getBrandMetrics: (brandId: string, params?: any) => api.get(`/analytics/brand-metrics/${brandId}`, { params }),
  getCrisisDetection: () => api.get('/analytics/crisis-detection'),
  getTopKeywords: (params?: any) => api.get('/analytics/keywords', { params }),
};

// Alerts API
export const alertsApi = {
  getAlerts: (params?: any) => api.get('/alerts/', { params }),
  getAlertById: (id: string) => api.get(`/alerts/${id}`),
  updateAlert: (id: string, data: any) => api.put(`/alerts/${id}`, data),
  acknowledgeAlert: (id: string) => api.post(`/alerts/${id}/acknowledge`),
};

// Human-in-the-Loop API
export const hitlApi = {
  getQueue: () => api.get('/responses/queue'),
  approveResponse: (id: string, data: any) => api.post(`/responses/${id}/approve`, data),
  rejectResponse: (id: string, data: any) => api.post(`/responses/${id}/reject`, data),
  getResponseById: (id: string) => api.get(`/responses/${id}`),
};

// Brands API
export const brandsApi = {
  getBrands: () => api.get('/brands/'),
  createBrand: (data: any) => api.post('/brands/', data),
  updateBrand: (id: string, data: any) => api.put(`/brands/${id}`, data),
  deleteBrand: (id: string) => api.delete(`/brands/${id}`),
};

export default api;
