import { useState } from 'react';
import ExpenseForm from './ExpenseForm';
import IncomeForm from './IncomeForm';
import IncasationForm from './IncasationForm';
import TransferForm from './TransferForm';

const MENU_ITEMS = [
  {
    id: 'expense',
    icon: '📉',
    title: 'Расход',
    subtitle: 'Добавить расход',
    color: 'red',
    component: ExpenseForm
  },
  {
    id: 'income',
    icon: '📈',
    title: 'Приход',
    subtitle: 'Добавить приход',
    color: 'green',
    component: IncomeForm
  },
  {
    id: 'incasation',
    icon: '🏦',
    title: 'Инкасация',
    subtitle: 'Наличные → Банк',
    color: 'blue',
    component: IncasationForm
  },
  {
    id: 'transfer',
    icon: '🔄',
    title: 'Перевод',
    subtitle: 'Счёт → Счёт',
    color: 'purple',
    component: TransferForm
  }
];

export default function AddModal({ onClose }) {
  const [selectedType, setSelectedType] = useState(null);

  const handleSelect = (item) => {
    setSelectedType(item);
  };

  const handleBack = () => {
    setSelectedType(null);
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end"
      onClick={onClose}
    >
      <div 
        className="bg-white w-full rounded-t-3xl slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {selectedType ? (
          // Форма выбранной операции
          <div>
            <div className="p-4 border-b flex items-center gap-3">
              <button 
                onClick={handleBack}
                className="text-2xl"
              >
                ←
              </button>
              <span className="text-2xl">{selectedType.icon}</span>
              <h2 className="text-xl font-bold">{selectedType.title}</h2>
            </div>
            
            <selectedType.component 
              onClose={onClose}
              onSuccess={() => {
                onClose();
                // Можно добавить обновление timeline
              }}
            />
          </div>
        ) : (
          // Меню выбора
          <div>
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">Что добавить?</h2>
            </div>

            <div className="p-4 space-y-2">
              {MENU_ITEMS.map(item => (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  className="
                    w-full p-4 rounded-xl
                    flex items-center gap-4
                    bg-gray-50 hover:bg-gray-100
                    active:scale-98 transition-all
                  "
                >
                  <span className="text-4xl">{item.icon}</span>
                  <div className="flex-1 text-left">
                    <div className="font-semibold text-lg">{item.title}</div>
                    <div className="text-sm text-gray-500">{item.subtitle}</div>
                  </div>
                  <span className="text-gray-400">→</span>
                </button>
              ))}
            </div>

            <div className="p-4">
              <button
                onClick={onClose}
                className="w-full p-4 text-gray-600 font-medium"
              >
                Отмена
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
