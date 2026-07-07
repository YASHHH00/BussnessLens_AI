import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const aiService = {
  async sendChatMessage(message: string, history: Types.ChatMessage[] = []): Promise<Types.ChatMessage> {
    const response = await apiClient.post('/ai/chat', { message, history });
    return response.data.data;
  },

  async getSuggestedPrompts(): Promise<Types.SuggestedPrompt[]> {
    const response = await apiClient.get('/ai/prompts');
    return response.data.data || [
      { id: 'p1', text: 'Why did profit drop in Europe last month?', category: 'FINANCIAL' },
      { id: 'p2', text: 'Which products are at risk of stocking out within 7 days?', category: 'OPERATIONAL' },
      { id: 'p3', text: 'Forecast total gross revenue for the next 90 days with confidence intervals.', category: 'FORECASTING' },
      { id: 'p4', text: 'Analyze customer acquisition cost (CAC) vs Lifetime Value (LTV).', category: 'FINANCIAL' },
    ];
  },
};
