import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useTelegram } from '../../hooks/useTelegram';

export default function IncasationForm({ onClose, onSuccess }) {
  const { hapticFeedback, showAlert } = useTelegram();
  const [loading, setLoading] = useState(false);
  const [cashAccounts, setCashAccounts] = useState([]);
  const [bankAccounts, setBankAccounts] = useState([]);

  const [form, setForm] = useState({
    from_account_id: '',
    to_account_id: '',
    amount: '',
    description: 'Инкасация',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const accounts = await api.getAccounts();
      setCashAccounts(accounts.filter(a => a.account_type === 'cash'));
      setBankAccounts(accounts.filter(a => a.account_type === 'bank'));
    } catch (error) {
      console.error('Ошибка загрузки счетов:', error);
      showAlert('Не удалось загрузить счета');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!form.from_account_id || !form.to_account_id || !form.amount) {
      showAlert('Заполните все поля');
      return;
    }

    if (parseFloat(form.amount) <= 0) {
      showAlert('Сумма должна быть больше 0');
      return;
    }

    setLoading(true);
    hapticFeedback('medium');

    try {
      await api.createIncasation({
        ...form,
        amount: parseFloat(form.amount)
      });

      hapticFeedback('success');
      showAlert('✅ Инкасация выполнена!');
      onSuccess();
    } catch (error) {
      console.error('Ошибка инкасации:', error);
      hapticFeedback('error');
      showAlert('❌ Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const selectedCash = cashAccounts.find(a => a.id === parseInt(form.from_account_id));

  return (
    <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
      {/* Откуда (Касса) */}
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-700">
          💵 Откуда (Касса):
        </label>
        <select
          value={form.from_account_id}
          onChange={(e) => setForm({...form, from_account_id: e.target.value})}
          className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        >
          <option value="">Выберите кассу</option>
          {cashAccounts.map(acc => (
            <option key={acc.id} value={acc.id}>
              {acc.name} {acc.balance ? `(${acc.balance.toLocaleString()} сум)` : ''}
            </option>
          ))}
        </select>
        {selectedCash && selectedCash.balance && (
          <p className="text-sm text-gray-500 mt-1">
            Доступно: {selectedCash.balance.toLocaleString()} сум
          </p>
        )}
      </div>

      {/* Куда (Банк) */}
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-700">
          🏦 Куда (Банк):
        </label>
        <select
          value={form.to_account_id}
          onChange={(e) => setForm({...form, to_account_id: e.target.value})}
          className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        >
          <option value="">Выберите банк</option>
          {bankAccounts.map(acc => (
            <option key={acc.id} value={acc.id}>
              {acc.name}
            </option>
          ))}
        </select>
      </div>

      {/* Сумма */}
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-700">
          💰 Сумма инкасации:
        </label>
        <input
          type="number"
          value={form.amount}
          onChange={(e) => setForm({...form, amount: e.target.value})}
          placeholder="500000"
          className="w-full p-4 border border-gray-200 rounded-xl text-lg font-medium focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
          min="0"
          step="1000"
        />
      </div>

      {/* Дата */}
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-700">
          📅 Дата:
        </label>
        <input
          type="date"
          value={form.date}
          onChange={(e) => setForm({...form, date: e.target.value})}
          className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      {/* Комментарий */}
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-700">
          📝 Комментарий:
        </label>
        <input
          type="text"
          value={form.description}
          onChange={(e) => setForm({...form, description: e.target.value})}
          placeholder="Инкасация за день"
          className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Кнопки */}
      <div className="flex gap-3 pt-4 sticky bottom-0 bg-white pb-4">
        <button
          type="submit"
          disabled={loading}
          className="
            flex-1 bg-blue-500 text-white p-4 rounded-xl 
            font-semibold text-lg
            disabled:opacity-50 disabled:cursor-not-allowed
            active:scale-95 transition-all
          "
        >
          {loading ? '⏳ Обработка...' : '✅ Инкассировать'}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="px-6 bg-gray-200 rounded-xl font-medium"
        >
          Отмена
        </button>
      </div>
    </form>
  );
}
