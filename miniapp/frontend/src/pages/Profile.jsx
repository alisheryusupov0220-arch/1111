import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const Profile = () => {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [showUsers, setShowUsers] = useState(false);
  const [loading, setLoading] = useState(true);

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
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const telegramId = localStorage.getItem('telegram_id');
      
      // Загружаем текущего пользователя
      const response = await apiService.verifyUser(parseInt(telegramId));
      setCurrentUser(response.data);
      
      // Если owner или manager - загружаем всех пользователей
      if (response.data.role === 'owner' || response.data.role === 'manager') {
        try {
          const usersResponse = await apiService.getAllUsers();
          setUsers(usersResponse.data);
        } catch (error) {
          console.error('Error loading users:', error);
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
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
      loadProfile();
    } catch (error) {
      console.error('Error updating role:', error);
      alert(error.response?.data?.detail || 'Ошибка при обновлении роли');
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
      loadProfile();
    } catch (error) {
      console.error('Error toggling status:', error);
      alert(error.response?.data?.detail || 'Ошибка при изменении статуса');
    }
  };

  const handleLogout = () => {
    if (window.confirm('Выйти из аккаунта?')) {
      localStorage.removeItem('telegram_id');
      localStorage.removeItem('current_user_id');
      window.location.reload();
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
      <h1 className="text-2xl font-bold mb-6">👤 Профиль</h1>

      {/* Информация о текущем пользователе */}
      {currentUser && (
        <div className="bg-white rounded-xl p-6 mb-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-2xl font-bold mb-1">
                {currentUser.full_name || currentUser.username || 'Пользователь'}
              </div>
              {currentUser.username && (
                <div className="text-gray-500">@{currentUser.username}</div>
              )}
              <div className="text-sm text-gray-400 mt-1">
                Telegram ID: {currentUser.telegram_id}
              </div>
            </div>
            <div className={`px-4 py-2 rounded-lg font-medium ${roleColors[currentUser.role]}`}>
              {roleNames[currentUser.role]}
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full py-3 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition font-medium"
          >
            🚪 Выйти из аккаунта
          </button>
        </div>
      )}

      {/* Управление пользователями (только для owner/manager) */}
      {currentUser && (currentUser.role === 'owner' || currentUser.role === 'manager') && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <button
            onClick={() => setShowUsers(!showUsers)}
            className="w-full flex items-center justify-between py-3 text-lg font-semibold"
          >
            <span>👥 Управление пользователями ({users.length})</span>
            <span className="text-2xl">{showUsers ? '▼' : '▶'}</span>
          </button>

          {showUsers && (
            <div className="mt-6 space-y-3">
              {/* Инструкция */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
                <div className="flex items-start gap-3">
                  <div className="text-2xl">ℹ️</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-blue-900 mb-2">
                      Как добавить пользователя?
                    </h3>
                    <div className="text-sm text-blue-800">
                      Пользователи добавляются автоматически при первом входе в систему
                    </div>
                  </div>
                </div>
              </div>

              {/* Список пользователей */}
              {users.map((user) => (
                <div
                  key={user.id}
                  className={`p-4 rounded-xl border-2 ${
                    !user.is_active ? 'opacity-50 border-gray-200 bg-gray-50' : 'border-gray-100 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="font-semibold">
                          {user.full_name || user.username || `User ${user.id}`}
                        </div>
                        {user.id === currentUser.id && (
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
                      {user.username && (
                        <div className="text-sm text-gray-500">@{user.username}</div>
                      )}
                      <div className="text-xs text-gray-400">
                        ID: {user.telegram_id}
                      </div>
                    </div>
                  </div>

                  {/* Роль */}
                  <select
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    disabled={user.id === currentUser.id}
                    className={`w-full mb-3 px-3 py-2 rounded-lg text-sm font-medium ${
                      roleColors[user.role]
                    } ${
                      user.id === currentUser.id ? 'cursor-not-allowed' : 'cursor-pointer'
                    }`}
                  >
                    <option value="owner">👑 {roleNames.owner}</option>
                    <option value="manager">👔 {roleNames.manager}</option>
                    <option value="accountant">📊 {roleNames.accountant}</option>
                    <option value="cashier">💰 {roleNames.cashier}</option>
                  </select>

                  {/* Кнопка активации */}
                  {user.id !== currentUser.id && currentUser.role === 'owner' && (
                    <button
                      onClick={() => handleToggleStatus(user.id, user.is_active)}
                      className={`w-full text-sm px-4 py-2 rounded-lg font-medium ${
                        user.is_active
                          ? 'bg-red-50 text-red-600 hover:bg-red-100'
                          : 'bg-green-50 text-green-600 hover:bg-green-100'
                      }`}
                    >
                      {user.is_active ? '❌ Деактивировать' : '✅ Активировать'}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Profile;


