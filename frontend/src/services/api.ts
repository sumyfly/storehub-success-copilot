import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Customer {
  id: number;
  name: string;
  mrr: number;
  usage_score: number;
  support_tickets: number;
  last_login_days: number;
  contract_date: string;
  health_score: number;
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

export interface DashboardStats {
  total_customers: number;
  critical_alerts: number;
  medium_risk_customers: number;
  healthy_customers: number;
  total_alerts: number;
}

export interface CustomerHealth {
  customer_id: number;
  customer_name: string;
  overall_health_score: number;
  factors: {
    usage_score: number;
    support_tickets: number;
    last_login_days: number;
    mrr: number;
  };
  risk_level: 'critical' | 'medium' | 'healthy';
  alerts: Alert[];
}

// API functions
export const apiService = {
  // Get all customers
  getCustomers: async (): Promise<Customer[]> => {
    const response = await api.get('/customers');
    return response.data;
  },

  // Get all alerts
  getAlerts: async (): Promise<Alert[]> => {
    const response = await api.get('/alerts');
    return response.data;
  },

  // Get dashboard stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  // Get customer health details
  getCustomerHealth: async (customerId: number): Promise<CustomerHealth> => {
    const response = await api.get(`/health/${customerId}`);
    return response.data;
  },
}; 