/**
 * Comprehensive Mock Backend Adapter simulating all Backend V3 Services
 */
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
import * as Types from '../types';

// Mock datasets and state
let currentUser: Types.User = {
  id: 'usr_001',
  email: 'admin@businesslens.ai',
  name: 'Alex Rivera (Executive)',
  role: 'EXECUTIVE',
  avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  department: 'Executive Leadership',
  createdAt: '2025-01-15T08:00:00Z',
  lastLoginAt: new Date().toISOString(),
};

const mockConnections: Types.DatabaseConnection[] = [
  {
    id: 'conn_pg_01',
    name: 'Production E-Commerce Analytics (PostgreSQL)',
    type: 'POSTGRESQL',
    host: 'pg-prod.businesslens.ai',
    port: 5432,
    databaseName: 'retail_analytics_db',
    username: 'bl_analytics_read',
    status: 'CONNECTED',
    lastConnectedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    isProductionReady: true,
    schemaVersion: 'v3.2.0',
    tableCount: 14,
  },
  {
    id: 'conn_mysql_01',
    name: 'Legacy CRM Database (MySQL - Coming Soon)',
    type: 'MYSQL',
    host: 'mysql-crm.internal',
    port: 3306,
    databaseName: 'crm_main',
    username: 'crm_ro',
    status: 'DISCONNECTED',
    isProductionReady: false,
    schemaVersion: 'v1.0.0',
    tableCount: 8,
  },
];

const mockSemanticFields: Types.SemanticField[] = [
  {
    id: 'sem_01',
    businessField: 'Total Revenue',
    displayName: 'Gross Revenue ($)',
    mappedTable: 'orders',
    mappedColumn: 'total_amount',
    aggregation: 'SUM',
    formula: 'SUM(orders.total_amount)',
    dataType: 'NUMERIC',
    isForecastable: true,
    description: 'Total financial value of all completed customer orders before returns.',
    currentStatus: 'MAPPED',
    sampleValues: [149.99, 299.50, 1250.00, 45.00, 89.90],
    confidence: 98,
  },
  {
    id: 'sem_02',
    businessField: 'Net Profit Margin',
    displayName: 'Profit Margin (%)',
    mappedTable: 'orders',
    mappedColumn: 'net_profit',
    aggregation: 'AVG',
    formula: '(SUM(net_profit) / SUM(total_amount)) * 100',
    dataType: 'NUMERIC',
    isForecastable: true,
    description: 'Percentage of revenue retained as profit after deducting COGS and discounts.',
    currentStatus: 'MAPPED',
    sampleValues: [24.5, 31.2, 18.0, 22.8, 28.4],
    confidence: 95,
  },
  {
    id: 'sem_03',
    businessField: 'Customer Acquisition Cost (CAC)',
    displayName: 'CAC ($)',
    mappedTable: 'marketing_spend',
    mappedColumn: 'acquisition_cost',
    aggregation: 'AVG',
    formula: 'SUM(marketing_spend.cost) / COUNT(DISTINCT customers.id)',
    dataType: 'NUMERIC',
    isForecastable: false,
    description: 'Average cost incurred to acquire a single new paying customer.',
    currentStatus: 'UNDER_REVIEW',
    sampleValues: [34.50, 42.10, 38.90, 45.00],
    confidence: 82,
  },
  {
    id: 'sem_04',
    businessField: 'Order Date',
    displayName: 'Transaction Date',
    mappedTable: 'orders',
    mappedColumn: 'created_at',
    aggregation: 'NONE',
    dataType: 'DATE',
    isForecastable: true,
    description: 'Timestamp when the customer checkout was finalized.',
    currentStatus: 'MAPPED',
    sampleValues: ['2026-07-01', '2026-07-02', '2026-07-03'],
    confidence: 99,
  },
  {
    id: 'sem_05',
    businessField: 'Customer Region',
    displayName: 'Geographic Region',
    mappedTable: 'customers',
    mappedColumn: 'state_region',
    aggregation: 'NONE',
    dataType: 'STRING',
    isForecastable: false,
    description: 'Primary shipping region of the customer account.',
    currentStatus: 'MAPPED',
    sampleValues: ['North America', 'Europe', 'Asia-Pacific', 'Latin America'],
    confidence: 92,
  },
];

