import { Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';

import { useTelegram } from './hooks/useTelegram';
import api from './services/api';

import Header from './components/Layout/Header';
import BottomNav from './components/Layout/BottomNav';
import FloatingButton from './components/Layout/FloatingButton';
import AddModal from './components/Modals/AddModal';

import Home from './pages/Home';
import Timeline from './pages/Timeline';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';
import Users from './pages/Users';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

export default function App() {
  const { user, isReady } = useTelegram();
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const authenticateUser = async () => {
      console.log('1. Начало authenticateUser, isReady:', isReady);
      
      if (!isReady) {
        console.log('2. isReady = false, выходим');
        return;
      }

      try {
        // Получаем telegram_id из Telegram WebApp или используем тестовый
        const telegramId = user?.id?.toString() || '123456789';
        
        console.log('3. telegram_id:', telegramId);
        console.log('4. user объект:', user);
        
        // Сохраняем telegram_id для всех запросов
        localStorage.setItem('telegram_id', telegramId);
        console.log('5. Сохранили в localStorage');

        // Отправляем запрос на регистрацию/вход (передаём дополнительные поля из Telegram)
        console.log('6. Отправляем запрос на /auth/verify');
        const response = await api.verifyUser(telegramId, {
          username: user?.username || '',
          first_name: user?.first_name || '',
          last_name: user?.last_name || ''
        });
        const userData = response.data;
        console.log('7. Получили ответ от сервера:', userData);

        // НОВОЕ: Сохраняем user_id для проверки владения операциями
        if (userData?.id) {
          localStorage.setItem('current_user_id', userData.id.toString());
        }

        setCurrentUser(userData);
        setAuthenticated(true);
        console.log('8. Авторизация успешна');
      } catch (error) {
        console.error('❌ ОШИБКА авторизации:', error);
        console.error('❌ Детали:', error.response?.data || error.message);
        
        // Показываем более детальную ошибку
        const errorMsg = error.response?.data?.detail || error.message || 'Неизвестная ошибка';
        alert(`Ошибка авторизации: ${errorMsg}`);
      } finally {
        setLoading(false);
        console.log('9. Закончили authenticateUser');
      }
    };

    authenticateUser();
  }, [user, isReady]);

  if (loading || !authenticated) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-spin">⏳</div>
          <div className="text-gray-600">
            {loading ? 'Загрузка...' : 'Ошибка авторизации'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header user={currentUser} />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/timeline" element={<Timeline />} />
        <Route path="/analytics" element={<Analytics />} />
  <Route path="/profile" element={<Profile />} />
  <Route path="/users" element={<Users />} />
  <Route path="/reports" element={<Reports />} />
  <Route path="/settings" element={<Settings />} />
      </Routes>

      {!showAdd && (
        <FloatingButton onClick={() => setShowAdd(true)} />
      )}

      {showAdd && (
        <AddModal onClose={() => setShowAdd(false)} />
      )}

      <BottomNav />
    </div>
  );
}