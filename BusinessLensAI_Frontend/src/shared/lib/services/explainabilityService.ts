import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const explainabilityService = {
  async getExplanation(targetType: Types.ExplainTargetType, targetId: string): Promise<Types.ExplainabilityPayload> {
    const response = await apiClient.get(`/explainability/${targetType.toLowerCase()}/${targetId}`);
    return response.data.data;
  },
};
