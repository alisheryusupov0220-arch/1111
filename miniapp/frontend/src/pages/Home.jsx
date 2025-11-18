import { useState } from 'react';

export default function Home() {
  const [stats] = useState({
    today_expenses: 150000,
    today_income: 500000,
    balance: 2500000,
  });

  return (
    <div className="p-6 space-y-6 pb-24">
      <h2 className="text-3xl font-bold text-gray-900">Сегодня</h2>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-5 shadow-sm">
          <div className="text-sm text-gray-500 mb-1">Расходы</div>
          <div className="text-2xl font-bold text-red-500">-{stats.today_expenses.toLocaleString()}</div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-sm">
          <div className="text-sm text-gray-500 mb-1">Приходы</div>
          <div className="text-2xl font-bold text-green-500">+{stats.today_income.toLocaleString()}</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-6 shadow-lg">
        <div className="text-sm opacity-90 mb-2">Общий баланс</div>
        <div className="text-4xl font-bold">{stats.balance.toLocaleString()}</div>
        <div className="text-sm opacity-90 mt-1">сум</div>
      </div>
    </div>
  );
}

