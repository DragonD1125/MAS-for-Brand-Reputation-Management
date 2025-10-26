import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 12000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface BrandAnalysisPayload {
  brand_name: string;
  max_articles?: number;
  days_back?: number;
}

export interface BrandArticle {
  title: string;
  source?: string;
  url?: string;
  published_at?: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  sentiment_score: number;
  excerpt?: string;
  keywords: string[];
}

export interface BrandAnalysisSummary {
  total_articles: number;
  positive: number;
  neutral: number;
  negative: number;
  average_sentiment_score: number;
  top_keywords: string[];
  insights: string[];
  recommendations: string[];
}

export interface BrandAnalysisResponse {
  brand_name: string;
  timeframe_days: number;
  fetched_at: string;
  articles: BrandArticle[];
  summary: BrandAnalysisSummary;
}

export interface RiskAssessment {
  crisis_score: number;
  crisis_level: 'low' | 'moderate' | 'severe';
  negative_sentiment_ratio: number;
  crisis_indicators_found: number;
  requires_immediate_attention: boolean;
}

export interface FullOrchestrationResponse {
  success: boolean;
  brand_name: string;
  workflow_id: string;
  started_at: string;
  completed_at: string;
  execution_time_seconds: number;
  steps_completed: string[];
  failed_steps: string[];
  articles: BrandArticle[];
  summary: BrandAnalysisSummary;
  agent_results: Record<string, any>;
  quality_scores: Record<string, number>;
  risk_assessments: RiskAssessment;
  performance_metrics: Record<string, any>;
  recommendations: string[];
  next_actions: string[];
  langgraph_execution: boolean;
}

export const analyticsApi = {
  getStatus: () => api.get('/analytics/'),
  runBrandAnalysis: (payload: BrandAnalysisPayload) =>
    api.post<BrandAnalysisResponse>('/analytics/brand-analysis', payload),
  runOrchestration: (payload: BrandAnalysisPayload) =>
    api.post<FullOrchestrationResponse>('/analytics/brand-analysis-orchestrated', payload),
};

export default api;
