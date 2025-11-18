import { useLocation, useNavigate } from 'react-router-dom';

const NAV_ITEMS = [
  { id: 'home', icon: '🏠', label: 'Главная', path: '/' },
  { id: 'timeline', icon: '📊', label: 'Timeline', path: '/timeline' },
  { id: 'add', icon: '', label: '', path: '' }, // пустое место под FAB
  { id: 'analytics', icon: '📈', label: 'Аналитика', path: '/analytics' },
  { id: 'settings', icon: '⚙️', label: 'Настройки', path: '/settings' },
  { id: 'profile', icon: '👤', label: 'Профиль', path: '/profile' }
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t h-16 flex items-center justify-around px-2 z-40">
      {NAV_ITEMS.map((item) =>
        item.id === 'add' ? (
          <div key={item.id} className="w-16" />
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
      )}
    </nav>
  );
}

