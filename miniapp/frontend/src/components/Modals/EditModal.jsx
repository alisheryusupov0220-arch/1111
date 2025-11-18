import { useEffect, useState } from 'react';
import { useTelegram } from '../../hooks/useTelegram';

export default function EditModal({ item, onClose, onSave }) {
  const { showAlert, hapticFeedback, user } = useTelegram();
  const [formData, setFormData] = useState({
    date: '',
    amount: '',
    description: '',
    category_id: null,
    account_id: null,
  });

  // Получаем текущий user_id из localStorage
  const currentUserId = localStorage.getItem('current_user_id');
  const isOwner = item && currentUserId && item.user_id === parseInt(currentUserId);

  useEffect(() => {
    if (item) {
      setFormData({
        date: item.date || '',
        amount: item.amount || '',
        description: item.description || '',
        category_id: item.category_id || null,
        account_id: item.account_id || null,
      });
    }
  }, [item]);

  const handleChange = (field) => (event) => {
    setFormData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!isOwner) {
      showAlert?.('❌ Вы можете редактировать только свои операции');
      return;
    }
    
    hapticFeedback?.('medium');

    try {
      await onSave({
        ...formData,
        amount: Number(formData.amount),
      });
      showAlert?.('✅ Операция обновлена!');
      onClose();
    } catch (error) {
      console.error('Ошибка обновления:', error);
      const errorMsg = error.response?.data?.detail || 'Ошибка при обновлении';
      showAlert?.(errorMsg);
    }
  };

  const handleDelete = async () => {
    if (!isOwner) {
      showAlert?.('❌ Вы можете удалять только свои операции');
      return;
    }
    
    if (window.confirm('Удалить эту операцию?')) {
      hapticFeedback?.('heavy');
      try {
        await onSave(null);
        showAlert?.('✅ Операция удалена');
        onClose();
      } catch (error) {
        console.error('Ошибка удаления:', error);
        const errorMsg = error.response?.data?.detail || 'Ошибка при удалении';
        showAlert?.(errorMsg);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end z-50">
      <div className="bg-white w-full rounded-t-3xl p-6 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">✏️ {isOwner ? 'Редактировать' : 'Просмотр'}</h2>
          <button onClick={onClose} className="text-2xl">
            ×
          </button>
        </div>

        {/* Показываем информацию о создателе */}
        {item && (item.created_by_name || item.created_by_username) && (
          <div className="mb-4 p-3 bg-gray-100 rounded-xl">
            <div className="text-sm text-gray-600">
              👤 Создал: <span className="font-medium">{item.created_by_name || item.created_by_username}</span>
            </div>
            {!isOwner && (
              <div className="text-xs text-orange-600 mt-1">
                ⚠️ Вы можете только просматривать эту операцию
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">💰 Сумма:</label>
            <input
              type="number"
              value={formData.amount}
              onChange={handleChange('amount')}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-300 text-lg"
              required
              disabled={!isOwner}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">📅 Дата:</label>
            <input
              type="date"
              value={formData.date}
              onChange={handleChange('date')}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-300"
              required
              disabled={!isOwner}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">📝 Описание:</label>
            <input
              type="text"
              value={formData.description}
              onChange={handleChange('description')}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-300"
              placeholder="Например: Покупка овощей"
              disabled={!isOwner}
            />
          </div>

          {isOwner ? (
            <div className="flex gap-3">
              <button
                type="submit"
                className="flex-1 bg-blue-500 text-white py-4 rounded-xl font-bold text-lg hover:bg-blue-600 transition"
              >
                💾 Сохранить
              </button>
              <button
                type="button"
                onClick={handleDelete}
                className="px-6 bg-red-500 text-white py-4 rounded-xl font-bold text-lg hover:bg-red-600 transition"
              >
                🗑️
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onClose}
              className="w-full bg-gray-500 text-white py-4 rounded-xl font-bold text-lg"
            >
              Закрыть
            </button>
          )}
        </form>
      </div>
    </div>
  );
}