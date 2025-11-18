import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Добавить telegram_id в каждый запрос
api.interceptors.request.use((config) => {
  const telegramId = localStorage.getItem('telegram_id');
  if (telegramId) {
    config.headers['X-Telegram-Id'] = telegramId;
  }
  return config;
});

export default {
  // === АУТЕНТИФИКАЦИЯ ===
  async verifyUser(telegram_id) {
    const { data } = await api.post('/auth/verify', { telegram_id });
    return data;
  },

  // === TIMELINE ===
  async getTimeline(params = {}) {
    const { data } = await api.get('/timeline', { params });
    return data;
  },

  // === РАСХОДЫ ===
  async createExpense(expense) {
    const { data } = await api.post('/operations/expense', expense);
    return data;
  },

  // === ПРИХОДЫ ===
  async createIncome(income) {
    const { data } = await api.post('/operations/income', income);
    return data;
  },

  // === ИНКАСАЦИЯ 🆕 ===
  async createIncasation(incasation) {
    const { data } = await api.post('/transfers/incasation', incasation);
    return data;
  },

  // === ПЕРЕВОДЫ 🆕 ===
  async createTransfer(transfer) {
    const { data } = await api.post('/transfers/transfer', transfer);
    return data;
  },

  // === СПРАВОЧНИКИ ===
  async getAccounts() {
    const { data } = await api.get('/accounts');
    return data;
  },

  async getCategories(type = 'expense') {
    const { data } = await api.get(`/categories/${type}`);
    return data;
  },

  // === ОТЧЁТЫ КАССИРА ===
  async createReport(report) {
    const { data } = await api.post('/reports', report);
    return data;
  }
};
