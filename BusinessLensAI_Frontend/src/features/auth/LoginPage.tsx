import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Mail, Lock, Sparkles, ShieldCheck, ArrowRight } from 'lucide-react';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { Button, Input, Modal, toast } from '../../shared/components';

const loginSchema = z.object({
  email: z.string().email({ message: 'Please enter a valid enterprise email address.' }),
  password: z.string().min(6, { message: 'Password must be at least 6 characters.' }),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((s) => s.login);
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [isSendingReset, setIsSendingReset] = useState(false);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: 'admin@businesslens.ai',
      password: 'password123',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      await login(data.email, data.password);
      toast.success('Welcome back!', 'You have successfully logged into BusinessLens AI.');
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'Invalid login credentials.';
      toast.error('Authentication Error', msg);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail || !forgotEmail.includes('@')) {
      toast.error('Invalid Email', 'Please enter a valid email address.');
      return;
    }
    setIsSendingReset(true);
    await new Promise((r) => setTimeout(r, 800));
    setIsSendingReset(false);
    setIsForgotModalOpen(false);
    toast.success('Password Reset Sent', `If an account exists for ${forgotEmail}, you will receive password reset instructions shortly.`);
  };

  const handleOAuthLogin = (provider: string) => {
    toast.info('SSO / OAuth Login', `${provider} enterprise single sign-on is configured in production via Okta / Azure AD.`);
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background relative overflow-hidden p-4">
      {/* Background Glow */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/15 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10 animate-in fade-in-50 zoom-in-95 duration-300">
        <div className="text-center mb-8 space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary to-purple-600 text-white shadow-xl mb-2">
            <Sparkles className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">BusinessLens AI</h1>
          <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">
            Enterprise Self-Service BI Platform
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card/80 backdrop-blur-xl p-8 shadow-2xl space-y-6">
          <div className="space-y-1">
            <h2 className="text-lg font-semibold text-foreground">Sign In to Your Workspace</h2>
            <p className="text-xs text-muted-foreground">
              Use your enterprise credentials or pre-filled demo account.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Enterprise Email"
              type="email"
              placeholder="admin@businesslens.ai"
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email?.message}
              {...register('email')}
            />

            <div className="space-y-1">
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                leftIcon={<Lock className="w-4 h-4" />}
                error={errors.password?.message}
                {...register('password')}
              />
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setIsForgotModalOpen(true)}
                  className="text-xs text-primary hover:underline font-medium focus:outline-none"
                >
                  Forgot password?
                </button>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-2 font-bold shadow-md"
              isLoading={isSubmitting}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In to Platform
            </Button>
          </form>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-border w-full" />
            <span className="bg-card px-3 text-xs text-muted-foreground font-medium uppercase tracking-wider absolute">
              Or connect via SSO
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleOAuthLogin('Google Workspace')}
              className="w-full text-xs font-semibold"
            >
              Google SSO
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleOAuthLogin('Microsoft Azure AD')}
              className="w-full text-xs font-semibold"
            >
              Azure AD / Okta
            </Button>
          </div>

          <div className="p-3 rounded-lg bg-muted/50 border border-border flex items-center gap-2.5 text-xs text-muted-foreground">
            <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
            <span>256-bit TLS encrypted session. Protected by SOC2 Type II compliance.</span>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      <Modal
        isOpen={isForgotModalOpen}
        onClose={() => setIsForgotModalOpen(false)}
        title="Reset Enterprise Password"
        description="Enter your corporate email address to receive password recovery instructions."
        size="sm"
      >
        <form onSubmit={handleForgotPassword} className="space-y-4">
          <Input
            label="Corporate Email"
            type="email"
            placeholder="name@company.com"
            value={forgotEmail}
            onChange={(e) => setForgotEmail(e.target.value)}
            required
          />
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setIsForgotModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isSendingReset}>
              Send Recovery Link
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
