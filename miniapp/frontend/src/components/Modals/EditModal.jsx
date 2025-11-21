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

        {/* Информация об авторе операции */}
        <div className={`mb-4 p-3 rounded-lg ${
          isOwner 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-yellow-50 border border-yellow-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">
                {isOwner ? '✏️ Ваша операция' : '👤 Чужая операция'}
              </span>
              <span className="text-sm text-gray-600">
                • Создал: {item.created_by_name || item.created_by_username || 'Неизвестно'}
              </span>
            </div>
            {!isOwner && (
              <span className="text-xs text-yellow-700 font-medium">
                🔒 Только просмотр
              </span>
            )}
          </div>
        </div>

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

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={!isOwner}
              className={`flex-1 py-3 rounded-xl font-semibold transition ${
                isOwner
                  ? 'bg-purple-500 text-white hover:bg-purple-600'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              {isOwner ? '💾 Сохранить изменения' : '🔒 Редактирование запрещено'}
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={!isOwner}
              className={`flex-1 py-3 rounded-xl font-semibold transition ${
                isOwner
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              {isOwner ? '🗑️ Удалить операцию' : '🔒 Удаление запрещено'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}