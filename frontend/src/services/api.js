import axios from 'axios';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
    ? 'https://threatview-xtk4.onrender.com/api'
    : 'http://localhost:8000/api');

const api = axios.create({
  baseURL: API_BASE_URL,
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
