import React from 'react';
import {
  Row,
  Col,
  Card,
  Table,
  Tag,
  Typography,
  Progress,
  Statistic,
  Space,
  Timeline,
  Spin,
} from 'antd';
import {
  ClockCircleOutlined,
  UserOutlined,
  TrophyOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { useParams } from 'react-router-dom';

const { Title, Text } = Typography;

interface CustomerJourney {
  customer_id: number;
  customer_name: string;
  current_stage: string;
  days_in_current_stage: number;
  previous_stage: string;
  time_to_value_days: number;
  journey_velocity: number;
  health_score: number;
  expansion_score: number;
  stage_history: Array<{
    stage: string;
    start_date: string;
    end_date: string;
    duration_days: number;
    key_activities: string[];
    health_change: number;
  }>;
  predicted_next_stage: string;
  predicted_timeline: number;
  recommendations: string[];
}

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

const CustomerJourneyPage: React.FC = () => {
  const { customerId } = useParams<{ customerId: string }>();

  const { data: journeyData, isLoading } = useQuery<CustomerJourney>(
    ['customerJourney', customerId],
    async () => {
      const response = await fetch(`http://localhost:8000/customers/${customerId}/journey`);
      return response.json();
    },
    {
      enabled: !!customerId,
    }
  );

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!journeyData) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>Customer Journey Not Found</Title>
        <Text>The customer journey data could not be loaded.</Text>
      </div>
    );
  }

  const stageHistoryColumns = [
    {
      title: 'Stage',
      dataIndex: 'stage',
      key: 'stage',
      render: (stage: string) => (
        <Tag color={getStageColor(stage.toLowerCase())} style={{ textTransform: 'capitalize' }}>
          {stage}
        </Tag>
      ),
    },
    {
      title: 'Duration',
      dataIndex: 'duration_days',
      key: 'duration_days',
      render: (days: number) => `${days} days`,
    },
    {
      title: 'Key Activities',
      dataIndex: 'key_activities',
      key: 'key_activities',
      render: (activities: string[]) => (
        <Space wrap>
          {activities.map((activity, index) => (
            <Tag key={index} color="blue">
              {activity}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Health Change',
      dataIndex: 'health_change',
      key: 'health_change',
      render: (change: number) => (
        <Tag color={change > 0 ? 'green' : change < 0 ? 'red' : 'default'}>
          {change > 0 ? '+' : ''}{Math.round(change * 100)}%
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Customer Journey: {journeyData.customer_name}
      </Title>

      {/* Customer Journey KPIs */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Current Stage"
              value={journeyData.current_stage}
              prefix={<UserOutlined />}
              valueStyle={{ color: getStageColor(journeyData.current_stage.toLowerCase()) }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Days in Current Stage"
              value={journeyData.days_in_current_stage}
              suffix="days"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Time to Value"
              value={journeyData.time_to_value_days}
              suffix="days"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Journey Velocity"
              value={Math.round(journeyData.journey_velocity * 100)}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ 
                color: journeyData.journey_velocity > 0 ? '#52c41a' : '#f5222d' 
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card>
            <Statistic
              title="Health Score"
              value={Math.round(journeyData.health_score * 100)}
              suffix="%"
              valueStyle={{ color: '#722ed1' }}
            />
            <Progress 
              percent={Math.round(journeyData.health_score * 100)} 
              status={journeyData.health_score > 0.7 ? 'success' : journeyData.health_score > 0.4 ? 'normal' : 'exception'}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card>
            <Statistic
              title="Expansion Score"
              value={Math.round(journeyData.expansion_score * 100)}
              suffix="%"
              valueStyle={{ color: '#fa8c16' }}
            />
            <Progress 
              percent={Math.round(journeyData.expansion_score * 100)} 
              strokeColor="#fa8c16"
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Journey Timeline */}
        <Col xs={24} lg={12}>
          <Card title="Journey Timeline" size="small">
            <Timeline>
              {journeyData.stage_history.map((stage, index) => (
                <Timeline.Item
                  key={index}
                  color={getStageColor(stage.stage.toLowerCase())}
                  label={stage.start_date}
                >
                  <div>
                    <Text strong style={{ textTransform: 'capitalize' }}>
                      {stage.stage} Stage
                    </Text>
                    <br />
                    <Text type="secondary">
                      Duration: {stage.duration_days} days
                    </Text>
                    <br />
                    <Text type="secondary">
                      Health Change: {stage.health_change > 0 ? '+' : ''}{Math.round(stage.health_change * 100)}%
                    </Text>
                  </div>
                </Timeline.Item>
              ))}
              <Timeline.Item color="blue" label="Current">
                <Text strong style={{ textTransform: 'capitalize' }}>
                  {journeyData.current_stage} Stage
                </Text>
                <br />
                <Text type="secondary">
                  {journeyData.days_in_current_stage} days and counting...
                </Text>
              </Timeline.Item>
              <Timeline.Item color="gray" label="Predicted">
                <Text style={{ textTransform: 'capitalize' }}>
                  {journeyData.predicted_next_stage} Stage
                </Text>
                <br />
                <Text type="secondary">
                  Estimated in {journeyData.predicted_timeline} days
                </Text>
              </Timeline.Item>
            </Timeline>
          </Card>
        </Col>

        {/* Stage History Table */}
        <Col xs={24} lg={12}>
          <Card title="Stage History Details" size="small">
            <Table
              dataSource={journeyData.stage_history}
              columns={stageHistoryColumns}
              size="small"
              pagination={false}
              rowKey={(record, index) => index?.toString() || '0'}
            />
          </Card>
        </Col>
      </Row>

      {/* Recommendations */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Journey Optimization Recommendations" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              {journeyData.recommendations.map((recommendation, index) => (
                <div key={index} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <Text>• {recommendation}</Text>
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CustomerJourneyPage; 