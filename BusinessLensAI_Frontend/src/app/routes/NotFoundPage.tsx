import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileQuestion, ArrowLeft, Home } from 'lucide-react';
import { Button, Card, CardContent } from '../../shared/components';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[75vh] w-full flex items-center justify-center p-4 animate-in fade-in-50 duration-300">
      <Card className="max-w-md w-full text-center p-8 shadow-xl space-y-6">
        <div className="w-16 h-16 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto shadow-inner">
          <FileQuestion className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">404 - Page Not Found</h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            The requested workspace URL or analytical dashboard route does not exist in BusinessLens AI.
          </p>
        </div>

        <div className="flex items-center justify-center gap-3 pt-2">
          <Button variant="outline" size="md" onClick={() => navigate(-1)} leftIcon={<ArrowLeft className="w-4 h-4" />}>
            Go Back
          </Button>
          <Button variant="primary" size="md" onClick={() => navigate('/')} leftIcon={<Home className="w-4 h-4" />}>
            Platform Home
          </Button>
        </div>
      </Card>
    </div>
  );
};
