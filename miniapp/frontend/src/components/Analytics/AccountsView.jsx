import { useEffect, useState } from 'react';
import DatePicker from 'react-datepicker';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import api from '../../services/api';

export default function AccountsView() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [period, setPeriod] = useState('month');
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const [customStart, setCustomStart] = useState(null);
  const [customEnd, setCustomEnd] = useState(null);
  
  const [balance, setBalance] = useState(null);
  const [movements, setMovements] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      loadAccountData();
    }
  }, [selectedAccount, period, selectedMonth, customStart, customEnd]);

  const loadAccounts = async () => {
    try {
      const data = await api.getAccounts();
      setAccounts(data);
      if (data.length > 0) {
        setSelectedAccount(data[0].id);
      }
    } catch (error) {
      console.error('Ошибка загрузки счетов:', error);
    }
  };

  const loadAccountData = async () => {
    if (!selectedAccount) return;
    
    setLoading(true);
    
    try {
      // Получить текущий баланс
      const balanceData = await api.getAccountBalance(selectedAccount);
      setBalance(balanceData);
      
      // Параметры периода
      let params = {};
      if (period === 'month' && selectedMonth) {
        const year = selectedMonth.getFullYear();
        const month = selectedMonth.getMonth() + 1;
        const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
        const lastDay = new Date(year, month, 0).getDate();
        const endDate = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
        params = { start_date: startDate, end_date: endDate };
      } else if (period === 'custom' && customStart && customEnd) {
        params = {
          start_date: customStart.toISOString().split('T')[0],
          end_date: customEnd.toISOString().split('T')[0]
        };
      } else if (period !== 'custom' && period !== 'month') {
        params = { days: parseInt(period) };
      }
      
      // Получить движения за период
      const movementsData = await api.getAccountMovements(selectedAccount, params);
      setMovements(movementsData);
      
      // Получить данные для графика
      const chartData = await api.getAccountChart(selectedAccount, params);
      setChartData(chartData);
      
    } catch (error) {
      console.error('Ошибка загрузки данных счёта:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    return Math.round(num).toLocaleString('ru-RU');
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { 
      day: '2-digit', 
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDateTick = (value) =>
    new Date(value).toLocaleDateString('ru', { day: '2-digit', month: 'short' });

  const formatAmountTick = (value) => {
    if (Math.abs(value) >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    return `${(value / 1000).toFixed(0)}K`;
  };

  const tooltipFormatter = (value) => `${Number(value || 0).toLocaleString()} сум`;

  const formatSelectedMonth = () => {
    if (!selectedMonth) return '';
    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    return `${months[selectedMonth.getMonth()]} ${selectedMonth.getFullYear()}`;
  };

  const getOperationIcon = (op) => {
    if (op.type === 'income') return '📥';
    if (op.type === 'expense') return '📤';
    if (op.type === 'transfer' || op.type === 'incasation') {
      return op.direction === 'in' ? '📥' : '📤';
    }
    return '💳';
  };

  const getOperationType = (op) => {
    if (op.type === 'income') return 'Приход';
    if (op.type === 'expense') return 'Расход';
    if (op.type === 'incasation') return op.direction === 'in' ? 'Инкасация (вход)' : 'Инкасация (выход)';
    if (op.type === 'transfer') return op.direction === 'in' ? 'Перевод (вход)' : 'Перевод (выход)';
    return op.type;
  };

  return (
    <div className="space-y-6">
      {/* Выбор счёта и периода */}
      <div className="bg-white p-4 rounded-2xl shadow-sm space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Счёт:</label>
          <select
            value={selectedAccount || ''}
            onChange={(e) => setSelectedAccount(parseInt(e.target.value))}
            className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {accounts.map(acc => (
              <option key={acc.id} value={acc.id}>
                {acc.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Период:</label>
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
        </div>

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

      {loading ? (
        <div className="text-center py-12 text-gray-400">
          <div className="text-4xl mb-2">⏳</div>
          <div>Загрузка...</div>
        </div>
      ) : balance && movements ? (
        <>
          {/* Текущий баланс */}
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-8 shadow-lg">
            <div className="text-sm opacity-90 mb-2">💰 Текущий баланс</div>
            <div className="text-5xl font-bold mb-2">{formatNumber(balance.balance)}</div>
            <div className="text-sm opacity-90">сум (в реальном времени)</div>
          </div>

          {/* Приходы и расходы за период */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl p-6 shadow-lg">
              <div className="text-sm opacity-90 mb-2">📥 Приходы</div>
              <div className="text-4xl font-bold mb-1">+{formatNumber(movements.total_income)}</div>
              <div className="text-xs opacity-90 mt-1">За период</div>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-2xl p-6 shadow-lg">
              <div className="text-sm opacity-90 mb-2">📤 Расходы</div>
              <div className="text-4xl font-bold mb-1">-{formatNumber(movements.total_expense)}</div>
              <div className="text-xs opacity-90 mt-1">За период</div>
            </div>
          </div>

          {/* График динамики */}
          {chartData.length > 0 && (
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-bold mb-4">📊 Динамика баланса</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={formatDateTick} />
                  <YAxis tickFormatter={formatAmountTick} />
                  <Tooltip formatter={tooltipFormatter} />
                  <Line 
                    type="monotone" 
                    dataKey="balance" 
                    stroke="#3B82F6" 
                    name="Баланс" 
                    strokeWidth={2} 
                    dot={false} 
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Таймлайн операций */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-lg font-bold mb-4">🕐 Таймлайн операций</h3>
            
            {movements.operations.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <div className="text-4xl mb-2">📭</div>
                <div>Нет операций за выбранный период</div>
              </div>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {movements.operations.map((op, idx) => (
                  <div
                    key={op.id}
                    className={`flex items-start gap-3 p-4 rounded-xl border-l-4 ${
                      op.balance_change > 0
                        ? 'bg-green-50 border-green-500'
                        : 'bg-red-50 border-red-500'
                    }`}
                  >
                    <div className="text-2xl mt-1">{getOperationIcon(op)}</div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="font-medium text-gray-900">
                            {op.description || getOperationType(op)}
                          </div>
                          <div className="text-sm text-gray-500 mt-1">
                            {formatDate(op.date)}
                          </div>
                        </div>
                        <div className={`text-lg font-bold ${
                          op.balance_change > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {op.balance_change > 0 ? '+' : ''}{formatNumber(op.balance_change)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <div className="text-4xl mb-2">⚠️</div>
          <div>Выберите счёт для просмотра аналитики</div>
        </div>
      )}
    </div>
  );
}
