/**
 * User Profile and Preferences types
 */

export type ThemePreference = 'dark' | 'light' | 'system';

export interface NotificationPreferences {
  emailAlerts: boolean;
  schemaDriftAlerts: boolean;
  reportCompletionAlerts: boolean;
  businessRuleTriggers: boolean;
  weeklyDigest: boolean;
}

export interface UserSettings {
  userId: string;
  theme: ThemePreference;
  defaultDashboardId?: string;
  defaultDomain: string; // 'RETAIL' by default
  notifications: NotificationPreferences;
}

export interface UserProfileFormValues {
  name: string;
  email: string;
  avatarUrl?: string;
  department?: string;
}

export interface PasswordChangeFormValues {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
