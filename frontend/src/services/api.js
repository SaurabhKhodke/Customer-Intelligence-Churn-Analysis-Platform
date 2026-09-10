import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const predict = async (customerData) => {
  const response = await api.post('/predict', customerData);
  return response.data;
};

export const getCustomer = async (customerId) => {
  const response = await api.get(`/customer/${customerId}`);
  return response.data;
};

export const getHighRiskCustomers = async (limit = 100, offset = 0) => {
  const response = await api.get('/customers/high-risk', {
    params: { limit, offset }
  });
  return response.data;
};

export const getRiskSummary = async () => {
  const response = await api.get('/customers/risk-summary');
  return response.data;
};

export const getDashboardSummary = async () => {
  const response = await api.get('/dashboard/summary');
  return response.data;
};

export const getCustomerExplanation = async (customerId) => {
  const response = await api.get(`/customers/${customerId}/explanation`);
  return response.data;
};

export const askAIQuery = async (question) => {
  const response = await api.post('/ai/query', { question });
  return response.data;
};

export default api;
