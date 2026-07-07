import React, { useState } from 'react';
import { RefreshCw, Database, Clock, CheckCircle2 } from 'lucide-react';
import { RedisCacheStatus as CacheStatus, RedisCacheStatus } from '@/shared/types';
import { Badge } from './Badge';
import { Button } from './Button';
import { formatTimeAgo, formatDateTime } from '../../lib/formatters';
import { toast } from './Toast';

export interface CacheStatusBadgeProps {
  status: RedisCacheStatus;
  onRefresh?: () => Promise<void> | void;
  className?: string;
}

export const CacheStatusBadge: React.FC<CacheStatusBadgeProps> = ({ status, onRefresh, className }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (!onRefresh) return;
    setIsRefreshing(true);
    try {
      await onRefresh();
      toast.success('Redis Cache Updated', 'Dashboard data has been refreshed from live database sources.');
    } catch {
      toast.error('Cache Refresh Failed', 'Unable to refresh live data. Serving cached version.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const isLive = status.statusText === 'LIVE' || !status.isCached;

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-card/60 backdrop-blur-sm text-xs ${className || ''}`}>
      <div className="flex items-center gap-1.5">
        <Database className={`w-3.5 h-3.5 ${isLive ? 'text-emerald-500 animate-pulse' : 'text-blue-500'}`} />
        <span className="font-semibold text-foreground">Data Source:</span>
        <Badge variant={isLive ? 'success' : 'info'} size="sm">
          {status.statusText || (isLive ? 'LIVE' : 'CACHED')}
        </Badge>
      </div>

      <div className="h-3 w-px bg-border mx-0.5" />

      <div className="flex items-center gap-1 text-muted-foreground" title={`Cached at: ${formatDateTime(status.cachedAt)}`}>
        <Clock className="w-3 h-3" />
        <span>Updated {formatTimeAgo(status.lastUpdated)}</span>
      </div>

      {onRefresh && (
        <>
          <div className="h-3 w-px bg-border mx-0.5" />
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            isLoading={isRefreshing}
            className="h-6 px-2 text-[11px] gap-1 text-primary hover:text-primary hover:bg-primary/10"
          >
            <RefreshCw className="w-3 h-3" />
            Refresh Cache
          </Button>
        </>
      )}
    </div>
  );
};
