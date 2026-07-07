import React, { useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import { EChartsOption } from 'echarts';
import { Download, FileSpreadsheet, Sparkles } from 'lucide-react';
import { useThemeStore } from '../../stores/useThemeStore';
import { Button } from '../ui/Button';
import { toast } from '../ui/Toast';

export interface ChartWrapperProps {
  title?: string;
  subtitle?: string;
  options: EChartsOption;
  height?: string | number;
  onExplain?: () => void;
  exportTitle?: string;
  className?: string;
}

export const ChartWrapper: React.FC<ChartWrapperProps> = ({
  title,
  subtitle,
  options,
  height = 320,
  onExplain,
  exportTitle = 'chart_export',
  className,
}) => {
  const chartRef = useRef<ReactECharts>(null);
  const theme = useThemeStore((s) => s.theme);

  // Determine current active ECharts theme
  const isDark =
    theme === 'dark' ||
    (theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  const handleExportPNG = () => {
    const instance = chartRef.current?.getEchartsInstance();
    if (!instance) return;
    const imgUrl = instance.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: isDark ? '#090d16' : '#ffffff' });
    const link = document.createElement('a');
    link.href = imgUrl;
    link.download = `${exportTitle}.png`;
    link.click();
    toast.success('Chart Exported', 'PNG image downloaded successfully.');
  };

  const handleExportCSV = () => {
    const series = (options.series || []) as { name?: string; data?: unknown[] }[];
    const xAxis = (options.xAxis as { data?: unknown[] }) || {};
    const xData = xAxis.data || [];

    if (!series.length || !xData.length) {
      toast.warning('Export Unavailable', 'This chart layout does not support standard tabular CSV export.');
      return;
    }

    let csvContent = 'data:text/csv;charset=utf-8,';
    const headers = ['Category', ...series.map((s) => s.name || 'Value')];
    csvContent += headers.join(',') + '\r\n';

    xData.forEach((xVal, idx) => {
      const row = [String(xVal)];
      series.forEach((s) => {
        const val = Array.isArray(s.data) ? s.data[idx] : '';
        row.push(val !== undefined && val !== null ? String(val) : '0');
      });
      csvContent += row.join(',') + '\r\n';
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.href = encodedUri;
    link.download = `${exportTitle}.csv`;
    link.click();
    toast.success('CSV Exported', 'Tabular chart dataset downloaded successfully.');
  };

  return (
    <div className={`flex flex-col w-full rounded-xl border border-border bg-card p-5 shadow-sm transition-all duration-200 ${className || ''}`}>
      {(title || subtitle || onExplain) && (
        <div className="flex items-start justify-between pb-4 mb-2 border-b border-border gap-4">
          <div>
            {title && <h3 className="text-base font-semibold text-foreground tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            {onExplain && (
              <Button
                variant="outline"
                size="sm"
                onClick={onExplain}
                className="h-8 px-2.5 text-xs text-purple-600 dark:text-purple-400 border-purple-500/20 hover:bg-purple-500/10 gap-1"
                title="View AI Explainability & Lineage"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Explain</span>
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExportPNG}
              className="h-8 px-2 text-muted-foreground hover:text-foreground"
              title="Download PNG Image"
            >
              <Download className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExportCSV}
              className="h-8 px-2 text-muted-foreground hover:text-foreground"
              title="Export CSV Data"
            >
              <FileSpreadsheet className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      <div className="w-full relative min-h-[200px]">
        <ReactECharts
          ref={chartRef}
          option={{
            ...options,
            backgroundColor: 'transparent',
            textStyle: { fontFamily: 'Inter, system-ui, sans-serif' },
            tooltip: {
              trigger: 'axis',
              backgroundColor: isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.95)',
              borderColor: isDark ? '#334155' : '#e2e8f0',
              textStyle: { color: isDark ? '#f8fafc' : '#0f172a', fontSize: 12 },
              ...(options.tooltip as object),
            },
          }}
          theme={isDark ? 'dark' : undefined}
          style={{ height: typeof height === 'number' ? `${height}px` : height, width: '100%' }}
          notMerge={true}
          lazyUpdate={true}
        />
      </div>
    </div>
  );
};
