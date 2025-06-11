import React, { useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Card,
  CardContent,
  Tooltip,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  TrendingUp,
  TrendingDown,
  Remove as RemoveIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { apiService, getHealthColor, Customer, CustomerHealth } from '../services/api';

const CustomerList: React.FC = () => {
  const [selectedCustomer, setSelectedCustomer] = useState<number | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const { data: customers, isLoading } = useQuery<Customer[]>(
    'customers',
    apiService.getCustomers,
    { refetchInterval: 60000 }
  );

  const { data: customerHealth } = useQuery<CustomerHealth | null>(
    ['customerHealth', selectedCustomer],
    () => selectedCustomer ? apiService.getCustomerHealth(selectedCustomer) : null,
    { enabled: !!selectedCustomer }
  );

  const handleViewDetails = (customerId: number) => {
    setSelectedCustomer(customerId);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedCustomer(null);
  };

  const getRiskLevel = (score: number) => {
    if (score >= 0.8) return { label: 'Excellent', color: 'success' as const };
    if (score >= 0.6) return { label: 'Good', color: 'info' as const };
    if (score >= 0.3) return { label: 'At Risk', color: 'warning' as const };
    return { label: 'Critical', color: 'error' as const };
  };

  const getPaymentStatusColor = (status?: string) => {
    switch (status) {
      case 'current': return 'success';
      case 'late': return 'warning';
      case 'overdue': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp color="success" />;
      case 'declining': return <TrendingDown color="error" />;
      case 'stable': return <RemoveIcon color="action" />;
      default: return <RemoveIcon color="action" />;
    }
  };

  if (isLoading) {
    return <Box>Loading customers...</Box>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customer Health Overview
      </Typography>

      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Customer Name</TableCell>
              <TableCell>Customer Label</TableCell>
              <TableCell>Health Score</TableCell>
              <TableCell>MRR</TableCell>
              <TableCell>Payment Status</TableCell>
              <TableCell>Support Tickets</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers?.map((customer) => {
              const riskLevel = getRiskLevel(customer.health_score);
              return (
                <TableRow key={customer.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle1">{customer.name}</Typography>
                      <Typography variant="caption" color="textSecondary">
                        {customer.customer_type}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={customer.customer_label}
                      size="small"
                      sx={{ fontSize: '0.75rem' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={customer.health_score * 100}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: 'grey.200',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getHealthColor(customer.health_score),
                            },
                          }}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ minWidth: 35 }}>
                        {Math.round(customer.health_score * 100)}%
                      </Typography>
                    </Box>
                    <Chip 
                      label={riskLevel.label} 
                      color={riskLevel.color} 
                      size="small" 
                      sx={{ mt: 0.5 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      ${customer.mrr.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={customer.payment_status || 'current'}
                      color={getPaymentStatusColor(customer.payment_status)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={customer.support_tickets}
                      color={customer.support_tickets > 5 ? 'error' : customer.support_tickets > 2 ? 'warning' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography 
                      variant="body2"
                      color={customer.last_login_days > 30 ? 'error' : customer.last_login_days > 7 ? 'warning' : 'textPrimary'}
                    >
                      {customer.last_login_days} days ago
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View detailed health report">
                      <IconButton 
                        onClick={() => handleViewDetails(customer.id)}
                        size="small"
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Customer Health Details Modal */}
      <Dialog 
        open={detailsOpen} 
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Customer Health Report: {customerHealth?.customer_name}
        </DialogTitle>
        <DialogContent>
          {customerHealth && (
            <Grid container spacing={3} sx={{ mt: 1 }}>
              {/* Health Overview */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Health Overview
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="textSecondary">
                        Overall Health Score
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={customerHealth.overall_health_score * 100}
                          sx={{
                            height: 10,
                            borderRadius: 5,
                            flexGrow: 1,
                            backgroundColor: 'grey.200',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getHealthColor(customerHealth.overall_health_score),
                            },
                          }}
                        />
                        <Typography variant="h6">
                          {Math.round(customerHealth.overall_health_score * 100)}%
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Chip label={customerHealth.customer_label} sx={{ mb: 1 }} />
                      <Typography variant="body2" color="textSecondary">
                        Risk Level: {customerHealth.risk_level}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Health Factors */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Health Factors
                    </Typography>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">Usage Score: {Math.round(customerHealth.factors.usage_score * 100)}%</Typography>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">Engagement: {Math.round(customerHealth.factors.engagement_score * 100)}%</Typography>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">Support Tickets: {customerHealth.factors.support_tickets}</Typography>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">Payment Status: {customerHealth.factors.payment_status}</Typography>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">NPS Score: {customerHealth.factors.nps_score}/10</Typography>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2">Feature Adoption:</Typography>
                      <Typography variant="caption" sx={{ ml: 2 }}>
                        Core: {Math.round(customerHealth.factors.feature_adoption.core * 100)}% | 
                        Advanced: {Math.round(customerHealth.factors.feature_adoption.advanced * 100)}% | 
                        Integrations: {Math.round(customerHealth.factors.feature_adoption.integrations * 100)}%
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Health Trend */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Health Trend
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      {getTrendIcon(customerHealth.health_trend.trend)}
                      <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                        {customerHealth.health_trend.trend}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      30-day change: {customerHealth.health_trend.change_30d > 0 ? '+' : ''}{Math.round(customerHealth.health_trend.change_30d * 100)}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Forecast (30d): {Math.round(customerHealth.health_trend.forecast_30d * 100)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Recommended Actions */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Top Recommended Actions
                    </Typography>
                    {customerHealth.recommended_actions.slice(0, 3).map((action, index) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Typography variant="body2" fontWeight="medium">
                          {action.description}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                          <Chip label={action.urgency} size="small" color="primary" />
                          <Chip label={`${action.effort} effort`} size="small" variant="outlined" />
                          <Chip label={`${action.expected_impact} impact`} size="small" variant="outlined" />
                        </Box>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomerList; 