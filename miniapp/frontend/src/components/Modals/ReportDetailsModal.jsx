import React from 'react';

const ReportDetailsModal = ({ report, onClose }) => {
  const formatNumber = (num) => {
    return new Intl.NumberFormat('ru-RU').format(num);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Заголовок */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-1">
              📋 Отчёт от {formatDate(report.report_date)}
            </h2>
            <div className="text-sm text-gray-600">
              📍 {report.location_name}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-3xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Общая информация */}
          <div className="bg-purple-50 rounded-xl p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Общая выручка</div>
                <div className="text-2xl font-bold text-purple-600">
                  {formatNumber(report.total_sales)} сум
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Кассир</div>
                <div className="text-lg font-semibold text-gray-800">
                  👤 {report.cashier_name || report.cashier_username}
                </div>
              </div>
            </div>
          </div>

          {/* Касса */}
          {report.cash_actual > 0 && (
            <div className="bg-green-50 rounded-xl p-4">
              <h3 className="text-lg font-semibold mb-3 text-green-800">💰 Касса</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Ожидается</div>
                  <div className="text-lg font-semibold">
                    {formatNumber(report.cash_expected || 0)} сум
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Фактически</div>
                  <div className="text-lg font-semibold">
                    {formatNumber(report.cash_actual || 0)} сум
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Разница</div>
                  <div className={`text-lg font-semibold ${
                    (report.cash_difference || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatNumber(report.cash_difference || 0)} сум
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Платежи */}
          {report.payments && report.payments.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">💳 Методы оплаты</h3>
              <div className="space-y-2">
                {report.payments.map((payment, index) => (
                  <div
                    key={index}
                    className="bg-gray-50 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div>
                      <div className="font-medium">{payment.payment_method_name}</div>
                      {payment.commission_amount > 0 && (
                        <div className="text-sm text-gray-500">
                          Комиссия: {formatNumber(payment.commission_amount)} сум
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-green-600">
                        {formatNumber(payment.amount)} сум
                      </div>
                      {payment.commission_amount > 0 && (
                        <div className="text-sm text-gray-500">
                          Чистыми: {formatNumber(payment.net_amount)} сум
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Расходы */}
          {report.expenses && report.expenses.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">📤 Расходы</h3>
              <div className="space-y-2">
                {report.expenses.map((expense, index) => (
                  <div
                    key={index}
                    className="bg-red-50 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div>
                      <div className="font-medium">{expense.category_name || 'Без категории'}</div>
                      {expense.description && (
                        <div className="text-sm text-gray-600">{expense.description}</div>
                      )}
                    </div>
                    <div className="text-lg font-semibold text-red-600">
                      {formatNumber(expense.amount)} сум
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Прочие приходы */}
          {report.incomes && report.incomes.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">📥 Прочие приходы</h3>
              <div className="space-y-2">
                {report.incomes.map((income, index) => (
                  <div
                    key={index}
                    className="bg-blue-50 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div>
                      <div className="font-medium">{income.category_name || 'Без категории'}</div>
                      {income.description && (
                        <div className="text-sm text-gray-600">{income.description}</div>
                      )}
                    </div>
                    <div className="text-lg font-semibold text-blue-600">
                      {formatNumber(income.amount)} сум
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Заметки */}
          {report.notes && (
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-700 mb-2">📝 Заметки:</div>
              <div className="text-gray-600">{report.notes}</div>
            </div>
          )}

          {/* Служебная информация */}
          <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="font-medium">Создан:</span>{' '}
                {new Date(report.created_at).toLocaleString('ru-RU')}
              </div>
              {report.closed_at && (
                <div>
                  <span className="font-medium">Закрыт:</span>{' '}
                  {new Date(report.closed_at).toLocaleString('ru-RU')}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Кнопка закрытия */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4">
          <button
            onClick={onClose}
            className="w-full py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-xl font-semibold transition"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportDetailsModal;
