import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme as antTheme } from 'antd';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import 'antd/dist/reset.css';
import './index.css';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CustomerList from './pages/CustomerList';
import AlertsPage from './pages/AlertsPage';
import ActionsPage from './pages/ActionsPage';

// Ant Design theme configuration
const customTheme = {
  algorithm: antTheme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    borderRadius: 6,
    fontSize: 14,
  },
  components: {
    Layout: {
      bodyBg: '#f0f2f5',
      siderBg: '#001529',
      headerBg: '#fff',
    },
    Menu: {
      darkItemBg: '#001529',
      darkItemSelectedBg: '#1890ff',
    },
  },
};

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  console.log('Customer Success Copilot - Full App Loading!');
  
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={customTheme}>
        <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/customers" element={<CustomerList />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/actions" element={<ActionsPage />} />
              </Routes>
            </Layout>
          </Router>
          <Toaster position="top-right" />
        </div>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App; 