const mockDataQualityReport: Types.DataQualityReport = {
  connectionId: 'conn_pg_01',
  overallScore: 94,
  scannedAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
  missingValuesCount: 142,
  duplicateRowsCount: 0,
  nullPercentage: 0.8,
  invalidDatesCount: 3,
  outliersCount: 18,
  relationshipIssuesCount: 0,
  orphanRecordsCount: 0,
  columnCompleteness: [
    { columnName: 'total_amount', tableName: 'orders', totalRows: 15420, nullCount: 0, nullPercentage: 0, status: 'PASS' },
    { columnName: 'customer_phone', tableName: 'customers', totalRows: 4200, nullCount: 132, nullPercentage: 3.1, status: 'WARNING' },
    { columnName: 'discount_code', tableName: 'orders', totalRows: 15420, nullCount: 8900, nullPercentage: 57.7, status: 'INFO' },
    { columnName: 'delivery_date', tableName: 'shipments', totalRows: 15420, nullCount: 10, nullPercentage: 0.06, status: 'PASS' },
  ],
  consistencyChecks: [
    { id: 'chk_1', name: 'Revenue positive validation', description: 'All completed orders must have total_amount > 0', status: 'PASS', affectedRows: 0, recommendation: 'No action needed.' },
    { id: 'chk_2', name: 'Order to Customer FK Integrity', description: 'All orders.customer_id must exist in customers table', status: 'PASS', affectedRows: 0, recommendation: 'Foreign keys are 100% consistent.' },
    { id: 'chk_3', name: 'Timestamp timezone formatting', description: 'Check for UTC ISO compliance on created_at dates', status: 'WARNING', affectedRows: 3, recommendation: 'Standardize 3 legacy timestamps in orders table to UTC.' },
  ],
  topRecommendations: [
    'Enforce NOT NULL constraint on customers.email and orders.total_amount.',
    'Standardize 3 legacy date records in orders table to ISO-8601 UTC format.',
    'Review 18 statistical price outliers (> 3 std dev from mean) in electronics category.',
  ],
};

const mockBusinessRules: Types.BusinessRuleAlert[] = [
  {
    id: 'rule_01',
    alertType: 'REVENUE_DROP',
    title: 'Anomalous Weekend Revenue Dip Detected',
    severity: 'CRITICAL',
    explanation: 'Revenue in the European region dropped by 24.5% compared to the 8-week moving average. Caused by payment gateway timeout errors on checkout.',
    triggerTimestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    metricAffected: 'Regional Revenue',
    currentValue: '$42,150',
    thresholdValue: '$55,000 (Min Expected)',
    isResolved: false,
  },
  {
    id: 'rule_02',
    alertType: 'LOW_INVENTORY',
    title: 'Stockout Risk: Wireless Noise-Canceling Headphones',
    severity: 'WARNING',
    explanation: 'Current inventory level (42 units) will be exhausted within 4.5 days based on current daily sales velocity (9.3 units/day).',
    triggerTimestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    metricAffected: 'Inventory Turnover',
    currentValue: '42 Units',
    thresholdValue: '100 Units (Reorder Point)',
    isResolved: false,
  },
  {
    id: 'rule_03',
    alertType: 'SALES_SPIKE',
    title: 'Viral Promotion Surge: Smart Home Hub V2',
    severity: 'INFO',
    explanation: 'Order volume spiked by 310% in the last 6 hours following tech influencer feature. Ensure fulfillment center staffing matches demand.',
    triggerTimestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    metricAffected: 'Hourly Orders',
    currentValue: '480 Orders/hr',
    thresholdValue: '150 Orders/hr (Baseline)',
    isResolved: true,
  },
  {
    id: 'rule_04',
    alertType: 'ABNORMAL_DISCOUNTS',
    title: 'High Discount Rate on Enterprise B2B Contracts',
    severity: 'WARNING',
    explanation: 'Average discount applied by sales reps reached 34.2% this week, exceeding the approved standard policy ceiling of 25%.',
    triggerTimestamp: new Date(Date.now() - 1000 * 60 * 300).toISOString(),
    metricAffected: 'Average Discount %',
    currentValue: '34.2%',
    thresholdValue: '25.0% (Policy Ceiling)',
    isResolved: false,
  },
];

