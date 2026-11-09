import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkBackendHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const fetchDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

export const fetchTrends = async (days = 30) => {
  const response = await api.get(`/dashboard/trends?days=${days}`);
  return response.data;
};

export const fetchCategories = async () => {
  const response = await api.get('/dashboard/categories');
  return response.data;
};

export const fetchCountries = async () => {
  const response = await api.get('/dashboard/countries');
  return response.data;
};

export const fetchSources = async () => {
  const response = await api.get('/dashboard/sources');
  return response.data;
};

export const fetchSchedulerStatus = async () => {
  const response = await api.get('/scheduler/status');
  return response.data;
};

export default api;
