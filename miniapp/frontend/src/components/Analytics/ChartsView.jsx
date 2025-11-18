import { useEffect, useMemo, useState } from 'react';
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
import api from '../../services/api';

export default function ChartsView() {
  const [data, setData] = useState([]);
  const [days, setDays] = useState(30);

  useEffect(() => {
    loadData();
  }, [days]);

  const loadData = async () => {
    try {
      const result = await api.getTrendData(days);
      setData(result);
    } catch (error) {
      console.error('Ошибка:', error);
    }
  };

  const preparedData = useMemo(
    () =>
      data.map((item) => ({
        ...item,
        profit: (item.revenue || 0) - (item.expenses || 0),
      })),
    [data]
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

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        {[7, 14, 30].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-4 py-2 rounded-xl font-medium ${
              days === d ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            {d} дней
          </button>
        ))}
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">💰 Динамика выручки и расходов</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={preparedData}>
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

      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">📊 Прибыль по дням</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={preparedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={formatDateTick} />
            <YAxis tickFormatter={formatAmountTick} />
            <Tooltip formatter={tooltipFormatter} labelFormatter={tooltipLabelFormatter} />
            <Line type="monotone" dataKey="profit" stroke="#3B82F6" name="Прибыль" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


