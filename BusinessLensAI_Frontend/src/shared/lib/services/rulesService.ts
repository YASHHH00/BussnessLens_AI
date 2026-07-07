import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const rulesService = {
  async getBusinessRuleAlerts(): Promise<Types.BusinessRuleAlert[]> {
    const response = await apiClient.get('/rules/alerts');
    return response.data.data;
  },

  async resolveAlert(alertId: string): Promise<Types.BusinessRuleAlert> {
    const response = await apiClient.post(`/rules/alerts/${alertId}/resolve`);
    return response.data.data;
  },

  async getRules(connectionId?: string): Promise<Types.BusinessRule[]> {
    const response = await apiClient.get('/rules', { params: { connectionId } });
    return response.data.data || [];
  },

  async createRule(rule: Types.BusinessRule): Promise<Types.BusinessRule> {
    const response = await apiClient.post('/rules', rule);
    return response.data.data || rule;
  },
};
