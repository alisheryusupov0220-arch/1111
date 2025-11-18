import { useEffect, useState } from 'react';
import api from '../../services/api';
import { useTelegram } from '../../hooks/useTelegram';
import SelectWithSearch from '../UI/SelectWithSearch';

export default function ExpenseForm({
  onClose,
  onSuccess,
  onBack,
  icon = '📉',
  title = 'Расход'
}) {
  const { hapticFeedback, showAlert } = useTelegram();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [accounts, setAccounts] = useState([]);

  const [form, setForm] = useState({
    category_id: null,
    account_id: null,
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadDictionaries();
  }, []);

  const loadDictionaries = async () => {
    try {
      const [cats, accs] = await Promise.all([
        api.getCategories('expense'),
        api.getAccounts(),
      ]);
      setCategories(cats || []);
      setAccounts(accs || []);
    } catch (error) {
      console.error('Ошибка загрузки справочников:', error);
      showAlert?.('❌ Не удалось загрузить справочники');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.category_id || !form.account_id || !form.amount) {
      alert('Заполните обязательные поля');
      return;
    }

    const numericAmount = parseFloat(form.amount);
    if (Number.isNaN(numericAmount) || numericAmount <= 0) {
      alert('Сумма должна быть больше 0');
      return;
    }

    setLoading(true);
    hapticFeedback?.('medium');

    try {
      await api.createExpense({
        date: form.date,
        category_id: form.category_id,
        account_id: form.account_id,
        amount: numericAmount,
        description: form.description?.trim() || null,
      });

      hapticFeedback?.('success');
      showAlert?.('✅ Расход добавлен!');
      onSuccess?.();
    } catch (error) {
      console.error('Ошибка добавления расхода:', error);
      hapticFeedback?.('error');
      showAlert?.('❌ Ошибка: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleBackdrop = () => {
    (onBack || onClose)?.();
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end"
      onClick={handleBackdrop}
    >
      <div
        className="bg-white w-full rounded-t-3xl max-h-[90vh] overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b">
          <button
            type="button"
            onClick={handleBackdrop}
            className="text-2xl text-gray-400 hover:text-gray-600 transition-colors"
          >
            ←
          </button>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-xl text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto">
          <SelectWithSearch
            options={categories}
            value={form.category_id}
            onChange={(id) => setForm((prev) => ({ ...prev, category_id: Number(id) }))}
            label="📁 Наименование:"
            placeholder="Выберите наименование"
          />

          <SelectWithSearch
            options={accounts}
            value={form.account_id}
            onChange={(id) => setForm((prev) => ({ ...prev, account_id: Number(id) }))}
            label="🏦 Счёт списания:"
            placeholder="Выберите счёт"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💰 Сумма:
            </label>
            <input
              type="number"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              placeholder="150000"
              className="w-full p-4 border border-gray-200 rounded-xl text-lg font-medium focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
              min="0"
              step="1000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 Дата:
            </label>
            <input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📝 Описание:
            </label>
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Например: Покупка сырья"
              className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="
                flex-1 bg-red-500 text-white p-4 rounded-xl 
                font-semibold text-lg
                disabled:opacity-50 disabled:cursor-not-allowed
                active:scale-95 transition-all
                focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
              "
            >
              {loading ? '⏳ Обработка...' : '✅ Добавить расход'}
            </button>
            <button
              type="button"
              onClick={handleBackdrop}
              className="px-6 py-4 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 active:scale-95 transition-all"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