const mockAuditLogs: Types.SystemAuditLog[] = [
  { id: 'log_01', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), userId: 'usr_001', userName: 'Alex Rivera', userRole: 'EXECUTIVE', action: 'DASHBOARD_GEN', severity: 'INFO', description: 'Generated Executive Summary Dashboard v3.2', ipAddress: '192.168.1.42' },
  { id: 'log_02', timestamp: new Date(Date.now() - 1000 * 60 * 25).toISOString(), userId: 'usr_002', userName: 'Sarah Jenkins', userRole: 'DATA_ANALYST', action: 'SCHEMA_SCAN', severity: 'INFO', description: 'Completed metadata scan on Production E-Commerce Analytics (PostgreSQL)', ipAddress: '10.0.4.15' },
  { id: 'log_03', timestamp: new Date(Date.now() - 1000 * 60 * 110).toISOString(), userId: 'usr_003', userName: 'Marcus Vance', userRole: 'ADMIN', action: 'MAPPING_CHANGE', severity: 'WARNING', description: 'Confirmed schema mapping modification: revenue -> total_amount', ipAddress: '172.16.0.88' },
  { id: 'log_04', timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(), userId: 'usr_002', userName: 'Sarah Jenkins', userRole: 'DATA_ANALYST', action: 'AI_QUERY', severity: 'INFO', description: 'Executed AI Assistant NLQ: "Why did profit margin drop in Q2?"', ipAddress: '10.0.4.15' },
  { id: 'log_05', timestamp: new Date(Date.now() - 1000 * 60 * 360).toISOString(), userId: 'usr_003', userName: 'Marcus Vance', userRole: 'ADMIN', action: 'LOGIN', severity: 'INFO', description: 'Successful MFA login via Okta SSO', ipAddress: '172.16.0.88' },
];

/**
 * Enable Mock Adapter by intercepting Axios request adapter
 */
