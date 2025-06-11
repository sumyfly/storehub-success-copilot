import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  People,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { apiService, DashboardStats, Customer, Alert as AlertType } from '../services/api';

// Stat Card Component
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactElement;
  color: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4">
            {value}
          </Typography>
        </Box>
        <Box color={`${color}.main`}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

// Recent Alerts Component
const RecentAlerts: React.FC<{ alerts: AlertType[] }> = ({ alerts }) => (
  <Paper sx={{ p: 2 }}>
    <Typography variant="h6" gutterBottom>
      Recent Critical Alerts
    </Typography>
    {alerts.slice(0, 5).map((alert, index) => (
      <Alert 
        key={index} 
        severity={alert.severity === 'critical' ? 'error' : alert.severity === 'medium' ? 'warning' : 'info'}
        sx={{ mb: 1 }}
      >
        <Typography variant="body2">
          <strong>{alert.customer_name}</strong>: {alert.message}
        </Typography>
      </Alert>
    ))}
  </Paper>
);

// At-Risk Customers Component
const AtRiskCustomers: React.FC<{ customers: Customer[] }> = ({ customers }) => {
  const criticalCustomers = customers
    .filter(c => c.health_score < 0.3)
    .sort((a, b) => a.health_score - b.health_score)
    .slice(0, 5);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Customers at High Risk
      </Typography>
      {criticalCustomers.map((customer) => (
        <Box key={customer.id} sx={{ mb: 2, p: 1, border: '1px solid #f0f0f0', borderRadius: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            {customer.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Health Score: {(customer.health_score * 100).toFixed(0)}% • 
            MRR: ${customer.mrr.toLocaleString()} • 
            Last Login: {customer.last_login_days} days ago
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Box
              sx={{
                width: '100%',
                height: 8,
                backgroundColor: '#f0f0f0',
                borderRadius: 4,
                overflow: 'hidden',
              }}
            >
              <Box
                sx={{
                  width: `${customer.health_score * 100}%`,
                  height: '100%',
                  backgroundColor: customer.health_score < 0.3 ? '#f44336' : 
                                   customer.health_score < 0.6 ? '#ff9800' : '#4caf50',
                }}
              />
            </Box>
          </Box>
        </Box>
      ))}
    </Paper>
  );
};

export default function Dashboard() {
  // Fetch data
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>(
    'dashboardStats',
    apiService.getDashboardStats,
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: customers, isLoading: customersLoading } = useQuery<Customer[]>(
    'customers',
    apiService.getCustomers,
    { refetchInterval: 60000 } // Refresh every minute
  );

  const { data: alerts, isLoading: alertsLoading } = useQuery<AlertType[]>(
    'alerts',
    apiService.getAlerts,
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  if (statsLoading || customersLoading || alertsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customer Success Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Customers"
            value={stats?.total_customers || 0}
            icon={<People fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Alerts"
            value={stats?.critical_alerts || 0}
            icon={<Warning fontSize="large" />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Medium Risk"
            value={stats?.medium_risk_customers || 0}
            icon={<TrendingDown fontSize="large" />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Healthy Customers"
            value={stats?.healthy_customers || 0}
            icon={<TrendingUp fontSize="large" />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Content Grid */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          {alerts && <RecentAlerts alerts={alerts} />}
        </Grid>
        <Grid item xs={12} md={6}>
          {customers && <AtRiskCustomers customers={customers} />}
        </Grid>
      </Grid>
    </Box>
  );
} 