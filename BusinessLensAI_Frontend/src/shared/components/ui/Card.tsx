import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  isGlass?: boolean;
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({ className, isGlass = false, hoverEffect = false, children, ...props }) => {
  return (
    <div
      className={twMerge(
        clsx(
          'rounded-xl border border-border bg-card text-card-foreground shadow-sm transition-all duration-200',
          isGlass && 'bg-card/80 backdrop-blur-md',
          hoverEffect && 'hover:shadow-md hover:border-primary/30 hover:-translate-y-0.5',
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={twMerge(clsx('flex flex-col space-y-1.5 p-6 pb-3', className))} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, children, ...props }) => (
  <h3 className={twMerge(clsx('text-lg font-semibold leading-none tracking-tight text-foreground', className))} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ className, children, ...props }) => (
  <p className={twMerge(clsx('text-xs text-muted-foreground', className))} {...props}>
    {children}
  </p>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={twMerge(clsx('p-6 pt-0', className))} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={twMerge(clsx('flex items-center p-6 pt-0', className))} {...props}>
    {children}
  </div>
);
