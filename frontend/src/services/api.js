import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkBackendHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
