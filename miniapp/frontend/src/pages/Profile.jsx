import { useTelegram } from '../hooks/useTelegram';

export default function Profile() {
  const { user } = useTelegram();

  return (
    <div className="p-4 pb-24 space-y-4">
      <h2 className="text-2xl font-bold">Профиль</h2>

      <div className="bg-white rounded-xl p-6 shadow-sm space-y-3">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-blue-500 text-white flex items-center justify-center text-2xl">
            {user?.first_name?.[0] || '👤'}
          </div>
          <div>
            <div className="text-lg font-semibold">{user?.first_name}</div>
            <div className="text-gray-500 text-sm">@{user?.username}</div>
          </div>
        </div>

        <div className="text-sm text-gray-500">
          Telegram ID: <span className="font-mono">{user?.id}</span>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-2">Статус</h3>
        <p className="text-gray-500 text-sm">
          Доступ к функционалу определяется правами, выданными в основной системе.
        </p>
      </div>
    </div>
  );
}


