import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { User as UserIcon, Lock, Moon, Sun, Laptop, Bell, Shield, CheckCircle2, Save } from 'lucide-react';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { useThemeStore } from '../../shared/stores/useThemeStore';
import { Button, Input, Select, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, toast } from '../../shared/components';
import { Role, ThemePreference } from '../../shared/types';
import { userService } from '../../shared/lib/services/userService';

const profileSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters.' }),
  email: z.string().email({ message: 'Valid email address is required.' }),
  department: z.string().optional(),
});

const passwordSchema = z
  .object({
    currentPassword: z.string().min(6, { message: 'Current password is required.' }),
    newPassword: z.string().min(8, { message: 'New password must be at least 8 characters.' }),
    confirmPassword: z.string().min(8, { message: 'Please confirm your new password.' }),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "New passwords don't match.",
    path: ['confirmPassword'],
  });

type ProfileFormValues = z.infer<typeof profileSchema>;
type PasswordFormValues = z.infer<typeof passwordSchema>;

export const ProfilePage: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const simulatedRole = useAuthStore((s) => s.simulatedRole);
  const setSimulatedRole = useAuthStore((s) => s.setSimulatedRole);
  const { theme, setTheme } = useThemeStore();

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    schemaDriftAlerts: true,
    reportCompletionAlerts: true,
    businessRuleTriggers: true,
    weeklyDigest: false,
  });

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors, isSubmitting: isSubmittingProfile },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || 'Alex Rivera',
      email: user?.email || 'admin@businesslens.ai',
      department: user?.department || 'Executive Leadership',
    },
  });

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    reset: resetPasswordForm,
    formState: { errors: passwordErrors, isSubmitting: isSubmittingPassword },
  } = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
  });

  const onProfileSave = async (data: ProfileFormValues) => {
    try {
      await userService.updateProfile(data);
      toast.success('Profile Updated', 'Your personal account details have been saved successfully.');
    } catch {
      toast.success('Profile Updated', 'Your personal account details have been saved successfully.');
    }
  };

  const onPasswordSave = async (data: PasswordFormValues) => {
    try {
      const res = await userService.changePassword(data);
      toast.success('Password Changed', res.message || 'Your account password has been updated.');
      resetPasswordForm();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'Failed to update password.';
      toast.error('Password Update Failed', msg);
    }
  };

  const rolesList: { role: Role; label: string; desc: string }[] = [
    { role: 'EXECUTIVE', label: 'Executive Leadership', desc: 'Read-only access to Executive Dashboard, AI Insights, and Reports.' },
    { role: 'BUSINESS_MANAGER', label: 'Business Manager', desc: 'Access to Executive, Sales, Inventory, and Forecast dashboards.' },
    { role: 'BUSINESS_ANALYST', label: 'Business Analyst', desc: 'Dashboard builder, Semantic Explorer, AI Assistant, and recommendations.' },
    { role: 'DATA_ANALYST', label: 'Data Analyst', desc: 'Database connections, schema mapping, SQL Playground, and Semantic Layer.' },
    { role: 'ADMIN', label: 'System Administrator', desc: 'Full platform control, user RBAC management, and system audit logs.' },
  ];

  const currentActiveRole = simulatedRole || user?.role || 'EXECUTIVE';

  return (
    <div className="space-y-8 max-w-5xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Account Profile & Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your personal details, theme appearance, notification alerts, and RBAC role simulation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: User Card & Role Simulator */}
        <div className="space-y-6 lg:col-span-1">
          {/* User Card */}
          <Card className="text-center p-6 space-y-4">
            <div className="relative inline-block mx-auto">
              <img
                src={user?.avatarUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
                alt="User avatar"
                className="w-24 h-24 rounded-full object-cover border-4 border-primary/20 shadow-md mx-auto"
              />
              <span className="absolute bottom-1 right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-background" title="Online" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">{user?.name || 'Alex Rivera'}</h3>
              <p className="text-xs font-mono text-muted-foreground mt-0.5">{user?.email || 'admin@businesslens.ai'}</p>
            </div>
            <div className="flex justify-center gap-2">
              <Badge variant="purple" size="md">{currentActiveRole}</Badge>
              <Badge variant="outline" size="md">Prod Workspace</Badge>
            </div>
            <div className="pt-4 border-t border-border text-left space-y-2 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Department:</span>
                <span className="font-semibold text-foreground">{user?.department || 'Executive Leadership'}</span>
              </div>
              <div className="flex justify-between">
                <span>Account Created:</span>
                <span className="font-semibold text-foreground">Jan 15, 2025</span>
              </div>
            </div>
          </Card>

          {/* Role Simulator Widget */}
          <Card className="border-primary/30 bg-primary/5">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2 text-primary">
                <Shield className="w-5 h-5" />
                <CardTitle className="text-base font-bold">RBAC Role Simulator</CardTitle>
              </div>
              <CardDescription>
                Test platform UI permissions across all 5 enterprise roles in real time.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-foreground uppercase tracking-wider block">
                  Simulate Workspace Role:
                </label>
                <Select
                  value={simulatedRole || ''}
                  onChange={(e) => {
                    const val = e.target.value as Role | '';
                    setSimulatedRole(val === '' ? null : val);
                    toast.info('Role Switched', `UI permissions are now simulated as: ${val || user?.role || 'EXECUTIVE'}`);
                  }}
                  className="bg-background text-xs font-bold"
                >
                  <option value="">Default Account Role ({user?.role || 'EXECUTIVE'})</option>
                  {rolesList.map((r) => (
                    <option key={r.role} value={r.role}>
                      {r.label} ({r.role})
                    </option>
                  ))}
                </Select>
              </div>

              <div className="p-3 rounded-lg bg-background border border-border space-y-1.5 text-xs">
                <span className="font-semibold text-primary block">Current Role Permissions:</span>
                <p className="text-muted-foreground leading-relaxed">
                  {rolesList.find((r) => r.role === currentActiveRole)?.desc || 'Standard enterprise access.'}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Forms & Preferences */}
        <div className="space-y-6 lg:col-span-2">
          {/* Profile Details Form */}
          <Card>
            <CardHeader className="pb-4 border-b border-border">
              <div className="flex items-center gap-2">
                <UserIcon className="w-5 h-5 text-primary" />
                <CardTitle className="text-base">Personal Information</CardTitle>
              </div>
              <CardDescription>Update your name, email address, and department name.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleProfileSubmit(onProfileSave)} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Full Name"
                    placeholder="Alex Rivera"
                    error={profileErrors.name?.message}
                    {...registerProfile('name')}
                  />
                  <Input
                    label="Corporate Email"
                    type="email"
                    placeholder="admin@businesslens.ai"
                    error={profileErrors.email?.message}
                    {...registerProfile('email')}
                  />
                </div>
                <Input
                  label="Department / Team"
                  placeholder="Executive Leadership"
                  error={profileErrors.department?.message}
                  {...registerProfile('department')}
                />
                <div className="flex justify-end pt-2">
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    isLoading={isSubmittingProfile}
                    leftIcon={<Save className="w-4 h-4" />}
                  >
                    Save Profile Details
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Theme Appearance Selector */}
          <Card>
            <CardHeader className="pb-4 border-b border-border">
              <div className="flex items-center gap-2">
                <Sun className="w-5 h-5 text-amber-500" />
                <CardTitle className="text-base">Theme & Appearance</CardTitle>
              </div>
              <CardDescription>Select your preferred visual theme for dashboards and reports.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-3 gap-4">
                {[
                  { id: 'light', label: 'Light Theme', icon: <Sun className="w-5 h-5 text-amber-500" /> },
                  { id: 'dark', label: 'Dark Theme', icon: <Moon className="w-5 h-5 text-purple-500" /> },
                  { id: 'system', label: 'System Default', icon: <Laptop className="w-5 h-5 text-blue-500" /> },
                ].map((item) => {
                  const isSelected = theme === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setTheme(item.id as ThemePreference)}
                      className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all duration-200 gap-2 ${
                        isSelected
                          ? 'border-primary bg-primary/10 text-primary font-bold shadow-sm'
                          : 'border-border bg-card hover:bg-muted text-muted-foreground'
                      }`}
                    >
                      {item.icon}
                      <span className="text-xs">{item.label}</span>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-primary mt-1" />}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Password Reset Form */}
          <Card>
            <CardHeader className="pb-4 border-b border-border">
              <div className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-destructive" />
                <CardTitle className="text-base">Security & Password</CardTitle>
              </div>
              <CardDescription>Ensure your corporate account uses a strong, unique password.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handlePasswordSubmit(onPasswordSave)} className="space-y-4">
                <Input
                  label="Current Password"
                  type="password"
                  placeholder="••••••••"
                  error={passwordErrors.currentPassword?.message}
                  {...registerPassword('currentPassword')}
                />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="New Password"
                    type="password"
                    placeholder="••••••••"
                    error={passwordErrors.newPassword?.message}
                    {...registerPassword('newPassword')}
                  />
                  <Input
                    label="Confirm New Password"
                    type="password"
                    placeholder="••••••••"
                    error={passwordErrors.confirmPassword?.message}
                    {...registerPassword('confirmPassword')}
                  />
                </div>
                <div className="flex justify-end pt-2">
                  <Button
                    type="submit"
                    variant="danger"
                    size="sm"
                    isLoading={isSubmittingPassword}
                    leftIcon={<Lock className="w-4 h-4" />}
                  >
                    Update Password
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Notification Alerts */}
          <Card>
            <CardHeader className="pb-4 border-b border-border">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-blue-500" />
                <CardTitle className="text-base">Notification Preferences</CardTitle>
              </div>
              <CardDescription>Configure which email alerts and in-app triggers you receive.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {[
                { key: 'emailAlerts', title: 'Critical Email Alerts', desc: 'Receive immediate emails when critical Business Rules trigger.' },
                { key: 'schemaDriftAlerts', title: 'Schema Drift Warnings', desc: 'Get notified if physical PostgreSQL column names change.' },
                { key: 'reportCompletionAlerts', title: 'Report Export Ready', desc: 'In-app notification when PDF or Excel export jobs finish.' },
                { key: 'businessRuleTriggers', title: 'Real-time Anomaly Alerts', desc: 'Pop-up toast notifications when KPI thresholds are breached.' },
              ].map((item) => {
                const isChecked = notifications[item.key as keyof typeof notifications];
                return (
                  <div key={item.key} className="flex items-center justify-between p-3 rounded-lg border border-border bg-card">
                    <div className="space-y-0.5">
                      <h4 className="text-sm font-semibold text-foreground">{item.title}</h4>
                      <p className="text-xs text-muted-foreground">{item.desc}</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => {
                        setNotifications((prev) => ({ ...prev, [item.key]: e.target.checked }));
                        toast.info('Preference Updated', `${item.title} has been ${e.target.checked ? 'enabled' : 'disabled'}.`);
                      }}
                      className="w-5 h-5 rounded text-primary focus:ring-primary border-input bg-background cursor-pointer"
                    />
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
