import React, { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handleAddToast = (e: CustomEvent<Omit<ToastMessage, 'id'> & { id?: string }>) => {
      const newToast = { ...e.detail, id: e.detail.id || `toast_${Date.now()}` };
      setToasts((prev) => [...prev, newToast as ToastMessage]);

      if (newToast.duration !== 0) {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== newToast.id));
        }, newToast.duration || 5000);
      }
    };

    const handleSessionExpired = () => {
      handleAddToast(
        new CustomEvent('bl_toast', {
          detail: {
            type: 'warning',
            title: 'Session Expired',
            message: 'Your authentication session expired. Please sign in again.',
            duration: 8000,
          },
        })
      );
    };

    window.addEventListener('bl_toast' as unknown as keyof WindowEventMap, handleAddToast as unknown as EventListener);
    window.addEventListener('bl_session_expired', handleSessionExpired);

    return () => {
      window.removeEventListener('bl_toast' as unknown as keyof WindowEventMap, handleAddToast as unknown as EventListener);
      window.removeEventListener('bl_session_expired', handleSessionExpired);
    };
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-destructive shrink-0" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />,
    info: <Info className="w-5 h-5 text-blue-500 shrink-0" />,
  };

  const borderColors = {
    success: 'border-l-4 border-l-emerald-500',
    error: 'border-l-4 border-l-destructive',
    warning: 'border-l-4 border-l-amber-500',
    info: 'border-l-4 border-l-blue-500',
  };

  return (
    <>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={twMerge(
              clsx(
                'pointer-events-auto flex items-start gap-3 p-4 rounded-lg bg-card border border-border shadow-lg animate-in slide-in-from-bottom-5 duration-200',
                borderColors[toast.type]
              )
            )}
          >
            {icons[toast.type]}
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-semibold text-foreground">{toast.title}</h4>
              {toast.message && <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{toast.message}</p>}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-muted-foreground hover:text-foreground p-0.5 rounded transition-colors focus:outline-none"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </>
  );
};

export const toast = {
  show: (toast: Omit<ToastMessage, 'id'>) => {
    window.dispatchEvent(new CustomEvent('bl_toast', { detail: toast }));
  },
  success: (title: string, message?: string) => toast.show({ type: 'success', title, message }),
  error: (title: string, message?: string) => toast.show({ type: 'error', title, message }),
  warning: (title: string, message?: string) => toast.show({ type: 'warning', title, message }),
  info: (title: string, message?: string) => toast.show({ type: 'info', title, message }),
};
