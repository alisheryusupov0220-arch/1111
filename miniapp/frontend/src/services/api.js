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
    // Accepts telegram_id and optional extra user data (username, first_name, last_name)
    verifyUser: (telegram_id, userData = {}) =>
      api.post('/auth/verify', { telegram_id, ...userData }),

  // === УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ===
  getAllUsers: () => api.get('/users'),
  
  updateUserRole: (userId, role) => 
    api.put(`/users/${userId}/role?role=${role}`),
  
  toggleUserStatus: (userId, isActive) => 
    api.put(`/users/${userId}/status?is_active=${isActive}`),

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

  // === АНАЛИТИКА ===
  
  // --- ИЗМЕНЕНО ---
  // Теперь принимает объект params (например { days: 30 } или { start_date: '...', end_date: '...' })
  async getDashboard(params = {}) {
    const { data } = await api.get('/analytics/dashboard', { params });
    return data;
  },

  // Теперь принимает объект params
  async getPivotTable(params = {}) {
  const { data } = await api.get('/analytics/pivot', { params });
  return data;
},


async getCellDetails(period, categoryName, groupBy = 'month') {
  const { data } = await api.get('/analytics/cell-details', {
    params: { period, category_name: categoryName, group_by: groupBy }
  });
  return data;
},

  // --- КОНЕЦ ИЗМЕНЕНИЙ ---

  async getTrendData(days = 30) {
    const { data } = await api.get(`/analytics/trend?days=${days}`);
    return data;
  },

  // === TIMELINE УПРАВЛЕНИЕ ===
  async updateTimelineItem(id, payload) {
    const { data } = await api.put(`/timeline/${id}`, payload);
    return data;
  },

  async deleteTimelineItem(id) {
    const { data } = await api.delete(`/timeline/${id}`);
    return data;
  },

  // === ОТЧЁТЫ КАССИРА ===
  async createReport(report) {
    const { data } = await api.post('/reports', report);
    return data;
  },

  // ============ УПРАВЛЕНИЕ КАТЕГОРИЯМИ ============
  async getAllExpenseCategories() {
    const { data } = await api.get('/categories/expense/all');
    return data;
  },
  async createExpenseCategory(payload) {
    const { data } = await api.post('/categories/expense', payload);
    return data;
  },
  async updateExpenseCategory(id, payload) {
    const { data } = await api.put(`/categories/expense/${id}`, payload);
    return data;
  },
  async deleteExpenseCategory(id) {
    const { data } = await api.delete(`/categories/expense/${id}`);
    return data;
  },

  // ============ СИНХРОНИЗИРОВАННОЕ УПРАВЛЕНИЕ НАИМЕНОВАНИЯМИ ============
  // (обновляет ОБЕ таблицы: expense_categories И income_categories)

  async getAllUnifiedCategories() {
   const { data } = await api.get('/categories/unified/all');
   return data;
  },

  async createUnifiedCategory(payload) {
   const { data } = await api.post('/categories/unified', payload);
   return data;
  },

  async updateUnifiedCategory(id, payload) {
   const { data } = await api.put(`/categories/unified/${id}`, payload);
   return data;
  },

  async deleteUnifiedCategory(id) {
   const { data } = await api.delete(`/categories/unified/${id}`);
   return data;
  },

  // ============ УПРАВЛЕНИЕ СЧЕТАМИ ============
  async getAllAccounts() {
    const { data } = await api.get('/accounts/all');
    return data;
  },
  async createAccount(payload) {
    const { data } = await api.post('/accounts', payload);
    return data;
  },
  async updateAccount(id, payload) {
    const { data } = await api.put(`/accounts/${id}`, payload);
    return data;
  },
  async deleteAccount(id) {
    const { data } = await api.delete(`/accounts/${id}`);
    return data;
  },

  // ============ АНАЛИТИКА СЧЕТОВ ============
  async getAccountBalance(accountId) {
   const { data } = await api.get(`/analytics/accounts/${accountId}/balance`);
   return data;
  },

  async getAccountMovements(accountId, params = {}) {
   const { data } = await api.get(`/analytics/accounts/${accountId}/movements`, { params });
   return data;
  },

  async getAccountChart(accountId, params = {}) {
   const { data } = await api.get(`/analytics/accounts/${accountId}/chart`, { params });
   return data;
  },

  // ============ НАСТРОЙКИ АНАЛИТИКИ ============
  async getAnalyticsSettings() {
    const { data } = await api.get('/analytics/settings');
    return data;
  },

  async createAnalyticsSetting(payload) {
    const { data } = await api.post('/analytics/settings', payload);
    return data;
  },

  async updateAnalyticsSetting(id, payload) {
    const { data } = await api.put(`/analytics/settings/${id}`, payload);
    return data;
  },

  async deleteAnalyticsSetting(id) {
    const { data } = await api.delete(`/analytics/settings/${id}`);
    return data;
  },
  // ============ УПРАВЛЕНИЕ БЛОКАМИ АНАЛИТИКИ ============
  async getAnalyticBlocks() {
    const { data } = await api.get('/analytics/blocks');
    return data;
  },
  async createAnalyticBlock(payload) {
    const { data } = await api.post('/analytics/blocks', payload);
    return data;
  },
  async updateAnalyticBlock(id, payload) {
    const { data } = await api.put(`/analytics/blocks/${id}`, payload);
    return data;
  },
  async deleteAnalyticBlock(id) {
    const { data } = await api.delete(`/analytics/blocks/${id}`);
    return data;
  },
  // === КАССИРСКИЕ ОТЧЁТЫ ===
  getCashierReports: (params) => api.get('/cashier/reports', { params }),
  
  getCashierReportDetails: (reportId) => api.get(`/cashier/reports/${reportId}`),
  
  getLocations: () => api.get('/cashier/locations'),
  
  getPaymentMethods: () => api.get('/cashier/payment-methods'),
};