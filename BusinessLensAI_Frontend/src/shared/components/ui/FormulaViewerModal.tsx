import React from 'react';
import { Calculator, BookOpen, Layers, CheckCircle2 } from 'lucide-react';
import { Modal } from './Modal';
import { Badge } from './Badge';
import { Button } from './Button';

export interface FormulaViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  kpiTitle: string;
  formula: string;
  variables?: { name: string; description: string; sourceColumn: string }[];
  businessMeaning?: string;
  dependencies?: string[];
}

export const FormulaViewerModal: React.FC<FormulaViewerModalProps> = ({
  isOpen,
  onClose,
  kpiTitle,
  formula,
  variables = [],
  businessMeaning,
  dependencies = [],
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`KPI Formula Viewer: ${kpiTitle}`} size="lg">
      <div className="space-y-6">
        {/* Formula Box */}
        <div className="p-4 rounded-xl bg-muted/60 border border-border space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            <Calculator className="w-4 h-4 text-primary" />
            <span>Mathematical Formula</span>
          </div>
          <div className="p-3 rounded-lg bg-background border border-border font-mono text-base font-bold text-primary tracking-wide flex items-center justify-between">
            <span>{kpiTitle} = {formula}</span>
            <Badge variant="success">Active</Badge>
          </div>
        </div>

        {/* Business Meaning */}
        {businessMeaning && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
              <BookOpen className="w-4 h-4 text-blue-500" />
              <span>Business Meaning & Definition</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed p-3 rounded-lg bg-card border border-border">
              {businessMeaning}
            </p>
          </div>
        )}

        {/* Variables Table */}
        {variables.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
              <Layers className="w-4 h-4 text-amber-500" />
              <span>Formula Variables & Source Columns</span>
            </div>
            <div className="rounded-lg border border-border overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted/50 border-b border-border text-muted-foreground">
                  <tr>
                    <th className="p-2.5 font-semibold">Variable Name</th>
                    <th className="p-2.5 font-semibold">Physical Source Column</th>
                    <th className="p-2.5 font-semibold">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border bg-card">
                  {variables.map((varItem, idx) => (
                    <tr key={idx} className="hover:bg-muted/20">
                      <td className="p-2.5 font-mono font-semibold text-primary">{varItem.name}</td>
                      <td className="p-2.5 font-mono text-muted-foreground">{varItem.sourceColumn}</td>
                      <td className="p-2.5 text-foreground">{varItem.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Dependencies */}
        {dependencies.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-foreground uppercase tracking-wider">
              Data Table Dependencies
            </div>
            <div className="flex flex-wrap gap-2">
              {dependencies.map((dep, idx) => (
                <div key={idx} className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-xs font-medium border border-border">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>{dep}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end pt-4 border-t border-border">
          <Button variant="primary" onClick={onClose}>
            Close Formula Viewer
          </Button>
        </div>
      </div>
    </Modal>
  );
};
