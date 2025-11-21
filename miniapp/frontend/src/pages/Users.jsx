import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState(null);

  const roleColors = {
    owner: 'bg-purple-100 text-purple-800',
    manager: 'bg-blue-100 text-blue-800',
    accountant: 'bg-green-100 text-green-800',
    cashier: 'bg-gray-100 text-gray-800'
  };

  const roleNames = {
    owner: 'Владелец',
    manager: 'Менеджер',
    accountant: 'Бухгалтер',
    cashier: 'Кассир'
  };

  useEffect(() => {
    const userId = localStorage.getItem('current_user_id');
    setCurrentUserId(parseInt(userId));
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAllUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
      if (error.response?.status === 403) {
        alert('Доступ запрещён. Только владелец или менеджер может просматривать пользователей.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    if (!window.confirm(`Изменить роль на "${roleNames[newRole]}"?`)) {
      return;
    }

    try {
      await apiService.updateUserRole(userId, newRole);
      alert('Роль обновлена');
      loadUsers();
    } catch (error) {
      console.error('Error updating role:', error);
      if (error.response?.status === 403) {
        alert('Доступ запрещён. Только владелец может менять роли.');
      } else {
        alert('Ошибка при обновлении роли');
      }
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    const newStatus = !currentStatus;
    const action = newStatus ? 'активировать' : 'деактивировать';
    
    if (!window.confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} пользователя?`)) {
      return;
    }

    try {
      await apiService.toggleUserStatus(userId, newStatus);
      alert(`Пользователь ${action}ован`);
      loadUsers();
    } catch (error) {
      console.error('Error toggling status:', error);
      if (error.response?.status === 403) {
        alert('Доступ запрещён. Только владелец может менять статусы.');
      } else if (error.response?.status === 400) {
        alert('Нельзя деактивировать самого себя');
      } else {
        alert('Ошибка при изменении статуса');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 pb-24">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">👥 Пользователи</h1>
        <div className="text-sm text-gray-500">
          Всего: {users.length}
        </div>
      </div>

      {/* Инструкции: как добавляются пользователи */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
          <div className="text-2xl">ℹ️</div>
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-2">
              Как добавить нового пользователя?
            </h3>
            <div className="text-sm text-blue-800 space-y-2">
              <p>
                <strong>Пользователи добавляются АВТОМАТИЧЕСКИ</strong> при первом входе в систему:
              </p>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Новый сотрудник открывает Mini App в Telegram</li>
                <li>Система автоматически создаёт его аккаунт</li>
                <li>По умолчанию присваивается роль "Владелец"</li>
                <li>Вы видите его здесь и можете изменить роль</li>
              </ol>
              <p className="mt-3 pt-3 border-t border-blue-200">
                <strong>Для входа через браузер:</strong> нужно узнать свой Telegram ID через бота 
                <a href="https://t.me/userinfobot" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline ml-1">
                  @userinfobot
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {users.map((user) => (
          <div
            key={user.id}
            className={`bg-white rounded-xl p-4 shadow-sm border-2 ${
              !user.is_active ? 'opacity-50 border-gray-200' : 'border-transparent'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {/* Имя и username */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="text-lg font-semibold">
                    {user.full_name || user.username || `User ${user.id}`}
                  </div>
                  {user.id === currentUserId && (
                    <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-600 rounded-full">
                      Вы
                    </span>
                  )}
                  {!user.is_active && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-600 rounded-full">
                      Неактивен
                    </span>
                  )}
                </div>

                {/* Username и Telegram ID */}
                <div className="text-sm text-gray-500 mb-3">
                  {user.username && <div>@{user.username}</div>}
                  <div>Telegram ID: {user.telegram_id}</div>
                  <div className="text-xs">
                    Зарегистрирован: {new Date(user.created_at).toLocaleDateString('ru-RU')}
                  </div>
                </div>

                {/* Роль */}
                <div className="mb-3">
                  <select
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    disabled={user.id === currentUserId}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                      roleColors[user.role]
                    } ${
                      user.id === currentUserId ? 'cursor-not-allowed' : 'cursor-pointer'
                    }`}
                  >
                    <option value="owner">👑 {roleNames.owner}</option>
                    <option value="manager">👔 {roleNames.manager}</option>
                    <option value="accountant">📊 {roleNames.accountant}</option>
                    <option value="cashier">💰 {roleNames.cashier}</option>
                  </select>
                </div>

                {/* Кнопка активации/деактивации */}
                {user.id !== currentUserId && (
                  <button
                    onClick={() => handleToggleStatus(user.id, user.is_active)}
                    className={`text-sm px-4 py-2 rounded-lg font-medium ${
                      user.is_active
                        ? 'bg-red-50 text-red-600 hover:bg-red-100'
                        : 'bg-green-50 text-green-600 hover:bg-green-100'
                    }`}
                  >
                    {user.is_active ? '❌ Деактивировать' : '✅ Активировать'}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {users.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          Пользователи не найдены
        </div>
      )}
    </div>
  );
};

export default Users;
