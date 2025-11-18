import { useEffect, useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

import ChartsView from '../components/Analytics/ChartsView';
import api from '../services/api';

// === DASHBOARD VIEW ===
function DashboardView({ stats, blocks }) {
  
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

  // Получаем данные для блока
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
      {/* Выручка */}
      <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-6">
        <div className="text-sm opacity-90 mb-2">💰 Выручка</div>
        <div className="text-4xl font-bold">{formatNumber(stats.revenue)}</div>
        <div className="text-sm opacity-90 mt-1">сум</div>
      </div>

      {/* Динамические блоки аналитики */}
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

      {/* Prime Cost (если есть food_cost и labor_cost) */}
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

      {/* Прибыль и расходы */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="text-sm text-gray-600 mb-2">💰 Прибыль</div>
          <div className="text-3xl font-bold text-green-600 mb-1">
            {formatNumber(stats.profit)}
          </div>
          <div className="text-sm text-gray-500 mt-2">
            Рентабельность: {stats.profitability}%
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="text-sm text-gray-600 mb-2">📉 Расходы</div>
          <div className="text-3xl font-bold text-red-600 mb-1">
            {formatNumber(stats.total_expenses)}
          </div>
          <div className="text-sm text-gray-500 mt-2">Всего за период</div>
        </div>
      </div>
    </div>
  );
}

// === DETAILED TABLE VIEW ===
function DetailedTableView({ pivotData, blocks }) {
  const [selectedBlock, setSelectedBlock] = useState('all'); // 'all' или код блока

  const [groupBy, setGroupBy] = useState('month'); // 'month' или 'day'
  
  const formatNumber = (num) => {
    return Math.round(num).toLocaleString('ru-RU');
  };

  // Получаем все месяцы из данных
  const getAllMonths = () => {
    const months = new Set();
    Object.keys(pivotData).forEach(month => {
      months.add(month);
    });
    return Array.from(months).sort().reverse(); // От новых к старым
  };

  // Организуем данные: блок -> категория -> месяц -> сумма
  const organizeData = () => {
    const organized = {};

    // Инициализируем структуру для каждого блока
    blocks.forEach(block => {
      organized[block.code] = {
        name: block.name,
        icon: block.icon,
        color: block.color,
        categories: {}
      };
    });

    // Добавляем "Без блока"
    organized['unassigned'] = {
      name: 'Без блока',
      icon: '📦',
      color: 'gray',
      categories: {}
    };

    // Заполняем данными
    Object.keys(pivotData).forEach(month => {
      Object.keys(pivotData[month]).forEach(blockCode => {
        const normalizedCode = blockCode || 'unassigned';
        
        if (!organized[normalizedCode]) {
          organized[normalizedCode] = {
            name: blockCode,
            icon: '📊',
            color: 'gray',
            categories: {}
          };
        }

        Object.keys(pivotData[month][blockCode]).forEach(category => {
          if (!organized[normalizedCode].categories[category]) {
            organized[normalizedCode].categories[category] = {};
          }
          organized[normalizedCode].categories[category][month] = pivotData[month][blockCode][category];
        });
      });
    });

    return organized;
  };

  const organizedData = organizeData();
  const allMonths = getAllMonths();

  // Получаем итог по категории за все месяцы
  const getCategoryTotal = (categoryData) => {
    return Object.values(categoryData).reduce((sum, val) => sum + val, 0);
  };

  // Получаем итог по месяцу для выбранного блока
  const getMonthTotal = (month) => {
    let total = 0;
    const blockData = selectedBlock === 'all' 
      ? organizedData 
      : { [selectedBlock]: organizedData[selectedBlock] };

    Object.values(blockData).forEach(block => {
      Object.values(block.categories).forEach(categoryData => {
        total += categoryData[month] || 0;
      });
    });
    return total;
  };

  // Фильтруем данные по выбранному блоку
  const getFilteredData = () => {
    if (selectedBlock === 'all') {
      // Показываем все категории из всех блоков
      const allCategories = {};
      Object.values(organizedData).forEach(block => {
        Object.entries(block.categories).forEach(([category, data]) => {
          if (!allCategories[category]) {
            allCategories[category] = data;
          } else {
            // Суммируем если категория повторяется в разных блоках
            Object.keys(data).forEach(month => {
              allCategories[category][month] = (allCategories[category][month] || 0) + data[month];
            });
          }
        });
      });
      return allCategories;
    } else {
      return organizedData[selectedBlock]?.categories || {};
    }
  };

  const filteredCategories = getFilteredData();

  // Сортируем категории по общей сумме
  const sortedCategories = Object.entries(filteredCategories)
    .sort((a, b) => getCategoryTotal(b[1]) - getCategoryTotal(a[1]));

  // Получаем общую сумму по блоку
  const getBlockTotal = (blockCode) => {
    const blockData = organizedData[blockCode];
    if (!blockData) return 0;
    
    let total = 0;
    Object.values(blockData.categories).forEach(categoryData => {
      total += getCategoryTotal(categoryData);
    });
    return total;
  };

  if (allMonths.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-2">📭</div>
        <div>Нет данных за период</div>
      </div>
    );
  }

  // Цвета для кнопок
  const getColorClasses = (color, isActive) => {
    const colors = {
      blue: isActive ? 'bg-blue-500 text-white' : 'bg-blue-50 text-blue-700 hover:bg-blue-100',
      emerald: isActive ? 'bg-emerald-500 text-white' : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100',
      green: isActive ? 'bg-green-500 text-white' : 'bg-green-50 text-green-700 hover:bg-green-100',
      yellow: isActive ? 'bg-yellow-500 text-white' : 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100',
      red: isActive ? 'bg-red-500 text-white' : 'bg-red-50 text-red-700 hover:bg-red-100',
      purple: isActive ? 'bg-purple-500 text-white' : 'bg-purple-50 text-purple-700 hover:bg-purple-100',
      gray: isActive ? 'bg-gray-500 text-white' : 'bg-gray-50 text-gray-700 hover:bg-gray-100',
    };
    return colors[color] || colors.gray;
  };

  return (
    <div className="space-y-4">
      {/* Фильтр по блокам - красивые кнопки */}
      <div className="bg-white p-4 rounded-2xl shadow-sm">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Фильтр по блокам:</h3>
        <div className="flex flex-wrap gap-2">
          {/* Кнопка "Все блоки" */}
          <button
            onClick={() => setSelectedBlock('all')}
            className={`px-4 py-2.5 rounded-xl font-medium transition-all shadow-sm ${
              selectedBlock === 'all'
                ? 'bg-blue-500 text-white shadow-lg scale-105'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">📊</span>
              <div className="text-left">
                <div className="text-sm font-bold">Все блоки</div>
                <div className="text-xs opacity-80">
                  {formatNumber(
                    Object.keys(organizedData).reduce(
                      (sum, blockCode) => sum + getBlockTotal(blockCode), 0
                    )
                  )} сум
                </div>
              </div>
            </div>
          </button>

          {/* Кнопки блоков */}
          {blocks.map(block => {
            const blockTotal = getBlockTotal(block.code);
            const isActive = selectedBlock === block.code;
            
            return (
              <button
                key={block.code}
                onClick={() => setSelectedBlock(block.code)}
                className={`px-4 py-2.5 rounded-xl font-medium transition-all shadow-sm ${
                  isActive ? 'shadow-lg scale-105' : ''
                } ${getColorClasses(block.color, isActive)}`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{block.icon}</span>
                  <div className="text-left">
                    <div className="text-sm font-bold">{block.name}</div>
                    <div className="text-xs opacity-80">
                      {blockTotal > 0 ? `${formatNumber(blockTotal)} сум` : 'Нет данных'}
                    </div>
                  </div>
                </div>
              </button>
            );
          })}

          {/* Кнопка "Без блока" если есть данные */}
          {getBlockTotal('unassigned') > 0 && (
            <button
              onClick={() => setSelectedBlock('unassigned')}
              className={`px-4 py-2.5 rounded-xl font-medium transition-all shadow-sm ${
                selectedBlock === 'unassigned'
                  ? 'bg-gray-500 text-white shadow-lg scale-105'
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">📦</span>
                <div className="text-left">
                  <div className="text-sm font-bold">Без блока</div>
                  <div className="text-xs opacity-80">
                    {formatNumber(getBlockTotal('unassigned'))} сум
                  </div>
                </div>
              </div>
            </button>
          )}
        </div>
      </div>

      {/* Таблица */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th className="sticky left-0 bg-gray-50 px-4 py-3 text-left text-sm font-bold text-gray-700 min-w-[200px] z-10">
                  Категория
                </th>
                {allMonths.map(month => (
                  <th key={month} className="px-4 py-3 text-right text-sm font-bold text-gray-700 min-w-[120px]">
                    {month}
                  </th>
                ))}
                <th className="px-4 py-3 text-right text-sm font-bold text-gray-700 bg-blue-50 min-w-[120px]">
                  Итого
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sortedCategories.length === 0 ? (
                <tr>
                  <td colSpan={allMonths.length + 2} className="px-4 py-12 text-center text-gray-400">
                    <div className="text-4xl mb-2">🔍</div>
                    <div>Нет данных для выбранного блока</div>
                  </td>
                </tr>
              ) : (
                <>
                  {sortedCategories.map(([category, categoryData]) => {
                    const total = getCategoryTotal(categoryData);
                    return (
                      <tr key={category} className="hover:bg-gray-50 transition-colors">
                        <td className="sticky left-0 bg-white px-4 py-3 text-sm font-medium text-gray-900 z-10">
                          {category}
                        </td>
                        {allMonths.map(month => (
                          <td key={month} className="px-4 py-3 text-right text-sm text-gray-700">
                            {categoryData[month] ? formatNumber(categoryData[month]) : '-'}
                          </td>
                        ))}
                        <td className="px-4 py-3 text-right text-sm font-bold text-gray-900 bg-blue-50">
                          {formatNumber(total)}
                        </td>
                      </tr>
                    );
                  })}
                  
                  {/* Итоговая строка */}
                  <tr className="bg-blue-100 font-bold">
                    <td className="sticky left-0 bg-blue-100 px-4 py-3 text-sm z-10">
                      ИТОГО
                    </td>
                    {allMonths.map(month => (
                      <td key={month} className="px-4 py-3 text-right text-sm">
                        {formatNumber(getMonthTotal(month))}
                      </td>
                    ))}
                    <td className="px-4 py-3 text-right text-sm bg-blue-200">
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
      </div>

      {/* Легенда */}
      <div className="bg-white p-4 rounded-xl text-sm text-gray-600">
        <div className="font-semibold mb-2">💡 Подсказка:</div>
        <ul className="space-y-1 text-xs">
          <li>• Кликайте на блоки для фильтрации категорий</li>
          <li>• Прокрутите таблицу влево-вправо для просмотра всех месяцев</li>
          <li>• Категории отсортированы по общей сумме расходов</li>
        </ul>
      </div>
    </div>
  );
}

// === MAIN ANALYTICS COMPONENT ===
export default function Analytics() {
  const [tab, setTab] = useState('dashboard');
  
  const [period, setPeriod] = useState('30');
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
  }, [period, customStart, customEnd, blocks]);

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
    
    if (period === 'custom' && customStart && customEnd) {
      params = { 
        start_date: customStart.toISOString().split('T')[0], 
        end_date: customEnd.toISOString().split('T')[0] 
      };
    } else if (period !== 'custom') { 
      params = { days: parseInt(period) };
    } else {
      setLoading(false);
      return;
    }

    try {
      const dbData = await api.getDashboard(params);
      console.log('Dashboard data from API:', dbData);
      setDashboardData(dbData);
      
      const pvData = await api.getPivotTable(params);
      console.log('PivotTable data from API:', pvData);
      setPivotData(pvData);
      
    } catch (error) {
      console.error('Ошибка загрузки аналитики:', error);
    } finally {
      setLoading(false);
    }
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
          <option value="7">Последние 7 дней</option>
          <option value="14">Последние 14 дней</option>
          <option value="30">Последние 30 дней</option>
          <option value="custom">Произвольный</option>
        </select>
        
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
          onClick={() => setTab('charts')}
          className={`px-4 py-2 rounded-xl font-medium ${
            tab === 'charts' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          📈 Графики
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
      
      {tab === 'charts' && <ChartsView />}
    </div>
  );
}
