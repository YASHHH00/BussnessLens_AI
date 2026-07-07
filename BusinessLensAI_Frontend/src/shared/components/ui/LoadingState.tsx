import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface LoadingSkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<LoadingSkeletonProps> = ({ className }) => {
  return <div className={twMerge(clsx('animate-pulse rounded-md bg-muted/60', className))} />;
};

export interface LoadingStateProps {
  type?: 'card' | 'table' | 'chart' | 'dashboard' | 'text' | 'list';
  count?: number;
  className?: string;
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ type = 'card', count = 3, className, message }) => {
  if (type === 'dashboard') {
    return (
      <div className="space-y-6 w-full animate-in fade-in-50 duration-300">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-72" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="p-6 rounded-xl border border-border bg-card space-y-3">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-32" />
              <Skeleton className="h-3 w-16" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl border border-border bg-card space-y-4">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-64 w-full" />
          </div>
          <div className="p-6 rounded-xl border border-border bg-card space-y-4">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="w-full rounded-xl border border-border bg-card overflow-hidden space-y-4 p-4 animate-in fade-in-50 duration-300">
        <div className="flex items-center justify-between pb-2 border-b border-border">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="space-y-3">
          <Skeleton className="h-10 w-full bg-muted" />
          {[...Array(count)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (type === 'chart') {
    return (
      <div className={twMerge(clsx('p-6 rounded-xl border border-border bg-card space-y-4 animate-in fade-in-50 duration-300', className))}>
        <div className="flex justify-between items-center">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-20" />
        </div>
        <Skeleton className="h-64 w-full rounded-lg" />
      </div>
    );
  }

  if (type === 'list') {
    return (
      <div className="space-y-3 w-full animate-in fade-in-50 duration-300">
        {[...Array(count)].map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4 rounded-lg border border-border bg-card">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-3 w-2/3" />
            </div>
            <Skeleton className="h-8 w-20" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={twMerge(clsx('grid grid-cols-1 md:grid-cols-3 gap-4 w-full animate-in fade-in-50 duration-300', className))}>
      {[...Array(count)].map((_, i) => (
        <div key={i} className="p-6 rounded-xl border border-border bg-card space-y-3">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          {message && <p className="text-xs text-muted-foreground pt-2 animate-pulse">{message}</p>}
        </div>
      ))}
    </div>
  );
};
