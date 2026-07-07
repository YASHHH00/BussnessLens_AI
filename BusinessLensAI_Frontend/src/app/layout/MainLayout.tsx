import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { ErrorBoundary, WorkflowProgressTracker } from '../../shared/components';

export const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground antialiased selection:bg-primary/20 selection:text-primary">
      {/* Top sticky Navbar */}
      <Navbar />

      <div className="flex flex-1 relative">
        {/* Collapsible Left Sidebar */}
        <Sidebar />

        {/* Main Workspace Area */}
        <main className="flex-1 min-w-0 overflow-y-auto p-4 sm:p-6 lg:p-8 flex flex-col justify-between">
          <div className="space-y-6 max-w-7xl mx-auto w-full">
            {/* 10-Step Workflow Progress Bar */}
            <WorkflowProgressTracker />

            {/* Error boundary wrapping routed page content */}
            <ErrorBoundary title="Page Rendering Exception">
              <Outlet />
            </ErrorBoundary>
          </div>

          {/* Platform Footer */}
          <footer className="mt-16 pt-6 border-t border-border text-center text-xs text-muted-foreground flex flex-col sm:flex-row items-center justify-between gap-4 max-w-7xl mx-auto w-full">
            <div>
              © 2026 <strong>BusinessLens AI</strong>. Built for enterprise self-service business intelligence.
            </div>
            <div className="flex items-center gap-4">
              <span>SOC2 Type II Compliant</span>
              <span>•</span>
              <span>PostgreSQL v16.2 Live</span>
              <span>•</span>
              <span className="text-emerald-500 font-semibold">All Systems Operational</span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
};
