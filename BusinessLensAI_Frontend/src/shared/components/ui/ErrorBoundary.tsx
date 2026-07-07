import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
  title?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in ErrorBoundary:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center min-h-[300px] p-8 text-center bg-card/50 rounded-xl border border-border shadow-sm my-4">
          <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center text-destructive mb-4">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-foreground mb-1">
            {this.props.title || 'Something went wrong while rendering this view.'}
          </h3>
          <p className="text-xs text-muted-foreground max-w-md mb-6 leading-relaxed">
            {this.state.error?.message || 'An unexpected runtime exception occurred in this component module.'}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={this.handleReset}
            leftIcon={<RefreshCw className="w-4 h-4" />}
          >
            Retry Action
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
