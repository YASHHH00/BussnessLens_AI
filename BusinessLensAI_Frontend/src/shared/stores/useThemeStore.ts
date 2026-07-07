/**
 * Zustand Theme Store managing dark / light / system default preferences
 */
import { create } from 'zustand';
import { ThemePreference } from '@/shared/types';

interface ThemeStoreState {
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  applyTheme: () => void;
}

const STORAGE_KEY = 'bl_theme_preference';

const getInitialTheme = (): ThemePreference => {
  if (typeof window === 'undefined') return 'system';
  const stored = localStorage.getItem(STORAGE_KEY) as ThemePreference;
  if (stored && ['dark', 'light', 'system'].includes(stored)) {
    return stored;
  }
  return 'system';
};

export const useThemeStore = create<ThemeStoreState>((set, get) => ({
  theme: getInitialTheme(),

  setTheme: (newTheme: ThemePreference) => {
    localStorage.setItem(STORAGE_KEY, newTheme);
    set({ theme: newTheme });
    get().applyTheme();
  },

  applyTheme: () => {
    if (typeof window === 'undefined') return;
    const root = window.document.documentElement;
    const { theme } = get();

    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
      return;
    }

    root.classList.add(theme);
  },
}));

// Listen for OS system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const store = useThemeStore.getState();
    if (store.theme === 'system') {
      store.applyTheme();
    }
  });
  
  // Apply initial theme
  useThemeStore.getState().applyTheme();
}
