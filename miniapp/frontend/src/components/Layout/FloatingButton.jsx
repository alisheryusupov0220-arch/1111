import { useState } from 'react';
import AddModal from '../Modals/AddModal';

export default function FloatingButton({ onClick }) {
  return (
    <button
      onClick={(e) => {
        console.log('FloatingButton clicked');
        onClick?.(e);
      }}
      className="fixed bottom-6 left-1/2 -translate-x-1/2 w-14 h-14 bg-blue-500 text-white rounded-full shadow-xl hover:bg-blue-600 active:scale-95 transition-all flex items-center justify-center z-50"
      style={{ zIndex: 9999, pointerEvents: 'auto' }}
    >
      <span className="text-3xl font-light leading-none pb-0.5">+</span>
    </button>
  );
}
