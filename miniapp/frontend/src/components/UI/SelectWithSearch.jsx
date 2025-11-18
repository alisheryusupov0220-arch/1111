import { useEffect, useMemo, useState } from 'react';

export default function SelectWithSearch({
  options = [],
  value,
  onChange,
  placeholder = 'Выберите...',
  label,
}) {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setSearch('');
    }
  }, [isOpen]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) {
      return options;
    }
    return options.filter((option) => option.name?.toLowerCase().includes(query));
  }, [options, search]);

  const selected = useMemo(() => options.find((option) => option.id === value), [options, value]);

  return (
    <div className="space-y-2">
      {label && <label className="block text-sm font-medium text-gray-700">{label}</label>}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="w-full px-4 py-3 rounded-xl border-2 border-gray-300 text-left text-base"
      >
        {selected ? selected.name : placeholder}
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50">
          <div className="bg-white w-full rounded-t-3xl p-6 max-h-[80vh] flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-bold">{label}</h3>
              <button onClick={() => setIsOpen(false)} className="text-2xl">
                ×
              </button>
            </div>

            <input
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="🔍 Поиск..."
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-300"
              autoFocus
            />

            <div className="overflow-y-auto space-y-2">
              {filtered.length === 0 && (
                <div className="text-sm text-gray-500 text-center py-6">Ничего не найдено</div>
              )}
              {filtered.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    onChange(option.id);
                    setIsOpen(false);
                  }}
                  className={`w-full px-4 py-3 rounded-xl text-left transition-colors ${
                    option.id === value ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {option.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