export function setupMockAdapter() {
  const originalAdapter = apiClient.defaults.adapter;

  apiClient.defaults.adapter = async (config: AxiosRequestConfig) => {
    // If VITE_USE_MOCKS is explicitly false, pass through to real network
    if (import.meta.env.VITE_USE_MOCKS === 'false' && originalAdapter) {
      return (originalAdapter as unknown as (config: AxiosRequestConfig) => Promise<AxiosResponse>)(config);
    }

    // Simulate network latency (200ms - 600ms)
    await new Promise((resolve) => setTimeout(resolve, 250 + Math.random() * 300));

    const url = config.url || '';
    const method = (config.method || 'get').toLowerCase();

    // 1. Auth routes
    if (url.includes('/auth/login') && method === 'post') {
      return mockResponse(config, 200, {
        user: currentUser,
        tokens: { accessToken: 'mock_jwt_access_token_v3', refreshToken: 'mock_jwt_refresh_token_v3', expiresIn: 900 },
      });
    }
    if (url.includes('/auth/refresh-token') && method === 'post') {
      return mockResponse(config, 200, {
        accessToken: 'mock_jwt_access_token_refreshed_' + Date.now(),
        refreshToken: 'mock_jwt_refresh_token_refreshed_' + Date.now(),
      });
    }

    // 2. Connections routes
    if (url.includes('/connections/test') && method === 'post') {
      const body = JSON.parse(config.data || '{}');
      if (body.port === 5432 || body.type === 'POSTGRESQL') {
        return mockResponse(config, 200, { success: true, message: 'Successfully connected to PostgreSQL v16.2 database.' });
      }
      return mockResponse(config, 400, { success: false, message: 'Connection timeout: Unable to reach database host on specified port.' });
    }
    if (url.includes('/connections') && method === 'get') {
      return mockResponse(config, 200, mockConnections);
    }

    // 3. Schema detection & Semantic Layer
    if (url.includes('/semantic/fields') && method === 'get') {
      return mockResponse(config, 200, mockSemanticFields);
    }
    if (url.includes('/semantic/domains') && method === 'get') {
      return mockResponse(config, 200, ['RETAIL', 'FOOD_DELIVERY', 'WAREHOUSE', 'RIDE_SHARING', 'HEALTHCARE']);
    }

    // 4. Data Quality & Business Rules
    if (url.includes('/quality/report') && method === 'get') {
      return mockResponse(config, 200, mockDataQualityReport);
    }
    if (url.includes('/rules/alerts') && method === 'get') {
      return mockResponse(config, 200, mockBusinessRules);
    }

    // 5. Universal Explainability
    if (url.includes('/explainability') && method === 'get') {
      const targetType = url.split('/').slice(-2)[0]?.toUpperCase() as Types.ExplainTargetType || 'KPI';
      const explanation: Types.ExplainabilityPayload = {
        targetId: 'exp_01',
        targetType,
        title: `Explainability Analysis: ${targetType}`,
        sourceTables: ['orders', 'customers', 'products'],
        sourceColumns: ['orders.total_amount', 'orders.created_at', 'customers.state_region'],
        formula: 'SUM(orders.total_amount) WHERE orders.status = "COMPLETED"',
        aggregation: 'SUM',
        appliedFilters: { dateRange: 'Last 30 Days', region: 'All Regions' },
        generatedSql: `SELECT customers.state_region AS region, SUM(orders.total_amount) AS total_revenue\nFROM orders\nJOIN customers ON orders.customer_id = customers.id\nWHERE orders.created_at >= NOW() - INTERVAL '30 days'\n  AND orders.status = 'COMPLETED'\nGROUP BY customers.state_region\nORDER BY total_revenue DESC;`,
        businessRulesUsed: ['Rule #1: Revenue positive validation', 'Rule #4: Exclude refunded transactions'],
        semanticLayerInfo: {
          businessField: 'Total Revenue',
          mappedColumn: 'orders.total_amount',
          description: 'Gross completed order revenue aggregated across selected time period.',
        },
        aiSummary: 'This metric was generated by aggregating validated order transactions from the PostgreSQL production database, applying standard GAAP accounting exclusion rules for refunds.',
        confidence: 99.4,
        aiCostSource: 'SEMANTIC_LAYER',
      };
      return mockResponse(config, 200, explanation);
    }

    // 6. SQL Playground (Data Analyst / Admin)
    if (url.includes('/sql/execute') && method === 'post') {
      const body = JSON.parse(config.data || '{}');
      const query = (body.query || '').toLowerCase();
      if (query.includes('drop') || query.includes('delete') || query.includes('update') || query.includes('insert')) {
        return mockResponse(config, 403, { code: 'READ_ONLY_VIOLATION', message: 'Security Error: Only SELECT read-only queries are permitted in the SQL Playground.' });
      }
      return mockResponse(config, 200, {
        columns: ['region', 'total_orders', 'total_revenue', 'avg_order_value'],
        rows: [
          { region: 'North America', total_orders: 8420, total_revenue: 1245000, avg_order_value: 147.86 },
          { region: 'Europe', total_orders: 4310, total_revenue: 689000, avg_order_value: 159.86 },
          { region: 'Asia-Pacific', total_orders: 2190, total_revenue: 312000, avg_order_value: 142.46 },
          { region: 'Latin America', total_orders: 500, total_revenue: 64000, avg_order_value: 128.00 },
        ],
        executionTimeMs: 142,
        rowCount: 4,
      });
    }

    // 7. Audit Logs
    if (url.includes('/audit-logs') && method === 'get') {
      return mockResponse(config, 200, mockAuditLogs);
    }

    // Default fallback mock
    return mockResponse(config, 200, { success: true, message: 'Mock response from BusinessLens AI Backend V3 Adapter.' });
  };
}

function mockResponse(config: AxiosRequestConfig, status: number, data: unknown): AxiosResponse {
  return {
    data: { success: status >= 200 && status < 300, data, timestamp: new Date().toISOString() },
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: { 'content-type': 'application/json' },
    config: config as AxiosResponse['config'],
  };
}
