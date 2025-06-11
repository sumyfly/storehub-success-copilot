import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  Button,
} from '@mui/material';
import { useQuery } from 'react-query';
import { apiService, Alert as AlertType } from '../services/api';

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical': return 'error';
    case 'medium': return 'warning';
    case 'low': return 'info';
    default: return 'info';
  }
};

export default function AlertsPage() {
  const { data: alerts, isLoading, error } = useQuery<AlertType[]>(
    'alerts',
    apiService.getAlerts,
    { refetchInterval: 30000 }
  );

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography color="error">Failed to load alerts</Typography>
      </Box>
    );
  }

  // Group alerts by severity
  const criticalAlerts = alerts?.filter(a => a.severity === 'critical') || [];
  const mediumAlerts = alerts?.filter(a => a.severity === 'medium') || [];
  const lowAlerts = alerts?.filter(a => a.severity === 'low') || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customer Alerts & Actions
      </Typography>
      
      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" color="error" gutterBottom>
            🚨 Critical Alerts ({criticalAlerts.length})
          </Typography>
          <Paper elevation={2}>
            <List>
              {criticalAlerts.map((alert, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {alert.customer_name}
                          </Typography>
                          <Chip
                            label={alert.type.replace('_', ' ').toUpperCase()}
                            color={getSeverityColor(alert.severity)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Suggested Actions:
                          </Typography>
                          <Box sx={{ mt: 0.5 }}>
                            {alert.actions.map((action, actionIndex) => (
                              <Button
                                key={actionIndex}
                                variant="outlined"
                                size="small"
                                sx={{ mr: 1, mb: 0.5 }}
                              >
                                {action}
                              </Button>
                            ))}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < criticalAlerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Box>
      )}

      {/* Medium Priority Alerts */}
      {mediumAlerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" color="warning.main" gutterBottom>
            ⚠️ Medium Priority Alerts ({mediumAlerts.length})
          </Typography>
          <Paper elevation={1}>
            <List>
              {mediumAlerts.map((alert, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {alert.customer_name}
                          </Typography>
                          <Chip
                            label={alert.type.replace('_', ' ').toUpperCase()}
                            color={getSeverityColor(alert.severity)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Suggested Actions:
                          </Typography>
                          <Box sx={{ mt: 0.5 }}>
                            {alert.actions.map((action, actionIndex) => (
                              <Button
                                key={actionIndex}
                                variant="outlined"
                                size="small"
                                sx={{ mr: 1, mb: 0.5 }}
                              >
                                {action}
                              </Button>
                            ))}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < mediumAlerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Box>
      )}

      {/* Summary */}
      <Box sx={{ mt: 4 }}>
        <Alert severity="info">
          <Typography variant="body2">
            Total Active Alerts: {alerts?.length || 0} | 
            Critical: {criticalAlerts.length} | 
            Medium: {mediumAlerts.length} | 
            Low: {lowAlerts.length}
          </Typography>
        </Alert>
      </Box>
    </Box>
  );
} 