import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import { useQuery } from 'react-query';
import { apiService, Customer } from '../services/api';

const getHealthColor = (score: number) => {
  if (score < 0.3) return 'error';
  if (score < 0.6) return 'warning';
  return 'success';
};

const getRiskLevel = (score: number) => {
  if (score < 0.3) return 'Critical';
  if (score < 0.6) return 'Medium';
  return 'Healthy';
};

export default function CustomerList() {
  const { data: customers, isLoading, error } = useQuery<Customer[]>(
    'customers',
    apiService.getCustomers,
    { refetchInterval: 60000 }
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
        <Typography color="error">Failed to load customers</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customer Portfolio
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Customer Name</TableCell>
              <TableCell>Health Score</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>MRR</TableCell>
              <TableCell>Usage Score</TableCell>
              <TableCell>Support Tickets</TableCell>
              <TableCell>Last Login</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers?.map((customer) => (
              <TableRow key={customer.id} hover>
                <TableCell>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {customer.name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={customer.health_score * 100}
                      color={getHealthColor(customer.health_score)}
                      sx={{ width: 60, height: 8 }}
                    />
                    <Typography variant="body2">
                      {(customer.health_score * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getRiskLevel(customer.health_score)}
                    color={getHealthColor(customer.health_score)}
                    size="small"
                  />
                </TableCell>
                <TableCell>${customer.mrr.toLocaleString()}</TableCell>
                <TableCell>{(customer.usage_score * 100).toFixed(0)}%</TableCell>
                <TableCell>{customer.support_tickets}</TableCell>
                <TableCell>
                  {customer.last_login_days === 0 ? 'Today' : 
                   customer.last_login_days === 1 ? 'Yesterday' : 
                   `${customer.last_login_days} days ago`}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
} 