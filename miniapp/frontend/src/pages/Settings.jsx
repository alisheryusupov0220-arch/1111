import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('categories');
  const [categories, setCategories] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', parent_id: null, type: '' });
  const [searchQuery, setSearchQuery] = useState('');

  // --- STATE ДЛЯ АНАЛИТИКИ ---
  const [analyticsTab, setAnalyticsTab] = useState('categories'); // 'categories' или 'blocks'
  const [analyticsSettings, setAnalyticsSettings] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [analyticBlocks, setAnalyticBlocks] = useState([]);
  const [blockFormData, setBlockFormData] = useState({
    code: '',
    name: '',
    icon: '📊',
    color: 'blue',
    threshold_good: 25,
    threshold_warning: 35,
    sort_order: 0
  });
  // ------------------------------------

  useEffect(() => {
    loadData();
  }, [activeTab, analyticsTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'categories') {
        // === ИЗМЕНЕНО: используем unified endpoint ===
        const data = await api.getAllUnifiedCategories();
        setCategories((data || []).filter(c => c.is_active));
      } else if (activeTab === 'accounts') {
        const data = await api.getAccounts();
        setAccounts(data || []);
      } else if (activeTab === 'analytics') {
        if (analyticsTab === 'categories') {
          const catData = await api.getAllUnifiedCategories(); // ИЗМЕНЕНО
          const anData = await api.getAnalyticsSettings();
          const blocks = await api.getAnalyticBlocks();
          setAllCategories(catData || []);
          setAnalyticsSettings(anData || []);
          setAnalyticBlocks(blocks || []);
        } else if (analyticsTab === 'blocks') {
          const blocks = await api.getAnalyticBlocks();
          setAnalyticBlocks(blocks || []);
        }
      }
    } catch (error) {
      console.error('Error loading:', error);
      alert('Ошибка загрузки данных');
    }
    setLoading(false);
  };

  // --- ФУНКЦИИ ДЛЯ КАТЕГОРИЙ В АНАЛИТИКЕ ---
  const getTypeForCategory = (catId) => {
    const setting = analyticsSettings.find(s => s.category_id === catId);
    return setting ? setting.analytic_type : 'none';
  };

  const handleTypeChange = async (catId, newType) => {
    const setting = analyticsSettings.find(s => s.category_id === catId);
    
    try {
      if (newType === 'none') {
        if (setting) {
          await api.deleteAnalyticsSetting(setting.id);
        }
      } else if (setting) {
        await api.updateAnalyticsSetting(setting.id, { category_id: catId, analytic_type: newType });
      } else {
        await api.createAnalyticsSetting({ category_id: catId, analytic_type: newType });
      }
      
      const anData = await api.getAnalyticsSettings();
      setAnalyticsSettings(anData || []);
      
    } catch (error) {
      console.error('Error updating analytics:', error);
      alert('Ошибка сохранения настроек аналитики');
    }
  };

  // --- ФУНКЦИИ ДЛЯ БЛОКОВ АНАЛИТИКИ ---
  const handleBlockSave = async () => {
    if (!blockFormData.code.trim() || !blockFormData.name.trim()) {
      alert('Заполните код и название блока');
      return;
    }

    try {
      if (editItem) {
        await api.updateAnalyticBlock(editItem.id, blockFormData);
      } else {
        await api.createAnalyticBlock(blockFormData);
      }
      setShowForm(false);
      setEditItem(null);
      setBlockFormData({
        code: '',
        name: '',
        icon: '📊',
        color: 'blue',
        threshold_good: 25,
        threshold_warning: 35,
        sort_order: 0
      });
      loadData();
    } catch (error) {
      console.error('Error saving block:', error);
      alert('Ошибка сохранения блока');
    }
  };

  const handleBlockEdit = (block) => {
    setEditItem(block);
    setBlockFormData({
      code: block.code,
      name: block.name,
      icon: block.icon,
      color: block.color,
      threshold_good: block.threshold_good,
      threshold_warning: block.threshold_warning,
      sort_order: block.sort_order
    });
    setShowForm(true);
  };

  const handleBlockDelete = async (id) => {
    if (!confirm('Архивировать блок? Он будет скрыт.')) return;
    try {
      await api.deleteAnalyticBlock(id);
      loadData();
    } catch (error) {
      console.error('Error deleting block:', error);
      alert('Ошибка удаления блока');
    }
  };

  // --- ФУНКЦИИ ДЛЯ НАИМЕНОВАНИЙ/СЧЕТОВ ---
  const handleSave = async () => {
    if (!formData.name.trim()) {
      alert('Введите название');
      return;
    }

    try {
      if (activeTab === 'categories') {
        // === ИЗМЕНЕНО: используем unified endpoints ===
        if (editItem) {
          await api.updateUnifiedCategory(editItem.id, formData);
        } else {
          await api.createUnifiedCategory(formData);
        }
      } else {
        if (!formData.type.trim()) {
          alert('Введите тип счёта');
          return;
        }
        if (editItem) {
          await api.updateAccount(editItem.id, formData);
        } else {
          await api.createAccount(formData);
        }
      }
      setShowForm(false);
      setEditItem(null);
      setFormData({ name: '', parent_id: null, type: '' });
      loadData();
    } catch (error) {
      console.error('Error saving:', error);
      alert('Ошибка сохранения');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Архивировать? Элемент скроется из списков.')) return;
    try {
      if (activeTab === 'categories') {
        // === ИЗМЕНЕНО: используем unified endpoint ===
        await api.deleteUnifiedCategory(id);
      } else {
        await api.deleteAccount(id);
      }
      loadData();
    } catch (error) {
      console.error('Error deleting:', error);
      alert('Ошибка удаления');
    }
  };

  const handleEdit = (item) => {
    setEditItem(item);
    setFormData({ 
      name: item.name, 
      parent_id: item.parent_id || null, 
      type: item.type || '' 
    });
    setShowForm(true);
  };

  const filteredItems = (activeTab === 'categories' ? categories : accounts).filter(
    item => item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white pb-24">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10 border-b border-gray-200">
        <div className="p-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">⚙️ Настройки</h1>
            <p className="text-sm text-gray-500 mt-0.5">Управление системой</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('categories')}
            className={`flex-1 py-3 px-2 text-sm font-medium transition-colors ${
              activeTab === 'categories'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            📝 Наименования
          </button>
          <button
            onClick={() => setActiveTab('accounts')}
            className={`flex-1 py-3 px-2 text-sm font-medium transition-colors ${
              activeTab === 'accounts'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            💳 Счета
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 py-3 px-2 text-sm font-medium transition-colors ${
              activeTab === 'analytics'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            📊 Аналитика
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Категории и Счета */}
        {(activeTab === 'categories' || activeTab === 'accounts') && (
          <>
            {/* Search */}
            <div className="mb-4">
              <input
                type="text"
                placeholder={`🔍 Поиск ${activeTab === 'categories' ? 'наименований' : 'счетов'}...`}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
              />
            </div>

            {/* Add button */}
            <button
              onClick={() => setShowForm(true)}
              className="w-full mb-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white py-4 rounded-xl font-medium shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <span className="text-xl">➕</span>
              <span>Добавить {activeTab === 'categories' ? 'наименование' : 'счёт'}</span>
            </button>

            {/* Loading */}
            {loading && (
              <div className="text-center py-8 text-gray-500">
                Загрузка...
              </div>
            )}

            {/* List */}
            <div className="space-y-2">
              {!loading && filteredItems.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  <div className="text-5xl mb-3">📭</div>
                  <div>Пусто</div>
                </div>
              )}

              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{item.name}</div>
                      {activeTab === 'accounts' && (
                        <div className="text-sm text-gray-500 mt-0.5">
                          {item.type === 'cash' && '💵 Наличные'}
                          {item.type === 'bank' && '🏦 Банк'}
                          {item.type === 'card' && '💳 Карта'}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => handleEdit(item)}
                      className="w-10 h-10 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors flex items-center justify-center"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="w-10 h-10 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors flex items-center justify-center"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Аналитика */}
        {activeTab === 'analytics' && (
          <>
            {/* Analytics Tabs */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setAnalyticsTab('categories')}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                  analyticsTab === 'categories'
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gray-50 shadow-sm'
                }`}
              >
                🔗 Привязка категорий
              </button>
              <button
                onClick={() => setAnalyticsTab('blocks')}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                  analyticsTab === 'blocks'
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gray-50 shadow-sm'
                }`}
              >
                📊 Блоки
              </button>
            </div>

            {/* Привязка категорий */}
            {analyticsTab === 'categories' && (
              <div className="space-y-2">
                {loading && (
                  <div className="text-center py-8 text-gray-500">Загрузка...</div>
                )}

                {!loading && allCategories.filter(c => c.is_active).map((cat) => (
                  <div
                    key={cat.id}
                    className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex-1 font-medium text-gray-900">{cat.name}</div>
                      <select
                        value={getTypeForCategory(cat.id)}
                        onChange={(e) => handleTypeChange(cat.id, e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="none">Не привязано</option>
                        {analyticBlocks.map(block => (
                          <option key={block.code} value={block.code}>
                            {block.icon} {block.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Блоки */}
            {analyticsTab === 'blocks' && (
              <div>
                <button
                  onClick={() => setShowForm(true)}
                  className="w-full mb-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white py-4 rounded-xl font-medium shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  <span className="text-xl">➕</span>
                  <span>Добавить блок</span>
                </button>

                {loading && (
                  <div className="text-center py-8 text-gray-500">Загрузка...</div>
                )}

                {!loading && analyticBlocks.length === 0 && (
                  <div className="text-center py-12 text-gray-400">
                    <div className="text-5xl mb-3">📭</div>
                    <div>Блоков пока нет</div>
                  </div>
                )}

                {analyticBlocks.map((block) => (
                  <div
                    key={block.id}
                    className="bg-white border border-gray-200 rounded-xl p-4 mb-2 shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-2xl">{block.icon}</span>
                          <div>
                            <div className="font-bold text-lg">{block.name}</div>
                            <div className="text-xs text-gray-500">Код: {block.code}</div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>✅ Отлично: ≤ {block.threshold_good}%</div>
                          <div>⚠️ Норма: {block.threshold_good}% - {block.threshold_warning}%</div>
                          <div>❌ Проблема: &gt; {block.threshold_warning}%</div>
                        </div>
                      </div>
                      <div className="flex gap-2 flex-shrink-0">
                        <button
                          onClick={() => handleBlockEdit(block)}
                          className="w-10 h-10 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors flex items-center justify-center"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleBlockDelete(block.id)}
                          className="w-10 h-10 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors flex items-center justify-center"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Форма для категорий/счетов */}
      {showForm && activeTab !== 'analytics' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50">
          <div className="bg-white w-full rounded-t-3xl p-6 pb-8 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">
              {editItem ? '✏️ Редактировать' : '➕ Добавить'} {activeTab === 'categories' ? 'наименование' : 'счёт'}
            </h2>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Название *</label>
                <input
                  type="text"
                  placeholder={activeTab === 'categories' ? 'Например: Продукты' : 'Например: Касса Tashkent'}
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
              </div>

              {activeTab === 'accounts' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Тип счёта *</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Выберите тип</option>
                    <option value="cash">💵 Наличные</option>
                    <option value="bank">🏦 Банк</option>
                    <option value="card">💳 Карта</option>
                  </select>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSave}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3.5 rounded-xl font-medium shadow-lg transition-all"
              >
                💾 Сохранить
              </button>
              <button
                onClick={() => {
                  setShowForm(false);
                  setEditItem(null);
                }}
                className="flex-1 bg-gray-200 hover:bg-gray-300 py-3.5 rounded-xl font-medium transition-all"
              >
                ❌ Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Форма для блоков аналитики */}
      {showForm && activeTab === 'analytics' && analyticsTab === 'blocks' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50">
          <div className="bg-white w-full rounded-t-3xl p-6 pb-8 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editItem ? '✏️ Редактировать блок' : '➕ Добавить блок'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Код (уникальный) *</label>
                <input
                  type="text"
                  placeholder="rent_cost"
                  value={blockFormData.code}
                  onChange={(e) => setBlockFormData({ ...blockFormData, code: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={!!editItem}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Название *</label>
                <input
                  type="text"
                  placeholder="Rent Cost"
                  value={blockFormData.name}
                  onChange={(e) => setBlockFormData({ ...blockFormData, name: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Иконка</label>
                <input
                  type="text"
                  placeholder="🏠"
                  value={blockFormData.icon}
                  onChange={(e) => setBlockFormData({ ...blockFormData, icon: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Цвет</label>
                <select
                  value={blockFormData.color}
                  onChange={(e) => setBlockFormData({ ...blockFormData, color: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="blue">Синий</option>
                  <option value="emerald">Зелёный</option>
                  <option value="red">Красный</option>
                  <option value="yellow">Жёлтый</option>
                  <option value="purple">Фиолетовый</option>
                  <option value="gray">Серый</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Порог "Отлично" (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={blockFormData.threshold_good}
                    onChange={(e) => setBlockFormData({ ...blockFormData, threshold_good: parseFloat(e.target.value) })}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Порог "Проблема" (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={blockFormData.threshold_warning}
                    onChange={(e) => setBlockFormData({ ...blockFormData, threshold_warning: parseFloat(e.target.value) })}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Порядок сортировки</label>
                <input
                  type="number"
                  value={blockFormData.sort_order}
                  onChange={(e) => setBlockFormData({ ...blockFormData, sort_order: parseInt(e.target.value) })}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleBlockSave}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3.5 rounded-xl font-medium shadow-lg transition-all"
              >
                💾 Сохранить
              </button>
              <button
                onClick={() => {
                  setShowForm(false);
                  setEditItem(null);
                }}
                className="flex-1 bg-gray-200 hover:bg-gray-300 py-3.5 rounded-xl font-medium transition-all"
              >
                ❌ Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
