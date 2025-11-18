# 🤖 CURSOR: Исправить бесконечную загрузку

## ПРОБЛЕМА
App.jsx ждёт backend API для аутентификации, но backend ещё нет.

## РЕШЕНИЕ
Временно отключить проверку auth для тестирования UI.

---

## В файле `src/App.jsx`

### ШАГ 1: Изменить начальное состояние

**Было:**
```jsx
const [authenticated, setAuthenticated] = useState(false);
```

**Стало:**
```jsx
const [authenticated, setAuthenticated] = useState(true); // Для теста без backend
```

### ШАГ 2: Закомментировать verifyUser

**Было:**
```jsx
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
```

**Стало:**
```jsx
// ВРЕМЕННО ОТКЛЮЧЕНО - включить когда backend готов
useEffect(() => {
  if (user && isReady) {
    localStorage.setItem('telegram_id', user.id);
  }
}, [user, isReady]);

/*
const verifyUser = async () => {
  try {
    const data = await api.verifyUser(user.id);
    localStorage.setItem('telegram_id', user.id);
    setAuthenticated(true);
  } catch (error) {
    console.error('Auth error:', error);
  }
};
*/
```

---

## В файле `src/pages/Timeline.jsx`

### ШАГ 3: Добавить тестовые данные

**Заменить `loadOperations`:**

```jsx
const loadOperations = async () => {
  try {
    // ВРЕМЕННО: тестовые данные вместо API
    const mockData = [
      {
        id: 1,
        date: '2025-11-08',
        type: 'expense',
        amount: 15000,
        description: 'Кофе',
        account_name: 'Касса'
      },
      {
        id: 2,
        date: '2025-11-08',
        type: 'income',
        amount: 150000,
        description: 'Продажа',
        account_name: 'Kaspi'
      },
      {
        id: 3,
        date: '2025-11-07',
        type: 'incasation',
        amount: 500000,
        description: 'Инкасация',
        from_account_name: 'Касса',
        to_account_name: 'Kapitalbank'
      }
    ];
    
    setOperations(mockData);
    
    // Когда backend готов, раскомментировать:
    // const data = await api.getTimeline({ limit: 50 });
    // setOperations(data);
  } catch (error) {
    console.error('Ошибка загрузки:', error);
  } finally {
    setLoading(false);
  }
};
```

---

## В файле `src/components/Modals/IncasationForm.jsx`

### ШАГ 4: Добавить тестовые счета

**В `loadAccounts`:**

```jsx
const loadAccounts = async () => {
  try {
    // ВРЕМЕННО: тестовые данные
    const mockAccounts = [
      { id: 1, name: 'Касса Филиал 1', account_type: 'cash', balance: 1500000 },
      { id: 2, name: 'Касса Филиал 2', account_type: 'cash', balance: 800000 },
      { id: 5, name: 'Kapitalbank', account_type: 'bank' },
      { id: 6, name: 'Uzcard', account_type: 'bank' }
    ];
    
    setCashAccounts(mockAccounts.filter(a => a.account_type === 'cash'));
    setBankAccounts(mockAccounts.filter(a => a.account_type === 'bank'));
    
    // Когда backend готов:
    // const accounts = await api.getAccounts();
    // setCashAccounts(accounts.filter(a => a.account_type === 'cash'));
    // setBankAccounts(accounts.filter(a => a.account_type === 'bank'));
  } catch (error) {
    console.error('Ошибка загрузки счетов:', error);
  }
};
```

### ШАГ 5: Заглушка для submit

**В `handleSubmit`:**

```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  
  if (!form.from_account_id || !form.to_account_id || !form.amount) {
    alert('Заполните все поля');
    return;
  }

  setLoading(true);
  hapticFeedback('medium');

  try {
    // ВРЕМЕННО: показать данные вместо отправки
    console.log('Инкасация:', form);
    alert(`✅ Инкасация создана!\nСумма: ${parseFloat(form.amount).toLocaleString()} сум`);
    
    // Когда backend готов:
    // await api.createIncasation({ ...form, amount: parseFloat(form.amount) });
    
    hapticFeedback('success');
    onSuccess();
  } catch (error) {
    console.error('Ошибка:', error);
    hapticFeedback('error');
    alert('❌ Ошибка: ' + error.message);
  } finally {
    setLoading(false);
  }
};
```

---

## АНАЛОГИЧНО для других форм:
- ExpenseForm.jsx
- IncomeForm.jsx  
- TransferForm.jsx

Добавить тестовые данные в `loadCategories()` и заглушки в `handleSubmit()`.

---

## РЕЗУЛЬТАТ

После этих изменений:
- ✅ Приложение сразу откроется
- ✅ Можно тестировать UI
- ✅ Формы работают (показывают alert вместо отправки)
- ✅ Timeline показывает тестовые данные

Когда backend будет готов - просто раскомментировать API вызовы!

---

✅ Сохрани изменения и перезапусти dev сервер!
