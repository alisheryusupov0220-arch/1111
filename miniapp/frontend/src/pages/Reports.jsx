import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import ReportDetailsModal from '../components/Modals/ReportDetailsModal';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  
  // Фильтры
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    locationId: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [reportsRes, locationsRes] = await Promise.all([
        apiService.getCashierReports(filters),
        apiService.getLocations()
      ]);
      setReports(reportsRes.data);
      setLocations(locationsRes.data);
    } catch (error) {
      console.error('Error loading reports:', error);
      alert('Ошибка загрузки отчётов');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const applyFilters = () => {
    loadData();
  };

  const openReportDetails = async (reportId) => {
    try {
      const response = await apiService.getCashierReportDetails(reportId);
      setSelectedReport(response.data);
      setShowDetails(true);
    } catch (error) {
      console.error('Error loading report details:', error);
      alert('Ошибка загрузки деталей отчёта');
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('ru-RU').format(num);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      open: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '⏳ Открыт' },
      closed: { bg: 'bg-green-100', text: 'text-green-800', label: '✅ Закрыт' },
      verified: { bg: 'bg-blue-100', text: 'text-blue-800', label: '✔️ Проверен' }
    };
    const badge = badges[status] || badges.open;
    return (
      <span className={`text-xs px-2 py-1 rounded-full ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-500">Загрузка отчётов...</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-4 pb-24">
      {/* Заголовок */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">📋 Отчёты кассиров</h1>
        <div className="text-sm text-gray-500">
          Всего: {reports.length}
        </div>
      </div>

      {/* Фильтры */}
      <div className="bg-white rounded-xl p-4 mb-6 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              С даты
            </label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleFilterChange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              По дату
            </label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleFilterChange('endDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Точка продаж
            </label>
            <select
              value={filters.locationId}
              onChange={(e) => handleFilterChange('locationId', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Все точки</option>
              {locations.map(loc => (
                <option key={loc.id} value={loc.id}>{loc.name}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={applyFilters}
              className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition font-medium"
            >
              🔍 Применить
            </button>
          </div>
        </div>
      </div>

      {/* Список отчётов */}
      <div className="space-y-3">
        {reports.map((report) => (
          <div
            key={report.id}
            onClick={() => openReportDetails(report.id)}
            className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition cursor-pointer border-2 border-transparent hover:border-purple-200"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="text-lg font-semibold">
                    📅 {formatDate(report.report_date)}
                  </h3>
                  {getStatusBadge(report.status)}
                </div>
                <div className="text-sm text-gray-600">
                  📍 {report.location_name || 'Точка не указана'}
                </div>
                <div className="text-sm text-gray-500">
                  👤 Кассир: {report.cashier_name || report.cashier_username || 'Неизвестно'}
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">
                  {formatNumber(report.total_sales)} сум
                </div>
                <div className="text-xs text-gray-500">Общая выручка</div>
              </div>
            </div>

            {/* Краткая информация */}
            <div className="grid grid-cols-3 gap-4 pt-3 border-t border-gray-100">
              <div>
                <div className="text-xs text-gray-500">Факт. касса</div>
                <div className="text-sm font-semibold text-gray-700">
                  {formatNumber(report.cash_actual || 0)} сум
                </div>
              </div>
              
              <div>
                <div className="text-xs text-gray-500">Разница</div>
                <div className={`text-sm font-semibold ${
                  (report.cash_difference || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {report.cash_difference ? formatNumber(report.cash_difference) + ' сум' : '-'}
                </div>
              </div>
              
              <div>
                <div className="text-xs text-gray-500">Создан</div>
                <div className="text-sm text-gray-600">
                  {new Date(report.created_at).toLocaleTimeString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {reports.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-4">📋</div>
          <div>Отчёты не найдены</div>
          <div className="text-sm mt-2">Попробуйте изменить фильтры</div>
        </div>
      )}

      {/* Модальное окно с деталями */}
      {showDetails && selectedReport && (
        <ReportDetailsModal
          report={selectedReport}
          onClose={() => {
            setShowDetails(false);
            setSelectedReport(null);
          }}
        />
      )}
    </div>
  );
};

export default Reports;
