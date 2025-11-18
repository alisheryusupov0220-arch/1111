import { useEffect, useState, useMemo } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import AccountsView from '../components/Analytics/AccountsView';
import api from '../services/api';

// === DASHBOARD VIEW С ГРАФИКАМИ ===
function DashboardView({ stats, blocks }) {
  const [chartData, setChartData] = useState([]);
  const [chartDays, setChartDays] = useState(30);
  
  useEffect(() => {
    loadChartData();
  }, [chartDays]);

  const loadChartData = async () => {
    try {
      const result = await api.getTrendData(chartDays);
      setChartData(result);
    } catch (error) {
      console.error('Ошибка загрузки графиков:', error);
    }
  };

  const preparedChartData = useMemo(
    () =>
      chartData.map((item) => ({
        ...item,
        profit: (item.revenue || 0) - (item.expenses || 0),
      })),
    [chartData]
  );

  const formatDateTick = (value) =>
    new Date(value).toLocaleDateString('ru', { day: '2-digit', month: 'short' });

  const formatAmountTick = (value) => `${(value / 1000).toFixed(0)}K`;

  const tooltipFormatter = (value) => `${Number(value || 0).toLocaleString()} сум`;
  const tooltipLabelFormatter = (value) =>
    new Date(value).toLocaleDateString('ru', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    emerald: 'bg-emerald-50 border-emerald-200',
    green: 'bg-green-50 border-green-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    red: 'bg-red-50 border-red-200',
    purple: 'bg-purple-50 border-purple-200',
    gray: 'bg-gray-50 border-gray-200',
  };

  const getStatus = (percent, block) => {
    if (percent <= block.threshold_good) return { color: block.color, text: '✅ Отлично' };
    if (percent <= block.threshold_warning) return { color: 'yellow', text: '⚠️ Норма' };
    return { color: 'red', text: '❌ Проблема' };
  };

  const formatNumber = (num) => {
    return Math.round(num).toLocaleString('ru-RU');
  };

  const getBlockData = (blockCode) => {
    const key = `${blockCode}_percentage`;
    const amountKey = blockCode;
    return {
      percentage: stats[key] || 0,
      amount: stats[amountKey] || 0
    };
  };

  return (
    <div className="space-y-6">
      {/* ========== ГЛАВНЫЕ МЕТРИКИ ========== */}
      
      {/* Прибыль */}
      <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl p-8 shadow-lg">
        <div className="text-sm opacity-90 mb-2">💰 Прибыль</div>
        <div className="text-5xl font-bold mb-2">{formatNumber(stats.profit)}</div>
        <div className="text-sm opacity-90">сум</div>
        <div className="mt-4 pt-4 border-t border-green-400 opacity-90">
          <div className="text-sm">Рентабельность: <span className="font-bold text-lg">{stats.profitability}%</span></div>
        </div>
      </div>

      {/* Оборот и Расходы */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-6 shadow-lg">
          <div className="text-sm opacity-90 mb-2">💵 Оборот</div>
          <div className="text-4xl font-bold mb-1">{formatNumber(stats.revenue)}</div>
          <div className="text-xs opacity-90 mt-1">Грязная выручка</div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-2xl p-6 shadow-lg">
          <div className="text-sm opacity-90 mb-2">📉 Расходы</div>
          <div className="text-4xl font-bold mb-1">{formatNumber(stats.total_expenses)}</div>
          <div className="text-xs opacity-90 mt-1">Всего за период</div>
        </div>
      </div>

      {/* ========== БЛОКИ АНАЛИТИКИ ========== */}
      
      <div className="pt-4">
        <h3 className="text-lg font-bold text-gray-700 mb-4">📊 Анализ расходов</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {blocks.filter(b => b.code !== 'other').map(block => {
            const data = getBlockData(block.code);
            const status = getStatus(data.percentage, block);
            const statusClass = colorClasses[status.color] || colorClasses.gray;

            return (
              <div key={block.code} className={`rounded-2xl p-5 border-2 ${statusClass}`}>
                <div className="text-sm text-gray-600 mb-2">
                  {block.icon} {block.name}
                </div>
                <div className="text-3xl font-bold mb-1">{data.percentage}%</div>
                <div className="text-lg font-semibold text-gray-700 mb-2">
                  {formatNumber(data.amount)} сум
                </div>
                <div className="text-sm mt-2">{status.text}</div>
                <div className="text-xs text-gray-500 mt-1">
                  Норма: {block.threshold_good}-{block.threshold_warning}%
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Prime Cost */}
      {stats.prime_cost_percentage !== undefined && (
        <div className={`rounded-2xl p-6 border-2 ${
          stats.prime_cost_percentage <= 55 ? colorClasses.emerald :
          stats.prime_cost_percentage <= 65 ? colorClasses.yellow :
          colorClasses.red
        }`}>
          <div className="text-sm text-gray-600 mb-2">💵 Prime Cost (основные затраты)</div>
          <div className="text-4xl font-bold mb-1">{stats.prime_cost_percentage}%</div>
          <div className="text-2xl font-semibold text-gray-700 mb-2">
            {formatNumber(stats.prime_cost)} сум
          </div>
          <div className="text-sm mt-2">
            {stats.prime_cost_percentage <= 55 ? '✅ Отлично' :
             stats.prime_cost_percentage <= 65 ? '⚠️ Норма' : '❌ Проблема'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Норма: 55-65%</div>
        </div>
      )}

      {/* ========== ГРАФИКИ ========== */}
      
      <div className="pt-6 border-t-2 border-gray-200">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">📈 Графики</h3>
        
        {/* Переключатель периода для графиков */}
        <div className="flex gap-2 mb-4">
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setChartDays(d)}
              className={`px-4 py-2 rounded-xl font-medium ${
                chartDays === d ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              {d} дней
            </button>
          ))}
        </div>

        {/* График выручки и расходов */}
        <div className="bg-white rounded-2xl p-6 shadow-sm mb-6">
          <h4 className="text-lg font-bold mb-4">💰 Динамика выручки и расходов</h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={preparedChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={formatDateTick} />
              <YAxis tickFormatter={formatAmountTick} />
              <Tooltip formatter={tooltipFormatter} labelFormatter={tooltipLabelFormatter} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#10B981" name="Выручка" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="expenses" stroke="#EF4444" name="Расходы" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* График прибыли */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h4 className="text-lg font-bold mb-4">📊 Прибыль по дням</h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={preparedChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={formatDateTick} />
              <YAxis tickFormatter={formatAmountTick} />
              <Tooltip formatter={tooltipFormatter} labelFormatter={tooltipLabelFormatter} />
              <Line type="monotone" dataKey="profit" stroke="#3B82F6" name="Прибыль" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// === DETAILED TABLE VIEW ===
function DetailedTableView({ pivotData, blocks }) {
  const [selectedBlock, setSelectedBlock] = useState('all');
  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, data: null, loading: false });

  const formatNumber = (num) => {
    return Math.round(num).toLocaleString('ru-RU');
  };

  const formatDate = (dateStr) => {
    const [year, month, day] = dateStr.split('-');
    const months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
    return `${parseInt(day)} ${months[parseInt(month) - 1]}`;
  };

  const getAllPeriods = () => {
    const periods = new Set();
    Object.keys(pivotData).forEach(period => {
      periods.add(period);
    });
    return Array.from(periods).sort().reverse();
  };

  const organizeData = () => {
    const organized = {};

    blocks.forEach(block => {
      organized[block.code] = {
        name: block.name,
        icon: block.icon,
        color: block.color,
        categories: {}
      };
    });

    organized['unassigned'] = {
      name: 'Без блока',
      icon: '📦',
      color: 'gray',
      categories: {}
    };

    Object.keys(pivotData).forEach(period => {
      Object.keys(pivotData[period]).forEach(blockCode => {
        const normalizedCode = blockCode || 'unassigned';
        
        if (!organized[normalizedCode]) {
          organized[normalizedCode] = {
            name: blockCode,
            icon: '📊',
            color: 'gray',
            categories: {}
          };
        }

        Object.keys(pivotData[period][blockCode]).forEach(category => {
          if (!organized[normalizedCode].categories[category]) {
            organized[normalizedCode].categories[category] = {};
          }
          organized[normalizedCode].categories[category][period] = pivotData[period][blockCode][category];
        });
      });
    });

    return organized;
  };

  const organizedData = organizeData();
  const allPeriods = getAllPeriods();

  const getCategoryTotal = (categoryData) => {
    return Object.values(categoryData).reduce((sum, val) => sum + val, 0);
  };

  const getPeriodTotal = (period) => {
    let total = 0;
    const blockData = selectedBlock === 'all' 
      ? organizedData 
      : { [selectedBlock]: organizedData[selectedBlock] };

    Object.values(blockData).forEach(block => {
      Object.values(block.categories).forEach(categoryData => {
        total += categoryData[period] || 0;
      });
    });
    return total;
  };

  const getFilteredData = () => {
    if (selectedBlock === 'all') {
      const allCategories = {};
      Object.values(organizedData).forEach(block => {
        Object.entries(block.categories).forEach(([category, data]) => {
          if (!allCategories[category]) {
            allCategories[category] = data;
          } else {
            Object.keys(data).forEach(period => {
              allCategories[category][period] = (allCategories[category][period] || 0) + data[period];
            });
          }
        });
      });
      return allCategories;
    }
    return organizedData[selectedBlock]?.categories || {};
  };

  const filteredCategories = getFilteredData();

  const handleCellMouseEnter = async (e, period, categoryName) => {
    const rect = e.target.getBoundingClientRect();
    setTooltip({ 
      show: true, 
      x: rect.left + rect.width / 2, 
      y: rect.top, 
      data: null, 
      loading: true 
    });

    try {
      const details = await api.getCellDetails(period, categoryName, 'day');
      setTooltip(prev => ({ ...prev, data: details, loading: false }));
    } catch (error) {
      console.error('Ошибка загрузки деталей ячейки:', error);
      setTooltip(prev => ({ ...prev, data: [], loading: false }));
    }
  };

  const handleCellMouseLeave = () => {
    setTooltip({ show: false, x: 0, y: 0, data: null, loading: false });
  };

  const sortedCategories = Object.entries(filteredCategories).sort((a, b) => 
    getCategoryTotal(b[1]) - getCategoryTotal(a[1])
  );

  return (
    <div className="space-y-4">
      {/* Фильтры по блокам */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedBlock('all')}
          className={`px-4 py-2 rounded-xl font-medium transition-all ${
            selectedBlock === 'all'
              ? 'bg-blue-500 text-white shadow-lg'
              : 'bg-white border border-gray-200 hover:border-blue-300'
          }`}
        >
          📊 Все блоки
        </button>
        {blocks.map(block => (
          <button
            key={block.code}
            onClick={() => setSelectedBlock(block.code)}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${
              selectedBlock === block.code
                ? 'bg-blue-500 text-white shadow-lg'
                : 'bg-white border border-gray-200 hover:border-blue-300'
            }`}
          >
            {block.icon} {block.name}
          </button>
        ))}
      </div>

      {/* Таблица */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700 sticky left-0 bg-gray-50 z-10 border-r border-gray-200">
                  Наименование
                </th>
                {allPeriods.map(period => (
                  <th key={period} className="px-4 py-3 text-right font-medium text-gray-600 whitespace-nowrap">
                    {formatDate(period)}
                  </th>
                ))}
                <th className="px-4 py-3 text-right font-semibold text-gray-700 bg-blue-50 sticky right-0 border-l border-gray-200">
                  Итого
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedCategories.length === 0 ? (
                <tr>
                  <td colSpan={allPeriods.length + 2} className="px-4 py-12 text-center text-gray-400">
                    <div className="text-4xl mb-2">📭</div>
                    <div>Нет данных для отображения</div>
                  </td>
                </tr>
              ) : (
                <>
                  {sortedCategories.map(([category, data]) => (
                    <tr key={category} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900 sticky left-0 bg-white z-10 border-r border-gray-100">
                        {category}
                      </td>
                      {allPeriods.map(period => (
                        <td 
                          key={period} 
                          className="px-4 py-3 text-right text-gray-700 whitespace-nowrap cursor-pointer hover:bg-blue-50 transition-colors"
                          onMouseEnter={(e) => data[period] && handleCellMouseEnter(e, period, category)}
                          onMouseLeave={handleCellMouseLeave}
                        >
                          {data[period] ? formatNumber(data[period]) : '-'}
                        </td>
                      ))}
                      <td className="px-4 py-3 text-right font-semibold text-gray-900 bg-blue-50 sticky right-0 border-l border-gray-200">
                        {formatNumber(getCategoryTotal(data))}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-blue-100 font-bold">
                    <td className="px-4 py-3 sticky left-0 bg-blue-100 z-10 border-r border-blue-200">
                      ИТОГО
                    </td>
                    {allPeriods.map(period => (
                      <td key={period} className="px-4 py-3 text-right">
                        {formatNumber(getPeriodTotal(period))}
                      </td>
                    ))}
                    <td className="px-4 py-3 text-right bg-blue-200">
                      {formatNumber(
                        Object.values(filteredCategories).reduce(
                          (sum, cat) => sum + getCategoryTotal(cat), 0
                        )
                      )}
                    </td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
        </div>

        {/* Tooltip */}
        {tooltip.show && (
          <div
            className="fixed z-50 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 max-w-sm"
            style={{
              left: `${tooltip.x}px`,
              top: `${tooltip.y}px`,
              transform: 'translate(-50%, -100%)',
              pointerEvents: 'none'
            }}
          >
            {tooltip.loading ? (
              <div className="text-sm text-gray-500">Загрузка...</div>
            ) : tooltip.data && tooltip.data.length > 0 ? (
              <div className="space-y-2">
                <div className="font-semibold text-gray-900 text-sm border-b pb-2">
                  Операции ({tooltip.data.length})
                </div>
                <div className="max-h-64 overflow-y-auto space-y-2">
                  {tooltip.data.map((op, idx) => (
                    <div key={idx} className="text-xs border-l-2 border-blue-400 pl-2 py-1">
                      <div className="font-medium text-gray-900">{op.description}</div>
                      <div className="text-gray-600">{formatNumber(op.amount)} сум</div>
                      <div className="text-gray-400 text-[10px]">{op.date}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">Нет операций</div>
            )}
          </div>
        )}
      </div>

      {/* Легенда */}
      <div className="bg-white p-4 rounded-xl text-sm text-gray-600">
        <div className="font-semibold mb-2">💡 Подсказка:</div>
        <ul className="space-y-1 text-xs">
          <li>• Выберите период сверху (7 дней, 30 дней, По месяцам, Произвольный)</li>
          <li>• Кликайте на блоки для фильтрации наименований</li>
          <li>• <strong>Наведите курсор на ячейку</strong> чтобы увидеть детали операций</li>
          <li>• Прокрутите таблицу влево-вправо для просмотра всех дней</li>
          <li>• Наименования отсортированы по общей сумме расходов</li>
        </ul>
      </div>
    </div>
  );
}

// === MAIN ANALYTICS COMPONENT ===
export default function Analytics() {
  const [tab, setTab] = useState('dashboard');
  
  const [period, setPeriod] = useState('month'); // ИЗМЕНЕНО: по умолчанию "month"
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const [customStart, setCustomStart] = useState(null);
  const [customEnd, setCustomEnd] = useState(null);
  const [dashboardData, setDashboardData] = useState({});
  const [pivotData, setPivotData] = useState({});
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBlocks();
  }, []);

  useEffect(() => {
    if (blocks.length > 0) {
      loadData();
    }
  }, [period, selectedMonth, customStart, customEnd, blocks]);

  const loadBlocks = async () => {
    try {
      const data = await api.getAnalyticBlocks();
      setBlocks(data || []);
    } catch (error) {
      console.error('Ошибка загрузки блоков:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    setDashboardData({});
    setPivotData({});

    let params = {};
    
    if (period === 'month' && selectedMonth) {
      const year = selectedMonth.getFullYear();
      const month = selectedMonth.getMonth() + 1;
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const lastDay = new Date(year, month, 0).getDate();
      const endDate = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
      
      params = { 
        start_date: startDate, 
        end_date: endDate 
      };
    } else if (period === 'custom' && customStart && customEnd) {
      params = { 
        start_date: customStart.toISOString().split('T')[0], 
        end_date: customEnd.toISOString().split('T')[0] 
      };
    } else if (period !== 'custom' && period !== 'month') { 
      params = { days: parseInt(period) };
    } else {
      setLoading(false);
      return;
    }

    try {
      const dbData = await api.getDashboard(params);
      console.log('Dashboard data from API:', dbData);
      setDashboardData(dbData);
      
      const pvData = await api.getPivotTable({ ...params, group_by: 'day' });
      console.log('PivotTable data from API:', pvData);
      setPivotData(pvData);
      
    } catch (error) {
      console.error('Ошибка загрузки аналитики:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatSelectedMonth = () => {
    if (!selectedMonth) return '';
    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    return `${months[selectedMonth.getMonth()]} ${selectedMonth.getFullYear()}`;
  };

  return (
    <div className="p-6 pb-24 space-y-6">
      <h2 className="text-3xl font-bold">📊 Аналитика</h2>

      {/* Выбор периода */}
      <div className="bg-white p-4 rounded-2xl shadow-sm space-y-3">
        <label className="font-medium text-gray-700">Период:</label>
        <select 
          value={period} 
          onChange={(e) => setPeriod(e.target.value)} 
          className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="month">📅 По месяцам</option>
          <option value="7">Последние 7 дней</option>
          <option value="30">Последние 30 дней</option>
          <option value="custom">Произвольный</option>
        </select>
        
        {period === 'month' && (
          <div>
            <label className="block text-sm text-gray-600 mb-2">Выберите месяц:</label>
            <DatePicker
              selected={selectedMonth}
              onChange={date => setSelectedMonth(date)}
              dateFormat="MMMM yyyy"
              showMonthYearPicker
              className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="text-sm text-gray-500 mt-2">
              📅 Выбран: {formatSelectedMonth()}
            </div>
          </div>
        )}
        
        {period === 'custom' && (
          <div className="flex gap-2">
            <DatePicker 
              selected={customStart} 
              onChange={date => setCustomStart(date)} 
              placeholderText="Дата начала"
              className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              dateFormat="yyyy-MM-dd"
            />
            <DatePicker 
              selected={customEnd} 
              onChange={date => setCustomEnd(date)} 
              placeholderText="Дата конца"
              className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              dateFormat="yyyy-MM-dd"
            />
          </div>
        )}
      </div>

      {/* Вкладки */}
      <div className="flex gap-2">
        <button
          onClick={() => setTab('dashboard')}
          className={`px-4 py-2 rounded-xl font-medium ${
            tab === 'dashboard' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          📊 Dashboard
        </button>
        <button
          onClick={() => setTab('table')}
          className={`px-4 py-2 rounded-xl font-medium ${
            tab === 'table' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          📋 Таблица
        </button>
        <button
          onClick={() => setTab('accounts')}
          className={`px-4 py-2 rounded-xl font-medium ${
            tab === 'accounts' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          💳 Счета
        </button>
      </div>

      {/* Контент вкладок */}
      {tab === 'dashboard' && (
        loading ? (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-2">⏳</div>
            <div>Загрузка...</div>
          </div>
        ) : dashboardData.revenue === undefined ? (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-2">⚠️</div>
            <div>Данные не загружены</div>
          </div>
        ) : (
          <DashboardView stats={dashboardData} blocks={blocks} />
        )
      )}
      
      {tab === 'table' && (
        loading ? (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-2">⏳</div>
            <div>Загрузка...</div>
          </div>
        ) : (
          <DetailedTableView pivotData={pivotData} blocks={blocks} />
        )
      )}
      
      {tab === 'accounts' && <AccountsView />}
    </div>
  );
}
