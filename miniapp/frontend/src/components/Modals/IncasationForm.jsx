import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useTelegram } from '../../hooks/useTelegram';
import SelectWithSearch from '../UI/SelectWithSearch';

export default function IncasationForm({
  onClose,
  onSuccess,
  onBack,
  icon = '🏦',
  title = 'Инкасация'
}) {
  const { hapticFeedback, showAlert } = useTelegram();
  const [loading, setLoading] = useState(false);
  const [cashAccounts, setCashAccounts] = useState([]);
  const [bankAccounts, setBankAccounts] = useState([]);

  const [form, setForm] = useState({
    from_account_id: null,
    to_account_id: null,
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
      // ИСПРАВЛЕНО: используем 'type' вместо 'account_type'
      setCashAccounts(accounts.filter((a) => a.account_type === 'cash'));
      setBankAccounts(accounts.filter((a) => a.account_type === 'bank'));
    } catch (error) {
      console.error('Ошибка загрузки счетов:', error);
      showAlert?.('❌ Не удалось загрузить счета');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.from_account_id || !form.to_account_id || !form.amount) {
      alert('Заполните все поля');
      return;
    }

    const amountValue = parseFloat(form.amount);
    if (Number.isNaN(amountValue) || amountValue <= 0) {
      alert('Сумма должна быть больше 0');
      return;
    }

    setLoading(true);
    hapticFeedback('medium');

    try {
      await api.createIncasation({
        date: form.date,
        from_account_id: form.from_account_id,
        to_account_id: form.to_account_id,
        amount: amountValue,
        description: form.description?.trim() || null,
      });

      hapticFeedback('success');
      showAlert?.('✅ Инкасация создана!');
      onSuccess?.();
    } catch (error) {
      console.error('Ошибка инкасации:', error);
      hapticFeedback('error');
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
            options={cashAccounts}
            value={form.from_account_id}
            onChange={(id) => setForm((prev) => ({ ...prev, from_account_id: Number(id) }))}
            label="💵 Откуда (Касса):"
            placeholder="Выберите кассу"
          />

          <SelectWithSearch
            options={bankAccounts}
            value={form.to_account_id}
            onChange={(id) => setForm((prev) => ({ ...prev, to_account_id: Number(id) }))}
            label="🏦 Куда (Банк):"
            placeholder="Выберите банк"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💰 Сумма инкасации:
            </label>
            <input
              type="number"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              placeholder="500000"
              className="w-full p-4 border border-gray-200 rounded-xl text-lg font-medium focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📝 Комментарий:
            </label>
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Инкасация за день"
              className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="
                flex-1 bg-blue-500 text-white p-4 rounded-xl 
                font-semibold text-lg
                disabled:opacity-50 disabled:cursor-not-allowed
                active:scale-95 transition-all
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              "
            >
              {loading ? '⏳ Обработка...' : '✅ Инкассировать'}
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
