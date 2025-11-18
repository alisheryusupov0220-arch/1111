export default function Header({ user }) {
  return (
    <header className="bg-white border-b px-4 py-3 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <span className="text-2xl">💰</span>
        <h1 className="text-lg font-bold">Air Waffle Finance</h1>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">
          {user?.full_name || user?.username || 'Пользователь'}
        </span>
        {user?.photo_url && (
          <img
            src={user.photo_url}
            alt="avatar"
            className="w-8 h-8 rounded-full object-cover"
          />
        )}
      </div>
    </header>
  );
}


