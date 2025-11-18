# 🤖 CURSOR: Создание Telegram Mini App для Air Waffle Finance

## 🎯 ЗАДАЧА
Создать Telegram Mini App с функционалом добавления операций (расходы, приходы, инкасация, переводы)

---

## 📦 УЖЕ ГОТОВО (в outputs/)

1. `package.json` - зависимости
2. `tailwind.config.js` - конфиг Tailwind
3. `vite.config.js` - конфиг Vite
4. `index.html` - HTML
5. `index.css` - стили
6. `useTelegram.js` - хук Telegram WebApp
7. `api.js` - API клиент
8. `FloatingButton.jsx` - центральная кнопка "+"
9. `AddModal.jsx` - меню выбора операции
10. `IncasationForm.jsx` - форма инкасации (образец)

---

## 🏗️ СТРУКТУРА ПРОЕКТА

Создай структуру:
```
miniapp/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   ├── Modals/
│   │   │   ├── Timeline/
│   │   │   └── Common/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── backend/
    └── (пока не нужен, будет позже)
```

---

## ✅ ШАГ 1: Инициализация проекта

```bash
# Создать папку
mkdir air-waffle-miniapp && cd air-waffle-miniapp
mkdir frontend && cd frontend

# Скопировать готовые файлы из outputs/
# - package.json
# - tailwind.config.js
# - vite.config.js
# - index.html

# Установить зависимости
npm install

# Создать структуру src/
mkdir -p src/{components/{Layout,Modals,Timeline,Common},pages,hooks,services,utils}

# Скопировать готовые компоненты из outputs/
# - src/index.css
# - src/hooks/useTelegram.js
# - src/services/api.js
# - src/components/Layout/FloatingButton.jsx
# - src/components/Modals/AddModal.jsx
# - src/components/Modals/IncasationForm.jsx
```

---

## ✅ ШАГ 2: Создать недостающие формы

### **ExpenseForm.jsx** (скопировать из IncasationForm.jsx)

```jsx
// src/components/Modals/ExpenseForm.jsx
// Аналогично IncasationForm, но:
// - Одно поле: категория (expense)
// - Одно поле: счёт
// - Поле: сумма
// - Поле: описание
// - API: api.createExpense({ amount, category_id, account_id, description, date })
```

### **IncomeForm.jsx** (скопировать из ExpenseForm)

```jsx
// src/components/Modals/IncomeForm.jsx
// Аналогично ExpenseForm, но:
// - Категории: income (не expense)
// - API: api.createIncome(...)
```

### **TransferForm.jsx** (скопировать из IncasationForm)

```jsx
// src/components/Modals/TransferForm.jsx
// Аналогично IncasationForm, но:
// - Откуда: любой счёт (не только касса)
// - Куда: любой счёт (не только банк)
// - Дополнительно: поле commission (комиссия)
// - API: api.createTransfer({ from_account_id, to_account_id, amount, commission, description, date })
```

---

## ✅ ШАГ 3: Создать Layout компоненты

### **Header.jsx**

```jsx
// src/components/Layout/Header.jsx
export default function Header({ user }) {
  return (
    <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-2xl">💰</span>
        <h1 className="text-lg font-bold">Air Waffle</h1>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">{user?.first_name}</span>
      </div>
    </div>
  );
}
```

### **BottomNav.jsx**

```jsx
// src/components/Layout/BottomNav.jsx
import { useNavigate, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { id: 'home', icon: '🏠', label: 'Главная', path: '/' },
  { id: 'timeline', icon: '📊', label: 'Timeline', path: '/timeline' },
  { id: 'add', icon: '', label: '', path: '' }, // Пустое место для FAB
  { id: 'analytics', icon: '📈', label: 'Аналитика', path: '/analytics' },
  { id: 'profile', icon: '👤', label: 'Профиль', path: '/profile' }
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t h-16 flex items-center justify-around px-2 z-40">
      {NAV_ITEMS.map(item => (
        item.id === 'add' ? (
          <div key="add" className="w-16" />
        ) : (
          <button
            key={item.id}
            onClick={() => navigate(item.path)}
            className={`
              flex flex-col items-center justify-center flex-1 h-full
              ${location.pathname === item.path ? 'text-blue-500' : 'text-gray-500'}
            `}
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="text-xs mt-1">{item.label}</span>
          </button>
        )
      ))}
    </nav>
  );
}
```

---

## ✅ ШАГ 4: Создать Pages

### **Home.jsx**

