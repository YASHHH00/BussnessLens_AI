import React from 'react';
import { Store, Utensils, Warehouse, Car, Stethoscope, ChevronDown } from 'lucide-react';
import { SemanticDomain as Domain, SemanticDomain } from '@/shared/types';
import { useAppStore } from '../../stores/useAppStore';
import { Badge } from '../ui/Badge';

export const DomainSelector: React.FC<{ className?: string }> = ({ className }) => {
  const activeDomain = useAppStore((s) => s.activeDomain);
  const setActiveDomain = useAppStore((s) => s.setActiveDomain);

  const domains: { id: SemanticDomain; label: string; icon: React.ReactNode; isAvailable: boolean; version: string }[] = [
    { id: 'RETAIL', label: 'Retail & E-Commerce', icon: <Store className="w-4 h-4 text-primary" />, isAvailable: true, version: 'Version 1 Production' },
    { id: 'FOOD_DELIVERY', label: 'Food Delivery & Logistics', icon: <Utensils className="w-4 h-4 text-amber-500" />, isAvailable: false, version: 'Future Plugin' },
    { id: 'WAREHOUSE', label: 'Warehouse & Inventory', icon: <Warehouse className="w-4 h-4 text-blue-500" />, isAvailable: false, version: 'Future Plugin' },
    { id: 'RIDE_SHARING', label: 'Ride Sharing & Fleet', icon: <Car className="w-4 h-4 text-purple-500" />, isAvailable: false, version: 'Future Plugin' },
    { id: 'HEALTHCARE', label: 'Healthcare & Clinical Analytics', icon: <Stethoscope className="w-4 h-4 text-emerald-500" />, isAvailable: false, version: 'Future Plugin' },
  ];

  return (
    <div className={`relative inline-block ${className || ''}`}>
      <div className="flex items-center gap-2">
        <label htmlFor="domain-select" className="text-xs font-semibold text-muted-foreground uppercase tracking-wider hidden sm:inline">
          Domain:
        </label>
        <div className="relative flex items-center">
          <select
            id="domain-select"
            value={activeDomain}
            onChange={(e) => setActiveDomain(e.target.value as SemanticDomain)}
            className="h-9 pl-9 pr-8 rounded-lg border border-border bg-card text-xs font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-ring appearance-none cursor-pointer hover:bg-muted/50 transition-colors shadow-sm"
          >
            {domains.map((dom) => (
              <option key={dom.id} value={dom.id} disabled={!dom.isAvailable}>
                {dom.label} ({dom.version})
              </option>
            ))}
          </select>
          <div className="absolute left-2.5 pointer-events-none flex items-center">
            {domains.find((d) => d.id === activeDomain)?.icon || <Store className="w-4 h-4 text-primary" />}
          </div>
          <div className="absolute right-2.5 pointer-events-none flex items-center text-muted-foreground">
            <ChevronDown className="w-4 h-4" />
          </div>
        </div>
        <Badge variant="success" size="sm" className="hidden md:inline-flex">
          Retail V1 Active
        </Badge>
      </div>
    </div>
  );
};
