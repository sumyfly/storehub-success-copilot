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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  People,
  Assessment,
  AttachMoney,
  NotificationImportant,
  CheckCircle,
  Lightbulb,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { apiService, DashboardStats, Customer, Alert as AlertType } from '../services/api';
import { getHealthColor, getSeverityColor, getTrendIcon } from '../services/api';

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

const Dashboard: React.FC = () => {
  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboardStats',
    apiService.getDashboardStats
  );

  const { data: alerts, isLoading: alertsLoading } = useQuery(
    'alerts',
    apiService.getAlerts
  );

  const { data: customers } = useQuery(
    'customers',
    apiService.getCustomers
  );

  const { data: trends } = useQuery(
    'trends',
    apiService.getHealthTrends
  );

  if (statsLoading || alertsLoading) {
    return <Box>Loading...</Box>;
  }

  const recentAlerts = alerts?.slice(0, 6) || [];
  const atRiskCustomers = customers?.filter(c => c.health_score < 0.6) || [];
  const topTrends = trends?.slice(0, 5) || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customer Success Dashboard
      </Typography>
      
      {/* Enhanced Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <People fontSize="large" color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Customers
                  </Typography>
                  <Typography variant="h4">{stats?.total_customers}</Typography>
                  <Typography variant="body2" color="success.main">
                    Avg Health: {stats?.average_health_score}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <NotificationImportant fontSize="large" color="error" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Critical Alerts
                  </Typography>
                  <Typography variant="h4">{stats?.critical_alerts}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stats?.total_alerts} total alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp fontSize="large" color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Expansion Ready
                  </Typography>
                  <Typography variant="h4">{stats?.expansion_opportunities}</Typography>
                  <Typography variant="body2" color="success.main">
                    High-health customers
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AttachMoney fontSize="large" color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Payment Issues
                  </Typography>
                  <Typography variant="h4">{stats?.payment_issues}</Typography>
                  <Typography variant="body2" color="warning.main">
                    Need attention
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Customer Segmentation */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Assessment fontSize="large" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Customer Segments
              </Typography>
              <Box>
                {stats?.customer_segments && Object.entries(stats.customer_segments).map(([label, count]) => (
                  <Box key={label} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body1">{label}</Typography>
                      <Chip label={String(count)} size="small" />
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(Number(count) / (stats?.total_customers || 1)) * 100}
                      sx={{ mt: 1, height: 8, borderRadius: 4 }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Health Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TrendingUp fontSize="large" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Health Trends (Bottom 5)
              </Typography>
              <List dense>
                {topTrends.map((trend) => (
                  <ListItem key={trend.customer_id} divider>
                    <ListItemIcon>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: getHealthColor(trend.current_health),
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={trend.customer_name}
                      secondary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="caption">
                            Health: {Math.round(trend.current_health * 100)}%
                          </Typography>
                          <Typography variant="caption">
                            {getTrendIcon(trend.trend.trend)} {trend.trend.trend}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Alerts and At-Risk Customers */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Warning fontSize="large" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Recent Critical Alerts
              </Typography>
              <List>
                {recentAlerts.map((alert, index) => (
                  <ListItem key={index} divider>
                    <ListItemIcon>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: getSeverityColor(alert.severity),
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={alert.customer_name}
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            {alert.message}
                          </Typography>
                          <Chip
                            label={alert.type.replace('_', ' ')}
                            size="small"
                            sx={{ mt: 0.5 }}
                            color={
                              alert.severity === 'critical'
                                ? 'error'
                                : alert.severity === 'medium'
                                ? 'warning'
                                : 'success'
                            }
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Lightbulb fontSize="large" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Customers Needing Attention
              </Typography>
              <List>
                {atRiskCustomers.slice(0, 6).map((customer) => (
                  <ListItem key={customer.id} divider>
                    <ListItemIcon>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: getHealthColor(customer.health_score),
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={customer.name}
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            Health Score: {Math.round(customer.health_score * 100)}%
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {customer.customer_label}
                          </Typography>
                          {customer.payment_status && customer.payment_status !== 'current' && (
                            <Chip
                              label={`Payment: ${customer.payment_status}`}
                              size="small"
                              color="error"
                              sx={{ mt: 0.5, ml: 1 }}
                            />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Health Distribution */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Customer Health Distribution
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <CheckCircle fontSize="large" sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="h4" color="success.main">
                    {stats?.healthy_customers}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Healthy (60%+)
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Warning fontSize="large" sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                  <Typography variant="h4" color="warning.main">
                    {stats?.medium_risk_customers}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    At Risk (30-60%)
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <NotificationImportant fontSize="large" sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                  <Typography variant="h4" color="error.main">
                    {(stats?.total_customers || 0) - (stats?.healthy_customers || 0) - (stats?.medium_risk_customers || 0)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Critical (&lt;30%)
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 