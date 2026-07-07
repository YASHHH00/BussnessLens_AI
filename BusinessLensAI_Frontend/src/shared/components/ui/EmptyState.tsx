import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Database, FolderOpen, Search, BarChart3, AlertCircle } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: 'database' | 'folder' | 'search' | 'chart' | 'alert' | React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = 'folder',
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  className,
}) => {
  const icons = {
    database: <Database className="w-10 h-10 text-primary" />,
    folder: <FolderOpen className="w-10 h-10 text-primary" />,
    search: <Search className="w-10 h-10 text-primary" />,
    chart: <BarChart3 className="w-10 h-10 text-primary" />,
    alert: <AlertCircle className="w-10 h-10 text-destructive" />,
  };

  return (
    <div
      className={twMerge(
        clsx(
          'flex flex-col items-center justify-center text-center p-12 rounded-xl border border-dashed border-border bg-card/40 my-6 animate-in fade-in-50 duration-300',
          className
        )
      )}
    >
      <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6 shadow-inner">
        {typeof icon === 'string' ? icons[icon as keyof typeof icons] || icons.folder : icon}
      </div>
      <h3 className="text-lg font-semibold text-foreground tracking-tight mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-8 leading-relaxed">{description}</p>
      
      {(actionLabel || secondaryActionLabel) && (
        <div className="flex flex-wrap items-center justify-center gap-3">
          {actionLabel && onAction && (
            <Button variant="primary" size="md" onClick={onAction}>
              {actionLabel}
            </Button>
          )}
          {secondaryActionLabel && onSecondaryAction && (
            <Button variant="outline" size="md" onClick={onSecondaryAction}>
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
