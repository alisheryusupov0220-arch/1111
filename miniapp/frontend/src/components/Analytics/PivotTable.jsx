import React from 'react';
// Убраны импорты useEffect, useState, api, так как они больше не нужны

// Принимаем { pivotData, loading } из Analytics.jsx
// 'pivotData' — это 'data' из инструкции
export default function PivotTable({ pivotData, loading }) {
  
  // Показываем заглушку "Загрузка..."
  if (loading) {
    return (
       <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-2">⏳</div>
        <div>Загрузка...</div>
      </div>
    );
  }

  // Показываем "Нет данных", если данные не пришли
  if (!pivotData || Object.keys(pivotData).length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-2">🔍</div>
        <div>Нет данных для отображения</div>
      </div>
    );
  }

  // Рендерим новую, "плоскую" таблицу из инструкции
  return (
    <div className="overflow-x-auto bg-white rounded-2xl shadow-sm p-4">
      <table className="w-full border-collapse text-sm min-w-[600px]">
        <thead className="bg-blue-500 text-white">
          <tr>
            <th className="border border-blue-400 p-2 text-left">Месяц</th>
            <th className="border border-blue-400 p-2 text-left">Тип аналитики</th>
            <th className="border border-blue-400 p-2 text-left">Категория</th>
            <th className="border border-blue-400 p-2 text-right">Сумма</th>
          </tr>
        </thead>
        <tbody>
          {/* Используем Object.entries для новой структуры данных, как в инструкции.
            pivotData = { "2023-10": { "food_cost": { "Продукты": 1000 } } }
          */}
          {Object.entries(pivotData).map(([month, types], monthIdx) => 
            Object.entries(types).map(([type, categories], typeIdx) => 
              Object.entries(categories).map(([cat, total], catIdx) => (
                <tr 
                  key={`${month}-${type}-${cat}`}
                  // Сохраняем стиль "зебры"
                  className={(monthIdx + typeIdx + catIdx) % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
                >
                  <td className="border p-2">{month}</td>
                  <td className="border p-2">{type}</td>
                  <td className="border p-2 font-medium">{cat}</td>
                  <td className="border p-2 text-right">{total.toLocaleString()}</td>
                </tr>
              ))
            )
          )}
        </tbody>
      </table>
    </div>
  );
}
