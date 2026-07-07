import React, { useState } from 'react';
import { BarChart3, Plus, Sparkles } from 'lucide-react';
import { Modal, Button, Input, Select, toast } from '../../shared/components';
import { DashboardWidget, WidgetType } from '../../shared/types';

export interface WidgetBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddWidget: (widget: DashboardWidget) => void;
}

export const WidgetBuilderModal: React.FC<WidgetBuilderModalProps> = ({ isOpen, onClose, onAddWidget }) => {
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [type, setType] = useState<WidgetType>('BAR_CHART');
  const [metric, setMetric] = useState('revenue');
  const [dimension, setDimension] = useState('category');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      toast.error('Validation Error', 'Widget title is required.');
      return;
    }

    const newWidget: DashboardWidget = {
      id: `w_custom_${Date.now()}`,
      title: title.trim(),
      subtitle: subtitle.trim() || `Custom analysis: ${metric} by ${dimension}`,
      type,
      width: type === 'METRIC_CARD' ? 3 : 6,
      height: type === 'METRIC_CARD' ? 140 : 320,
      metric,
      filters: {} as any,
      gridPos: { x: 0, y: 0, w: 6, h: 4 },
      config: {
        metric,
        dimension,
        colorScheme: 'primary',
      },
      aiExplanation: `Custom user-generated visualization mapping physical column ${metric} aggregated across ${dimension}.`,
      data: [
        { name: 'Electronics', value: 425000 },
        { name: 'Apparel', value: 310000 },
        { name: 'Home Goods', value: 280000 },
        { name: 'Accessories', value: 150000 },
      ],
    };

    onAddWidget(newWidget);
    toast.success('Widget Added', `Custom ${type.replace('_', ' ')} has been added to your dashboard.`);
    setTitle('');
    setSubtitle('');
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Custom Dashboard Widget Builder"
      description="Create a custom visualization or KPI card from your confirmed semantic mappings."
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input label="Widget Title" placeholder="e.g. Revenue by Product Category" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <Input label="Subtitle / Description (Optional)" placeholder="e.g. Q3 performance comparison" value={subtitle} onChange={(e) => setSubtitle(e.target.value)} />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Select label="Visualization Type" value={type} onChange={(e) => setType(e.target.value as WidgetType)}>
            <option value="BAR_CHART">Bar Chart</option>
            <option value="LINE_CHART">Line Chart</option>
            <option value="AREA_CHART">Area Trend Chart</option>
            <option value="PIE_CHART">Donut / Pie Chart</option>
            <option value="METRIC_CARD">KPI Metric Card</option>
          </Select>

          <Select label="Primary Metric" value={metric} onChange={(e) => setMetric(e.target.value)}>
            <option value="total_amount">Gross Revenue ($)</option>
            <option value="net_profit">Net Profit ($)</option>
            <option value="order_count">Total Orders (Qty)</option>
            <option value="aov">Average Order Value ($)</option>
          </Select>

          <Select label="Group By Dimension" value={dimension} onChange={(e) => setDimension(e.target.value)}>
            <option value="category">Product Category</option>
            <option value="state_region">State / Region</option>
            <option value="date_period">Time Period (Month)</option>
            <option value="status">Order Status</option>
          </Select>
        </div>

        <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/20 flex items-center gap-2 text-xs text-purple-600 dark:text-purple-400">
          <Sparkles className="w-4 h-4 shrink-0" />
          <span>AI will automatically apply appropriate zero-normalization, formatting, and explainability trails.</span>
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t border-border">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
            Add Widget to Dashboard
          </Button>
        </div>
      </form>
    </Modal>
  );
};
