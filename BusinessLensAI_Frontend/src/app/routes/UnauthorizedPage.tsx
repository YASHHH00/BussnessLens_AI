import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, Shield, Sparkles } from 'lucide-react';
import { Button, Card, CardContent, Badge } from '../../shared/components';
import { usePermission } from '../../shared/hooks/usePermission';

export const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentRole } = usePermission();

  return (
    <div className="min-h-[75vh] w-full flex items-center justify-center p-4 animate-in fade-in-50 duration-300">
      <Card className="max-w-lg w-full text-center p-8 border-destructive/30 shadow-2xl space-y-6">
        <div className="w-16 h-16 rounded-full bg-destructive/10 text-destructive flex items-center justify-center mx-auto shadow-inner">
          <ShieldAlert className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <Badge variant="danger" size="md">RBAC Access Restricted</Badge>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Permission Gate Triggered</h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Your current active role (<strong className="text-foreground uppercase">{currentRole}</strong>) does not have sufficient administrative or analytical permissions to access this module.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-muted/50 border border-border text-left space-y-2 text-xs">
          <span className="font-semibold text-foreground flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-primary" />
            How to preview this feature:
          </span>
          <p className="text-muted-foreground leading-relaxed">
            You can test this restricted feature by opening your <strong className="text-primary">Account Profile</strong> and using the <strong className="text-primary">RBAC Role Simulator</strong> to temporarily switch your role to <strong className="text-foreground">Data Analyst</strong> or <strong className="text-foreground">System Administrator</strong>.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Button
            variant="outline"
            size="md"
            onClick={() => navigate('/')}
            leftIcon={<ArrowLeft className="w-4 h-4" />}
            className="w-full sm:w-auto"
          >
            Return to Dashboard
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/profile')}
            rightIcon={<Sparkles className="w-4 h-4" />}
            className="w-full sm:w-auto"
          >
            Open Role Simulator
          </Button>
        </div>
      </Card>
    </div>
  );
};
