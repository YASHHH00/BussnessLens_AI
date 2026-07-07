/**
 * Zustand App Store for UI state: Sidebar, global filters, domain selector, workflow tracker
 */
import { create } from 'zustand';
import { SemanticDomain, FilterState } from '@/shared/types';

export type WorkflowStep = 
  | 'CONNECT_DB'
  | 'SCHEMA_DETECT'
  | 'METADATA_EXTRACT'
  | 'MAPPING_REVIEW'
  | 'SEMANTIC_LAYER'
  | 'RECOMMENDED_DASHBOARDS'
  | 'DASHBOARD_GEN'
  | 'INSIGHTS'
  | 'FORECAST'
  | 'REPORTS';

export const WORKFLOW_STEPS_LIST: { id: WorkflowStep; label: string; path: string }[] = [
  { id: 'CONNECT_DB', label: '1. Connect Database', path: '/connect' },
  { id: 'SCHEMA_DETECT', label: '2. Schema Detection', path: '/schema-detection' },
  { id: 'METADATA_EXTRACT', label: '3. Metadata Extraction', path: '/schema-detection' },
  { id: 'MAPPING_REVIEW', label: '4. Mapping Review', path: '/mapping' },
  { id: 'SEMANTIC_LAYER', label: '5. Semantic Layer', path: '/semantic-explorer' },
  { id: 'RECOMMENDED_DASHBOARDS', label: '6. Recommendations', path: '/recommendations' },
  { id: 'DASHBOARD_GEN', label: '7. Dashboards', path: '/dashboards/executive' },
  { id: 'INSIGHTS', label: '8. AI Insights', path: '/ai-assistant' },
  { id: 'FORECAST', label: '9. Forecasting', path: '/dashboards/forecast' },
  { id: 'REPORTS', label: '10. Reports', path: '/reports' },
];

interface AppStoreState {
  isSidebarOpen: boolean;
  isSidebarCollapsed: boolean;
  activeDomain: SemanticDomain;
  selectedDomain: SemanticDomain;
  currentWorkflowStep: WorkflowStep;
  workflowStep: WorkflowStep;
  completedSteps: WorkflowStep[];
  globalFilters: FilterState;
  globalDateRange: { start: string; end: string };
  globalRegionFilter: string;
  activeConnectionId: string | null;

  // Actions
  toggleSidebar: (open?: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setActiveDomain: (domain: SemanticDomain) => void;
  setSelectedDomain: (domain: SemanticDomain) => void;
  setWorkflowStep: (step: WorkflowStep) => void;
  updateGlobalFilters: (filters: Partial<FilterState>) => void;
  setGlobalFilters: (filters: Partial<FilterState>) => void;
  resetGlobalFilters: () => void;
  setGlobalDateRange: (range: { start: string; end: string }) => void;
  setGlobalRegionFilter: (region: string) => void;
  setActiveConnectionId: (id: string | null) => void;
}

const defaultFilters: FilterState = {
  dateRange: {
    startDate: new Date(Date.now() - 1000 * 3600 * 24 * 30).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    preset: '30D',
  },
  region: 'ALL',
  category: 'ALL',
  product: 'ALL',
  customerSegment: 'ALL',
};

export const useAppStore = create<AppStoreState>((set) => ({
  isSidebarOpen: true,
  isSidebarCollapsed: false,
  activeDomain: 'RETAIL',
  selectedDomain: 'RETAIL',
  currentWorkflowStep: 'DASHBOARD_GEN',
  workflowStep: 'DASHBOARD_GEN',
  completedSteps: ['CONNECT_DB', 'SCHEMA_DETECT', 'MAPPING_REVIEW', 'SEMANTIC_LAYER'],
  globalFilters: { ...defaultFilters },
  globalDateRange: { start: '2026-06-01', end: '2026-07-06' },
  globalRegionFilter: 'ALL',
  activeConnectionId: 'conn_pg_01',

  toggleSidebar: (open) => set((state) => {
    const newVal = open !== undefined ? open : !state.isSidebarOpen;
    return { isSidebarOpen: newVal, isSidebarCollapsed: !newVal };
  }),
  setSidebarCollapsed: (collapsed) => set({ isSidebarCollapsed: collapsed, isSidebarOpen: !collapsed }),
  
  setActiveDomain: (domain) => set({ activeDomain: domain, selectedDomain: domain }),
  setSelectedDomain: (domain) => set({ activeDomain: domain, selectedDomain: domain }),
  
  setWorkflowStep: (step) => set((state) => ({
    currentWorkflowStep: step,
    workflowStep: step,
    completedSteps: state.completedSteps.includes(step) ? state.completedSteps : [...state.completedSteps, step]
  })),
  
  updateGlobalFilters: (newFilters) => set((state) => ({
    globalFilters: {
      ...state.globalFilters,
      ...newFilters,
      dateRange: newFilters.dateRange || state.globalFilters.dateRange,
    },
  })),
  setGlobalFilters: (newFilters) => set((state) => ({
    globalFilters: {
      ...state.globalFilters,
      ...newFilters,
      dateRange: newFilters.dateRange || state.globalFilters.dateRange,
    },
  })),
  
  resetGlobalFilters: () => set({ globalFilters: { ...defaultFilters } }),
  setGlobalDateRange: (range) => set({ globalDateRange: range }),
  setGlobalRegionFilter: (region) => set({ globalRegionFilter: region }),
  setActiveConnectionId: (id) => set({ activeConnectionId: id }),
}));
