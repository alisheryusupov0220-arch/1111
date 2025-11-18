import { useEffect, useState } from 'react';

export function useTelegram() {
  const [tg, setTg] = useState(null);
  const [user, setUser] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const telegram = window.Telegram?.WebApp;
    
    if (telegram) {
      // --- БЕЗОПАСНЫЕ ВЫЗОВЫ ---
      try {
        if (telegram.ready) {
          telegram.ready();
        }
        if (telegram.expand) {
          telegram.expand();
        }
        
        setTg(telegram);
        setUser(telegram.initDataUnsafe?.user || null);
        setIsReady(true);

        // Скрыть кнопку "назад" если есть
        if (telegram.BackButton?.hide) {
          telegram.BackButton.hide();
        }
      } catch (error) {
        console.warn('Ошибка инициализации Telegram WebApp:', error);
      }
      // --- КОНЕЦ БЕЗОПАСНЫХ ВЫЗОВОВ ---
    } else {
      console.warn('Telegram WebApp не найден. Запуск в режиме разработки.');
      
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
    try {
      if (tg?.close) {
        tg.close();
      }
    } catch (error) {
      console.warn('Close method not available:', error);
    }
  };

  const showAlert = (message) => {
    try {
      if (tg?.showAlert) {
        tg.showAlert(message);
      } else {
        // Fallback для браузера
        alert(message);
      }
    } catch (error) {
      // Fallback для браузера если произошла ошибка
      alert(message);
    }
  };

  const showConfirm = (message, callback) => {
    try {
      if (tg?.showConfirm) {
        tg.showConfirm(message, callback);
      } else {
        // Fallback для браузера
        const result = window.confirm(message);
        callback(result);
      }
    } catch (error) {
      // Fallback для браузера
      const result = window.confirm(message);
      callback(result);
    }
  };

  const hapticFeedback = (type = 'medium') => {
    // Просто молчим если метод недоступен - НЕ бросаем ошибку
    try {
      if (tg?.HapticFeedback?.impactOccurred) {
        tg.HapticFeedback.impactOccurred(type);
      }
    } catch (error) {
      // Полностью игнорируем ошибку
      // console.debug('HapticFeedback not available');
    }
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