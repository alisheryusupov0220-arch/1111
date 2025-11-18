import { useEffect, useState } from 'react';
import api from '../../services/api';
import { useTelegram } from '../../hooks/useTelegram';
import SelectWithSearch from '../UI/SelectWithSearch';

export default function TransferForm({
  onClose,
  onSuccess,
  onBack,
  icon = '🔄',
  title = 'Перевод'
}) {
  const { hapticFeedback, showAlert } = useTelegram();
  const [loading, setLoading] = useState(false);
  const [accounts, setAccounts] = useState([]);

  const [form, setForm] = useState({
    from_account_id: null,
    to_account_id: null,
    amount: '',
    commission_amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await api.getAccounts();
      setAccounts(data || []);
    } catch (error) {
      console.error('Ошибка загрузки счетов:', error);
      showAlert?.('❌ Не удалось загрузить счета');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.from_account_id || !form.to_account_id || !form.amount) {
      alert('Заполните обязательные поля');
      return;
    }

    if (form.from_account_id === form.to_account_id) {
      alert('Выберите разные счета');
      return;
    }

    const amountValue = parseFloat(form.amount);
    const commissionValue = 0;

    if (Number.isNaN(amountValue) || amountValue <= 0) {
      alert('Сумма должна быть больше 0');
      return;
    }

    if (Number.isNaN(commissionValue) || commissionValue < 0) {
      alert('Комиссия должна быть неотрицательна');
      return;
    }

    setLoading(true);
    hapticFeedback('medium');

    try {
      await api.createTransfer({
        date: form.date,
        from_account_id: form.from_account_id,
        to_account_id: form.to_account_id,
        amount: amountValue,
        commission_amount: 0,
        description: form.description?.trim() || null,
      });

      hapticFeedback('success');
      showAlert?.('✅ Перевод создан!');
      onSuccess?.();
    } catch (error) {
      console.error('Ошибка перевода:', error);
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

        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto max-h-[70vh]">
          <SelectWithSearch
            options={accounts}
            value={form.from_account_id}
            onChange={(id) => setForm((prev) => ({ ...prev, from_account_id: Number(id) }))}
            label="🔻 Счёт списания:"
            placeholder="Выберите счёт"
          />

          <SelectWithSearch
            options={accounts}
            value={form.to_account_id}
            onChange={(id) => setForm((prev) => ({ ...prev, to_account_id: Number(id) }))}
            label="🔺 Счёт зачисления:"
            placeholder="Выберите счёт"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                💰 Сумма:
              </label>
              <input
                type="number"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                placeholder="300000"
                className="w-full p-4 border border-gray-200 rounded-xl text-lg font-medium focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
                min="0"
                step="1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                💸 Комиссия:
              </label>
              <input
                type="number"
                value={form.commission_amount}
                onChange={(e) => setForm({ ...form, commission_amount: e.target.value })}
                placeholder="0"
                className="w-full p-4 border border-gray-200 rounded-xl text-lg font-medium focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                min="0"
                step="1000"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 Дата:
            </label>
            <input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
              placeholder="Например: Перевод в филиал"
              className="w-full p-4 border border-gray-200 rounded-xl text-base focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="
                flex-1 bg-purple-500 text-white p-4 rounded-xl 
                font-semibold text-lg
                disabled:opacity-50 disabled:cursor-not-allowed
                active:scale-95 transition-all
                focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2
              "
            >
              {loading ? '⏳ Перевод...' : '✅ Выполнить'}
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
