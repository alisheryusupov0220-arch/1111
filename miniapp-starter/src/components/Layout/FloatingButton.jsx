import { useState } from 'react';
import AddModal from '../Modals/AddModal';

export default function FloatingButton() {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      {/* Центральная кнопка "+" */}
      <button
        onClick={() => setShowModal(true)}
        className="
          fixed bottom-20 left-1/2 -translate-x-1/2
          w-16 h-16 rounded-full z-50
          bg-blue-500 shadow-lg
          flex items-center justify-center
          text-white text-4xl font-light
          hover:bg-blue-600 active:scale-95
          transition-all duration-200
        "
        style={{ 
          boxShadow: '0 4px 20px rgba(59, 130, 246, 0.4)'
        }}
      >
        +
      </button>

      {/* Модальное окно выбора */}
      {showModal && (
        <AddModal onClose={() => setShowModal(false)} />
      )}
    </>
  );
}
