import React from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  Table,
  Tag,
  Alert,
  Typography,
  List,
  Avatar,
  Space,
  Divider,
  Badge,
  Spin,
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  TeamOutlined,
  AlertOutlined,
  DollarOutlined,
  TrophyOutlined,
  UserOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { Column } from '@ant-design/charts';
import { apiService, DashboardStats, Customer, Alert as AlertType } from '../services/api';

const { Title, Text } = Typography;

// Health Score Progress Component
const HealthScoreProgress = ({ score }: { score: number }) => {
  const percentage = Math.round(score * 100);
  let status: 'success' | 'normal' | 'exception' = 'normal';
  
  if (percentage >= 70) status = 'success';
  else if (percentage < 30) status = 'exception';
  
  return <Progress percent={percentage} status={status} size="small" />;
};

// Severity Tag Component
const SeverityTag = ({ severity }: { severity: string }) => {
  const colors = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'green',
  };
  
  return <Tag color={colors[severity as keyof typeof colors]}>{severity.toUpperCase()}</Tag>;
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

  const { data: customers, isLoading: customersLoading } = useQuery(
    'customers',
    apiService.getCustomers
  );

  const { data: trends } = useQuery(
    'trends',
    apiService.getHealthTrends
  );

  if (statsLoading || alertsLoading || customersLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  // Process data for charts
  const healthDistribution = [
    { range: 'Excellent (80-100%)', count: customers?.filter(c => c.health_score >= 0.8).length || 0 },
    { range: 'Good (60-80%)', count: customers?.filter(c => c.health_score >= 0.6 && c.health_score < 0.8).length || 0 },
    { range: 'At Risk (30-60%)', count: customers?.filter(c => c.health_score >= 0.3 && c.health_score < 0.6).length || 0 },
    { range: 'Critical (<30%)', count: customers?.filter(c => c.health_score < 0.3).length || 0 },
  ];

  // Recent alerts table columns
  const alertColumns = [
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      render: (name: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Alert Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => <SeverityTag severity={severity} />,
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
  ];

  // At-risk customers table columns
  const riskColumns = [
    {
      title: 'Customer',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Health Score',
      dataIndex: 'health_score',
      key: 'health_score',
      render: (score: number) => <HealthScoreProgress score={score} />,
      sorter: (a: Customer, b: Customer) => a.health_score - b.health_score,
    },
    {
      title: 'MRR',
      dataIndex: 'mrr',
      key: 'mrr',
      render: (mrr: number) => `$${mrr.toLocaleString()}`,
      sorter: (a: Customer, b: Customer) => a.mrr - b.mrr,
    },
    {
      title: 'Last Login',
      dataIndex: 'last_login_days',
      key: 'last_login_days',
      render: (days: number) => (
        <Tag color={days > 14 ? 'red' : days > 7 ? 'orange' : 'green'}>
          {days} days ago
        </Tag>
      ),
    },
  ];

  const recentAlerts = alerts?.slice(0, 5) || [];
  const atRiskCustomers = customers?.filter(c => c.health_score < 0.6).slice(0, 5) || [];
  const totalMrr = customers?.reduce((sum, c) => sum + c.mrr, 0) || 0;

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Customer Success Dashboard
      </Title>
      
      {/* Key Performance Indicators */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Customers"
              value={stats?.total_customers || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Critical Alerts"
              value={stats?.critical_alerts || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              suffix={
                <Badge 
                  count={`/${stats?.total_alerts || 0}`} 
                  style={{ backgroundColor: '#52c41a' }}
                />
              }
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Monthly Recurring Revenue"
              value={totalMrr}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
              formatter={(value) => `$${Number(value).toLocaleString()}`}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Average Health Score"
              value={stats?.average_health_score ? parseFloat(stats.average_health_score) * 100 : 0}
              prefix={<TrophyOutlined />}
              suffix="%"
              precision={1}
              valueStyle={{ 
                color: (stats?.average_health_score ? parseFloat(stats.average_health_score) : 0) > 0.7 ? '#52c41a' : '#faad14' 
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* Health Distribution Chart */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Customer Health Distribution" extra={<TrophyOutlined />}>
            <Column
              data={healthDistribution}
              xField="range"
              yField="count"
              columnStyle={{
                fill: ({ range }) => {
                  if (range.includes('Excellent')) return '#52c41a';
                  if (range.includes('Good')) return '#1890ff';
                  if (range.includes('At Risk')) return '#faad14';
                  return '#ff4d4f';
                },
              }}
              label={{
                position: 'top',
                style: { fill: '#000', fontSize: 12 },
              }}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="System Health Overview" extra={<CheckCircleOutlined />}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card size="small">
                  <Statistic
                    title="Healthy Customers"
                    value={customers?.filter(c => c.health_score >= 0.7).length || 0}
                    valueStyle={{ color: '#52c41a' }}
                    prefix={<CheckCircleOutlined />}
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small">
                  <Statistic
                    title="At Risk"
                    value={customers?.filter(c => c.health_score < 0.6).length || 0}
                    valueStyle={{ color: '#faad14' }}
                    prefix={<ExclamationCircleOutlined />}
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small">
                  <Statistic
                    title="Critical Risk"
                    value={customers?.filter(c => c.health_score < 0.3).length || 0}
                    valueStyle={{ color: '#ff4d4f' }}
                    prefix={<AlertOutlined />}
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small">
                  <Statistic
                    title="Revenue at Risk"
                    value={customers?.filter(c => c.health_score < 0.6).reduce((sum, c) => sum + c.mrr, 0) || 0}
                    valueStyle={{ color: '#ff4d4f' }}
                    prefix={<DollarOutlined />}
                    formatter={(value) => `$${Number(value).toLocaleString()}`}
                  />
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Recent Alerts and At-Risk Customers */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card 
            title="Recent Critical Alerts" 
            extra={<Badge count={recentAlerts.length} style={{ backgroundColor: '#ff4d4f' }} />}
          >
            <Table
              dataSource={recentAlerts}
              columns={alertColumns}
              pagination={false}
              size="small"
              rowKey={(record, index) => index || 0}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={10}>
          <Card 
            title="Customers Requiring Attention"
            extra={<ExclamationCircleOutlined style={{ color: '#faad14' }} />}
          >
            <Table
              dataSource={atRiskCustomers}
              columns={riskColumns}
              pagination={false}
              size="small"
              rowKey="id"
            />
          </Card>
        </Col>
      </Row>

      {/* Action Items */}
      <Row style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Recommended Actions" extra={<ClockCircleOutlined />}>
            <List
              dataSource={[
                {
                  title: 'Schedule urgent calls with critical risk customers',
                  description: `${customers?.filter(c => c.health_score < 0.3).length || 0} customers need immediate attention`,
                  priority: 'high',
                },
                {
                  title: 'Review customers with declining usage',
                  description: 'Proactive outreach to prevent churn',
                  priority: 'medium',
                },
                {
                  title: 'Analyze support ticket trends',
                  description: 'Identify common issues affecting customer health',
                  priority: 'low',
                },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Badge 
                        status={item.priority === 'high' ? 'error' : item.priority === 'medium' ? 'warning' : 'processing'} 
                      />
                    }
                    title={item.title}
                    description={item.description}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 