```jsx
// src/pages/Home.jsx
import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Home() {
  const [stats, setStats] = useState({
    today_expenses: 0,
    today_income: 0,
    balance: 0
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    // Можно добавить API endpoint для статистики
    // Пока заглушка
    setStats({
      today_expenses: 150000,
      today_income: 500000,
      balance: 2500000
    });
  };

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-2xl font-bold">Сегодня</h2>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-sm text-gray-500">Расходы</div>
          <div className="text-2xl font-bold text-red-500">
            -{stats.today_expenses.toLocaleString()}
          </div>
        </div>
        
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-sm text-gray-500">Приходы</div>
          <div className="text-2xl font-bold text-green-500">
            +{stats.today_income.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="bg-blue-500 text-white rounded-xl p-4">
        <div className="text-sm opacity-80">Общий баланс</div>
        <div className="text-3xl font-bold">
          {stats.balance.toLocaleString()} сум
        </div>
      </div>
    </div>
  );
}
```

### **Timeline.jsx**

```jsx
// src/pages/Timeline.jsx
import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Timeline() {
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOperations();
  }, []);

  const loadOperations = async () => {
    try {
      const data = await api.getTimeline({ limit: 50 });
      setOperations(data);
    } catch (error) {
      console.error('Ошибка загрузки:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4 text-center">Загрузка...</div>;
  }

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-2xl font-bold">История операций</h2>
      
      {operations.map(op => (
        <div key={op.id} className="bg-white rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center
                ${op.type === 'expense' ? 'bg-red-100' : 'bg-green-100'}
              `}>
                {op.type === 'expense' ? '📉' : '📈'}
              </div>
              <div>
                <div className="font-medium">{op.description || 'Операция'}</div>
                <div className="text-sm text-gray-500">{op.date}</div>
              </div>
            </div>
            <div className={`
              text-lg font-semibold
              ${op.type === 'expense' ? 'text-red-500' : 'text-green-500'}
            `}>
              {op.type === 'expense' ? '-' : '+'}
              {op.amount.toLocaleString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### **Analytics.jsx** и **Profile.jsx**

```jsx
// Простые заглушки
export default function Analytics() {
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold">Аналитика</h2>
      <p className="text-gray-500 mt-4">В разработке...</p>
    </div>
  );
}
```

---

## ✅ ШАГ 5: Создать App.jsx и main.jsx

### **App.jsx**

```jsx
// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useTelegram } from './hooks/useTelegram';
import api from './services/api';

import Header from './components/Layout/Header';
import BottomNav from './components/Layout/BottomNav';
import FloatingButton from './components/Layout/FloatingButton';

import Home from './pages/Home';
import Timeline from './pages/Timeline';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';

export default function App() {
  const { user, isReady } = useTelegram();
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    if (user && isReady) {
      verifyUser();
    }
  }, [user, isReady]);

  const verifyUser = async () => {
    try {
      const data = await api.verifyUser(user.id);
      localStorage.setItem('telegram_id', user.id);
      setAuthenticated(true);
    } catch (error) {
      console.error('Auth error:', error);
    }
  };

  if (!isReady || !authenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <div>Загрузка...</div>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>

        <FloatingButton />
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}
```

### **main.jsx**

```jsx
// src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

## ✅ ШАГ 6: Запуск

```bash
# Запустить dev сервер
npm run dev

# Открыть в браузере
# http://localhost:5173
```

---

## 🎨 ВАЖНЫЕ ДЕТАЛИ

### **Цвета операций:**
- Расход: `text-red-500`, `bg-red-100`
- Приход: `text-green-500`, `bg-green-100`
- Инкасация: `text-blue-500`, `bg-blue-100`
- Перевод: `text-purple-500`, `bg-purple-100`

### **Иконки операций:**
- Расход: 📉 или 💸
- Приход: 📈 или 💰
- Инкасация: 🏦
- Перевод: 🔄

### **Форматирование чисел:**
```javascript
amount.toLocaleString() // 1500000 → "1,500,000"
```

---

## 🐛 ТЕСТИРОВАНИЕ

1. Открой приложение в браузере
2. Проверь что кнопка "+" работает
3. Проверь что меню открывается
4. Проверь что формы работают (пока без API)
5. Проверь навигацию между страницами

---

## 📝 ЧЕКЛИСТ

- [ ] Создана структура проекта
- [ ] Установлены зависимости
- [ ] Скопированы готовые файлы
- [ ] Созданы формы: ExpenseForm, IncomeForm, TransferForm
- [ ] Созданы Layout: Header, BottomNav
- [ ] Созданы Pages: Home, Timeline, Analytics, Profile
- [ ] Создан App.jsx и main.jsx
- [ ] Приложение запускается
- [ ] FAB кнопка работает
- [ ] Навигация работает

---

✅ ГОТОВО! Запускай `npm run dev` и проверяй!
