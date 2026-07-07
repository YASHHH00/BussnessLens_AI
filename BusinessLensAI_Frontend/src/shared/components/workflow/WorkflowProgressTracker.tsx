import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, ChevronRight, Play } from 'lucide-react';
import { useAppStore, WORKFLOW_STEPS_LIST, WorkflowStep } from '../../stores/useAppStore';

export const WorkflowProgressTracker: React.FC<{ className?: string; compact?: boolean }> = ({ className, compact = false }) => {
  const currentStep = useAppStore((s) => s.currentWorkflowStep);
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);
  const navigate = useNavigate();

  const currentIndex = WORKFLOW_STEPS_LIST.findIndex((s) => s.id === currentStep);

  const handleStepClick = (stepId: WorkflowStep, path: string) => {
    setWorkflowStep(stepId);
    navigate(path);
  };

  if (compact) {
    const activeItem = WORKFLOW_STEPS_LIST[currentIndex] || WORKFLOW_STEPS_LIST[0];
    return (
      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card border border-border text-xs ${className || ''}`}>
        <span className="font-semibold text-muted-foreground uppercase tracking-wider">Step {currentIndex + 1}/10:</span>
        <span className="font-bold text-primary">{activeItem.label.replace(/^\d+\.\s*/, '')}</span>
      </div>
    );
  }

  return (
    <div className={`w-full overflow-x-auto pb-2 pt-1 ${className || ''}`}>
      <div className="flex items-center gap-1.5 min-w-max px-1">
        {WORKFLOW_STEPS_LIST.map((step, idx) => {
          const isCompleted = idx < currentIndex;
          const isCurrent = idx === currentIndex;

          return (
            <React.Fragment key={step.id}>
              <button
                onClick={() => handleStepClick(step.id, step.path)}
                className={`group flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 border ${
                  isCurrent
                    ? 'bg-primary text-primary-foreground border-primary shadow-sm ring-2 ring-primary/20 ring-offset-1 ring-offset-background font-bold'
                    : isCompleted
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
                    : 'bg-card text-muted-foreground border-border hover:bg-muted hover:text-foreground'
                }`}
              >
                <div
                  className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isCurrent
                      ? 'bg-primary-foreground text-primary'
                      : isCompleted
                      ? 'bg-emerald-500 text-white'
                      : 'bg-muted text-muted-foreground group-hover:bg-border'
                  }`}
                >
                  {isCompleted ? <Check className="w-2.5 h-2.5 stroke-[3]" /> : isCurrent ? <Play className="w-2 h-2 fill-current" /> : idx + 1}
                </div>
                <span>{step.label.replace(/^\d+\.\s*/, '')}</span>
              </button>

              {idx < WORKFLOW_STEPS_LIST.length - 1 && (
                <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/40 shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
