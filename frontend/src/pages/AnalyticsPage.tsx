import React, { useState } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  Table,
  Tag,
  Typography,
  Tabs,
  Space,
  Alert,
  Badge,
  Tooltip,
  Spin,
} from 'antd';
import {
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  DollarOutlined,
  AlertOutlined,
  TeamOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  CaretUpOutlined,
  CaretDownOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { Column, Pie } from '@ant-design/charts';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface JourneyAnalytics {
  stage_distribution: { [key: string]: number };
  stage_performance: {
    [key: string]: {
      customers: Array<{
        id: number;
        name: string;
        health_score: number;
        days_in_stage: number;
        journey_velocity: number;
        expansion_score: number;
      }>;
      avg_health: number;
      avg_days_in_stage: number;
      expansion_potential: number;
    };
  };
  journey_insights: {
    total_customers: number;
    fastest_time_to_value: number;
    slowest_time_to_value: number;
    avg_time_to_value: number;
  };
}

interface RiskAnalytics {
  risk_distribution: { [key: string]: number };
  risk_details: {
    critical_30d: Array<any>;
    high_60d: Array<any>;
    medium_90d: Array<any>;
    low_risk: Array<any>;
  };
  revenue_at_risk: {
    critical_30d: number;
    high_60d: number;
    medium_90d: number;
  };
  total_revenue_at_risk: number;
  prediction_insights: {
    highest_risk_customer: string;
    most_stable_customer: string;
    avg_churn_probability_30d: number;
  };
}

interface RevenueAnalytics {
  expansion_opportunities: {
    high_potential: Array<any>;
    count: number;
    revenue_potential: number;
  };
  upsell_candidates: {
    ready_customers: Array<any>;
    count: number;
    revenue_potential: number;
  };
  cross_sell_opportunities: {
    customers_with_potential: Array<any>;
    count: number;
    popular_products: string[];
  };
  revenue_insights: {
    total_current_mrr: number;
    total_ltv_prediction: number;
    avg_revenue_growth: number;
    expansion_revenue_potential: number;
  };
}

// Stage color mapping
const getStageColor = (stage: string) => {
  const colors: any = {
    onboarding: '#1890ff',
    adoption: '#52c41a',
    growth: '#13c2c2',
    mature: '#722ed1',
    at_risk: '#f5222d',
    unknown: '#8c8c8c',
  };
  return colors[stage] || '#8c8c8c';
};

// Risk level component
const RiskLevel = ({ percentage }: { percentage: number }) => {
  let color = 'green';
  let text = 'Low';
  if (percentage > 0.7) {
    color = 'red';
    text = 'High';
  } else if (percentage > 0.4) {
    color = 'orange';
    text = 'Medium';
  }
  
  return (
    <Tag color={color}>
      {text}: {Math.round(percentage * 100)}%
    </Tag>
  );
};

const AnalyticsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('journey');

  // Fetch analytics data
  const { data: journeyData, isLoading: journeyLoading } = useQuery<JourneyAnalytics>(
    'journeyAnalytics',
    async () => {
      const response = await fetch('http://localhost:8000/analytics/customer-journey');
      return response.json();
    }
  );

  const { data: riskData, isLoading: riskLoading } = useQuery<RiskAnalytics>(
    'riskAnalytics',
    async () => {
      const response = await fetch('http://localhost:8000/analytics/risk-prediction');
      return response.json();
    }
  );

  const { data: revenueData, isLoading: revenueLoading } = useQuery<RevenueAnalytics>(
    'revenueAnalytics',
    async () => {
      const response = await fetch('http://localhost:8000/analytics/revenue-intelligence');
      return response.json();
    }
  );

  if (journeyLoading || riskLoading || revenueLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  // Prepare chart data
  const stageDistributionData = journeyData ? Object.entries(journeyData.stage_distribution).map(([stage, count]) => ({
    stage: stage.charAt(0).toUpperCase() + stage.slice(1),
    count,
    color: getStageColor(stage)
  })) : [];

  const riskDistributionData = riskData ? Object.entries(riskData.risk_distribution).map(([risk, count]) => ({
    risk: risk.replace('_', ' ').toUpperCase(),
    count,
    value: count
  })) : [];

  // Journey stage performance table columns
  const stageColumns = [
    {
      title: 'Lifecycle Stage',
      dataIndex: 'stage',
      key: 'stage',
      render: (stage: string) => (
        <Tag color={getStageColor(stage.toLowerCase())} style={{ textTransform: 'capitalize' }}>
          {stage}
        </Tag>
      ),
    },
    {
      title: 'Customers',
      dataIndex: 'count',
      key: 'count',
      render: (count: number) => <Badge count={count} style={{ backgroundColor: '#1890ff' }} />,
    },
    {
      title: 'Avg Health Score',
      dataIndex: 'avg_health',
      key: 'avg_health',
      render: (score: number) => (
        <Progress 
          percent={Math.round(score * 100)} 
          size="small" 
          status={score > 0.7 ? 'success' : score > 0.4 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: 'Avg Days in Stage',
      dataIndex: 'avg_days_in_stage',
      key: 'avg_days_in_stage',
      render: (days: number) => `${days} days`,
    },
    {
      title: 'Expansion Potential',
      dataIndex: 'expansion_potential',
      key: 'expansion_potential',
      render: (potential: number) => (
        <Tag color={potential > 0.6 ? 'green' : potential > 0.3 ? 'orange' : 'red'}>
          {Math.round(potential * 100)}%
        </Tag>
      ),
    },
  ];

  const stageTableData = journeyData ? Object.entries(journeyData.stage_performance).map(([stage, data]: [string, any]) => ({
    key: stage,
    stage,
    count: data.customers.length,
    avg_health: data.avg_health,
    avg_days_in_stage: data.avg_days_in_stage,
    expansion_potential: data.expansion_potential,
  })) : [];

  // Risk customers table columns
  const riskColumns = [
    {
      title: 'Customer',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: 'MRR',
      dataIndex: 'mrr',
      key: 'mrr',
      render: (mrr: number) => `$${mrr?.toLocaleString()}`,
    },
    {
      title: '30d Risk',
      dataIndex: 'churn_30d',
      key: 'churn_30d',
      render: (risk: number) => <RiskLevel percentage={risk} />,
    },
    {
      title: 'Risk Factors',
      dataIndex: 'risk_factors',
      key: 'risk_factors',
      render: (factors: string[]) => (
        <Space wrap>
          {factors?.map((factor: string) => (
            <Tag key={factor} color="red">
              {factor.replace('_', ' ')}
            </Tag>
          ))}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Advanced Customer Intelligence Analytics
      </Title>

      <Tabs activeKey={activeTab} onChange={setActiveTab} size="large">
        {/* Customer Journey Analytics Tab */}
        <TabPane 
          tab={
            <span>
              <TrophyOutlined />
              Customer Journey
            </span>
          } 
          key="journey"
        >
          {/* Journey KPIs */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Total Customers"
                  value={journeyData?.journey_insights.total_customers || 0}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Avg Time to Value"
                  value={journeyData?.journey_insights.avg_time_to_value || 0}
                  suffix="days"
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Fastest Time to Value"
                  value={journeyData?.journey_insights.fastest_time_to_value || 0}
                  suffix="days"
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Slowest Time to Value"
                  value={journeyData?.journey_insights.slowest_time_to_value || 0}
                  suffix="days"
                  prefix={<AlertOutlined />}
                  valueStyle={{ color: '#f5222d' }}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            {/* Stage Distribution Chart */}
            <Col xs={24} lg={12}>
              <Card title="Lifecycle Stage Distribution" size="small">
                <Column
                  data={stageDistributionData}
                  xField="stage"
                  yField="count"
                  color="#1890ff"
                />
              </Card>
            </Col>

            {/* Stage Performance Table */}
            <Col xs={24} lg={12}>
              <Card title="Stage Performance Analysis" size="small">
                <Table 
                  dataSource={stageTableData} 
                  columns={stageColumns} 
                  size="small" 
                  pagination={false}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* Risk Prediction Analytics Tab */}
        <TabPane 
          tab={
            <span>
              <AlertOutlined />
              Risk Prediction
            </span>
          } 
          key="risk"
        >
          {/* Risk KPIs */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Critical Risk (30d)"
                  value={riskData?.risk_distribution.critical_30d || 0}
                  prefix={<AlertOutlined />}
                  valueStyle={{ color: '#f5222d' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Revenue at Risk"
                  value={riskData?.total_revenue_at_risk || 0}
                  prefix={<DollarOutlined />}
                  formatter={(value: any) => `$${value?.toLocaleString()}`}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Avg Churn Risk"
                  value={riskData?.prediction_insights.avg_churn_probability_30d 
                    ? Math.round(riskData.prediction_insights.avg_churn_probability_30d * 100) 
                    : 0}
                  suffix="%"
                  prefix={<CaretDownOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Stable Customers"
                  value={riskData?.risk_distribution.low_risk || 0}
                  prefix={<CaretUpOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Risk Insights */}
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col span={24}>
              <Alert
                message="Risk Analysis Insights"
                description={
                  <Space direction="vertical">
                    <Text>
                      <strong>Highest Risk:</strong> {riskData?.prediction_insights.highest_risk_customer}
                    </Text>
                    <Text>
                      <strong>Most Stable:</strong> {riskData?.prediction_insights.most_stable_customer}
                    </Text>
                  </Space>
                }
                type="info"
                showIcon
              />
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            {/* Risk Distribution Chart */}
            <Col xs={24} lg={12}>
              <Card title="Risk Distribution Overview" size="small">
                <Pie
                  data={riskDistributionData}
                  angleField="value"
                  colorField="risk"
                  radius={0.8}
                  label={{
                    type: 'spider',
                    labelHeight: 28,
                    content: '{name}: {percentage}',
                  }}
                />
              </Card>
            </Col>

            {/* High Risk Customers */}
            <Col xs={24} lg={12}>
              <Card title="High Risk Customers" size="small">
                <Table
                  dataSource={[
                    ...(riskData?.risk_details.critical_30d || []),
                    ...(riskData?.risk_details.medium_90d || [])
                  ]}
                  columns={riskColumns}
                  size="small"
                  pagination={{ pageSize: 5 }}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* Revenue Intelligence Tab */}
        <TabPane 
          tab={
            <span>
              <DollarOutlined />
              Revenue Intelligence
            </span>
          } 
          key="revenue"
        >
          {/* Revenue KPIs */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Current MRR"
                  value={revenueData?.revenue_insights.total_current_mrr || 0}
                  prefix={<DollarOutlined />}
                  formatter={(value: any) => `$${value?.toLocaleString()}`}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Expansion Potential"
                  value={revenueData?.revenue_insights.expansion_revenue_potential || 0}
                  prefix={<RiseOutlined />}
                  formatter={(value: any) => `$${value?.toLocaleString()}`}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Expansion Ready"
                  value={revenueData?.expansion_opportunities.count || 0}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Avg Revenue Growth"
                  value={revenueData?.revenue_insights.avg_revenue_growth 
                    ? Math.round(revenueData.revenue_insights.avg_revenue_growth * 100) 
                    : 0}
                  suffix="%"
                  prefix={revenueData?.revenue_insights.avg_revenue_growth && revenueData.revenue_insights.avg_revenue_growth > 0 ? <RiseOutlined /> : <FallOutlined />}
                  valueStyle={{ 
                    color: revenueData?.revenue_insights.avg_revenue_growth && revenueData.revenue_insights.avg_revenue_growth > 0 ? '#52c41a' : '#f5222d' 
                  }}
                />
              </Card>
            </Col>
          </Row>

          {/* Revenue Opportunities */}
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={8}>
              <Card title="Expansion Opportunities" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Statistic
                    title="High Potential Customers"
                    value={revenueData?.expansion_opportunities.count || 0}
                    valueStyle={{ color: '#52c41a' }}
                  />
                  <Statistic
                    title="Revenue Potential"
                    value={revenueData?.expansion_opportunities.revenue_potential || 0}
                    formatter={(value: any) => `$${value?.toLocaleString()}`}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Space>
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="Upsell Candidates" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Statistic
                    title="Ready Customers"
                    value={revenueData?.upsell_candidates.count || 0}
                    valueStyle={{ color: '#fa8c16' }}
                  />
                  <Statistic
                    title="Revenue Potential"
                    value={revenueData?.upsell_candidates.revenue_potential || 0}
                    formatter={(value: any) => `$${value?.toLocaleString()}`}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Space>
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="Cross-sell Opportunities" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Statistic
                    title="Customers with Potential"
                    value={revenueData?.cross_sell_opportunities.count || 0}
                    valueStyle={{ color: '#722ed1' }}
                  />
                  <div>
                    <Text strong>Popular Products:</Text>
                    <div style={{ marginTop: 8 }}>
                      {revenueData?.cross_sell_opportunities.popular_products?.map((product: string) => (
                        <Tag key={product} color="blue" style={{ margin: '2px' }}>
                          {product}
                        </Tag>
                      ))}
                    </div>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default AnalyticsPage; 