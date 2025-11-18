import { useEffect, useState } from 'react';

export function useTelegram() {
  const [tg, setTg] = useState(null);
  const [user, setUser] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const telegram = window.Telegram?.WebApp;
    
    if (telegram) {
      telegram.ready();
      telegram.expand();
      
      setTg(telegram);
      setUser(telegram.initDataUnsafe?.user || null);
      setIsReady(true);

      // Скрыть кнопку "назад" если есть
      telegram.BackButton.hide();
    } else {
      console.warn('Telegram WebApp не найден');
      
      // Для разработки: фейковый пользователь
      setUser({
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser'
      });
      setIsReady(true);
    }
  }, []);

  const close = () => {
    tg?.close();
  };

  const showAlert = (message) => {
    tg?.showAlert(message);
  };

  const showConfirm = (message, callback) => {
    tg?.showConfirm(message, callback);
  };

  const hapticFeedback = (type = 'medium') => {
    // type: 'light', 'medium', 'heavy', 'rigid', 'soft'
    tg?.HapticFeedback?.impactOccurred(type);
  };

  return {
    tg,
    user,
    isReady,
    close,
    showAlert,
    showConfirm,
    hapticFeedback
  };
}
