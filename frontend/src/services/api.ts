import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

// Enhanced type definitions
export interface Customer {
  id: number;
  name: string;
  mrr: number;
  usage_score: number;
  support_tickets: number;
  last_login_days: number;
  contract_date: string;
  health_score: number;
  customer_type?: string;
  payment_status?: string;
  engagement_score?: number;
  onboarding_completed?: boolean;
  nps_score?: number;
  customer_label?: string;
}

export interface Alert {
  customer_id: number;
  customer_name: string;
  type: string;
  severity: 'critical' | 'medium' | 'low';
  message: string;
  actions: string[];
  created_at: string;
}

export interface HealthTrend {
  trend: 'improving' | 'declining' | 'stable';
  change_30d: number;
  forecast_30d: number;
  confidence: number;
}

export interface CustomerHealth {
  customer_id: number;
  customer_name: string;
  overall_health_score: number;
  customer_label: string;
  factors: {
    usage_score: number;
    engagement_score: number;
    support_tickets: number;
    last_login_days: number;
    payment_status: string;
    feature_adoption: {
      core: number;
      advanced: number;
      integrations: number;
    };
    nps_score: number;
    mrr: number;
  };
  risk_level: 'critical' | 'medium' | 'healthy';
  health_trend: HealthTrend;
  alerts: Alert[];
  recommended_actions: ActionRecommendation[];
}

export interface ActionRecommendation {
  action_type: string;
  description: string;
  urgency: 'immediate' | 'within_24h' | 'within_week';
  effort: 'low' | 'medium' | 'high';
  expected_impact: 'low' | 'medium' | 'high';
  priority: number;
}

export interface DashboardStats {
  total_customers: number;
  critical_alerts: number;
  medium_risk_customers: number;
  healthy_customers: number;
  total_alerts: number;
  average_health_score: number;
  customer_segments: { [key: string]: number };
  expansion_opportunities: number;
  payment_issues: number;
}

export interface CustomerTrend {
  customer_id: number;
  customer_name: string;
  current_health: number;
  trend: HealthTrend;
}

// Enhanced API functions
export const apiService = {
  // Get all customers with enhanced data
  getCustomers: async (): Promise<Customer[]> => {
    const response = await api.get('/customers');
    return response.data;
  },

  // Get all alerts
  getAlerts: async (): Promise<Alert[]> => {
    const response = await api.get('/alerts');
    return response.data;
  },

  // Get detailed customer health info
  getCustomerHealth: async (customerId: number): Promise<CustomerHealth> => {
    const response = await api.get(`/health/${customerId}`);
    return response.data;
  },

  // Get dashboard stats with new metrics
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  // Get health trends for all customers
  getHealthTrends: async (): Promise<CustomerTrend[]> => {
    const response = await api.get('/insights/trends');
    return response.data;
  },

  // Get action recommendations for a customer
  getCustomerRecommendations: async (customerId: number) => {
    const response = await api.get(`/recommendations/${customerId}`);
    return response.data;
  },
};

// Utility functions for UI
export const getHealthColor = (score: number): string => {
  if (score >= 0.8) return '#4caf50'; // Green
  if (score >= 0.6) return '#ff9800'; // Orange
  if (score >= 0.3) return '#f44336'; // Red
  return '#d32f2f'; // Dark Red
};

export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical': return '#f44336';
    case 'medium': return '#ff9800';
    case 'low': return '#4caf50';
    default: return '#757575';
  }
};

export const getTrendIcon = (trend: 'improving' | 'declining' | 'stable'): string => {
  switch (trend) {
    case 'improving': return '📈';
    case 'declining': return '📉';
    case 'stable': return '➡️';
    default: return '➡️';
  }
};

export const formatPercentage = (value: number): string => {
  return `${Math.round(value * 100)}%`;
};

export const getUrgencyColor = (urgency: string): string => {
  switch (urgency) {
    case 'immediate': return '#f44336';
    case 'within_24h': return '#ff9800';
    case 'within_week': return '#2196f3';
    default: return '#757575';
  }
}; 