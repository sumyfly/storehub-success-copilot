import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Tabs, 
  Select, 
  Space, 
  Typography, 
  Alert,
  List,
  message,
  Button,
  Modal,
  Tag,
  Spin
} from 'antd';
import { 
  ThunderboltOutlined, 
  ClockCircleOutlined, 
  TrophyOutlined,
  UserOutlined,
  SettingOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import ActionCard from '../components/ActionCard';
import { api } from '../services/api';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

interface ActionsDashboard {
  summary: {
    total_recommendations: number;
    critical_actions: number;
    high_priority_actions: number;
    medium_priority_actions: number;
  };
  by_urgency: {
    critical: any[];
    high: any[];
    medium: any[];
  };
  by_category: {
    retention: number;
    engagement: number;
    expansion: number;
    support: number;
  };
  top_actions_today: any[];
}

const ActionsPage: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<ActionsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedUrgency, setSelectedUrgency] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [executionModal, setExecutionModal] = useState<{
    visible: boolean;
    action?: any;
  }>({ visible: false });

  useEffect(() => {
    loadActionsDashboard();
  }, []);

  const loadActionsDashboard = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/actions');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading actions dashboard:', error);
      message.error('Failed to load actions dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteAction = async (actionId: string) => {
    const action = findActionById(actionId);
    if (action) {
      setExecutionModal({ visible: true, action });
    }
  };

  const confirmExecuteAction = async () => {
    if (!executionModal.action) return;

    try {
      const response = await api.post(`/actions/${executionModal.action.id}/execute`, {
        customer_id: executionModal.action.customer_id,
        csm_id: 'current_user'
      });
      
      message.success(`Action "${executionModal.action.title}" executed successfully!`);
      setExecutionModal({ visible: false });
      loadActionsDashboard(); // Refresh data
    } catch (error) {
      console.error('Error executing action:', error);
      message.error('Failed to execute action');
    }
  };

  const handleViewDetails = (actionId: string) => {
    const action = findActionById(actionId);
    if (action) {
      Modal.info({
        title: action.title,
        width: 600,
        content: (
          <div>
            <p><strong>Description:</strong> {action.description}</p>
            <p><strong>Customer:</strong> {action.customer_name}</p>
            <p><strong>Timeline:</strong> {action.timeline}</p>
            <p><strong>Success Rate:</strong> {Math.round(action.success_rate * 100)}%</p>
            <p><strong>Business Impact:</strong> {action.business_impact}</p>
            {action.estimated_roi && (
              <p><strong>Estimated ROI:</strong> {action.estimated_roi}</p>
            )}
            {action.urgency_reason && (
              <p><strong>Urgency Reason:</strong> {action.urgency_reason}</p>
            )}
            {action.steps && action.steps.length > 0 && (
              <div>
                <strong>Steps:</strong>
                <ol style={{ marginTop: 8 }}>
                  {action.steps.map((step: string, index: number) => (
                    <li key={index} style={{ marginBottom: 4 }}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        ),
      });
    }
  };

  const findActionById = (actionId: string) => {
    if (!dashboardData) return null;
    
    // Search in all urgency categories
    const allActions = [
      ...dashboardData.by_urgency.critical,
      ...dashboardData.by_urgency.high,
      ...dashboardData.by_urgency.medium,
      ...dashboardData.top_actions_today
    ];
    
    return allActions.find(action => action.id === actionId);
  };

  const filterActions = (actions: any[]) => {
    return actions.filter(action => {
      const urgencyMatch = selectedUrgency === 'all' || action.urgency === selectedUrgency;
      const categoryMatch = selectedCategory === 'all' || action.category === selectedCategory;
      return urgencyMatch && categoryMatch;
    });
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'retention':
        return <UserOutlined style={{ color: '#f5222d' }} />;
      case 'engagement':
        return <ThunderboltOutlined style={{ color: '#1890ff' }} />;
      case 'expansion':
        return <TrophyOutlined style={{ color: '#52c41a' }} />;
      case 'support':
        return <SettingOutlined style={{ color: '#fa8c16' }} />;
      default:
        return <SettingOutlined />;
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p style={{ marginTop: 16 }}>Loading action recommendations...</p>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <Alert
        message="Unable to load actions dashboard"
        description="Please try refreshing the page"
        type="error"
        showIcon
      />
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>🎯 Action Recommendations</Title>
        <Text type="secondary">
          Intelligent action recommendations to improve customer success outcomes
        </Text>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={loadActionsDashboard}
          style={{ float: 'right' }}
        >
          Refresh
        </Button>
      </div>

      {/* Summary Statistics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Recommendations"
              value={dashboardData.summary.total_recommendations}
              prefix={<SettingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Critical Actions"
              value={dashboardData.summary.critical_actions}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="High Priority"
              value={dashboardData.summary.high_priority_actions}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#d46b08' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Medium Priority"
              value={dashboardData.summary.medium_priority_actions}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Category Overview */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Space>
              {getCategoryIcon('retention')}
              <div>
                <Text strong>{dashboardData.by_category.retention}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>Retention</Text>
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Space>
              {getCategoryIcon('engagement')}
              <div>
                <Text strong>{dashboardData.by_category.engagement}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>Engagement</Text>
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Space>
              {getCategoryIcon('expansion')}
              <div>
                <Text strong>{dashboardData.by_category.expansion}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>Expansion</Text>
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Space>
              {getCategoryIcon('support')}
              <div>
                <Text strong>{dashboardData.by_category.support}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>Support</Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Text strong>Filters:</Text>
          <Select
            style={{ width: 150 }}
            placeholder="Urgency"
            value={selectedUrgency}
            onChange={setSelectedUrgency}
          >
            <Option value="all">All Urgencies</Option>
            <Option value="critical">Critical</Option>
            <Option value="high">High Priority</Option>
            <Option value="medium">Medium Priority</Option>
          </Select>
          <Select
            style={{ width: 150 }}
            placeholder="Category"
            value={selectedCategory}
            onChange={setSelectedCategory}
          >
            <Option value="all">All Categories</Option>
            <Option value="retention">Retention</Option>
            <Option value="engagement">Engagement</Option>
            <Option value="expansion">Expansion</Option>
            <Option value="support">Support</Option>
          </Select>
        </Space>
      </Card>

      {/* Actions by Urgency Tabs */}
      <Tabs defaultActiveKey="top_actions">
        <TabPane tab="🔥 Top Actions Today" key="top_actions">
          <List
            dataSource={filterActions(dashboardData.top_actions_today)}
            renderItem={(action: any) => (
              <List.Item style={{ padding: 0 }}>
                <div style={{ width: '100%' }}>
                  <ActionCard
                    action={action}
                    onExecute={handleExecuteAction}
                    onViewDetails={handleViewDetails}
                  />
                </div>
              </List.Item>
            )}
          />
        </TabPane>

        <TabPane 
          tab={
            <span>
              🚨 Critical 
              <Tag color="red" style={{ marginLeft: 8 }}>
                {filterActions(dashboardData.by_urgency.critical).length}
              </Tag>
            </span>
          } 
          key="critical"
        >
          {dashboardData.by_urgency.critical.length > 0 ? (
            <Alert
              message="Critical Actions Require Immediate Attention"
              description="These actions address high-risk customers and should be prioritized today."
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
            />
          ) : null}
          <List
            dataSource={filterActions(dashboardData.by_urgency.critical)}
            renderItem={(action: any) => (
              <List.Item style={{ padding: 0 }}>
                <div style={{ width: '100%' }}>
                  <ActionCard
                    action={action}
                    onExecute={handleExecuteAction}
                    onViewDetails={handleViewDetails}
                  />
                </div>
              </List.Item>
            )}
          />
        </TabPane>

        <TabPane 
          tab={
            <span>
              ⚠️ High Priority 
              <Tag color="orange" style={{ marginLeft: 8 }}>
                {filterActions(dashboardData.by_urgency.high).length}
              </Tag>
            </span>
          } 
          key="high"
        >
          <List
            dataSource={filterActions(dashboardData.by_urgency.high)}
            renderItem={(action: any) => (
              <List.Item style={{ padding: 0 }}>
                <div style={{ width: '100%' }}>
                  <ActionCard
                    action={action}
                    onExecute={handleExecuteAction}
                    onViewDetails={handleViewDetails}
                  />
                </div>
              </List.Item>
            )}
          />
        </TabPane>

        <TabPane 
          tab={
            <span>
              📋 Medium Priority 
              <Tag color="blue" style={{ marginLeft: 8 }}>
                {filterActions(dashboardData.by_urgency.medium).length}
              </Tag>
            </span>
          } 
          key="medium"
        >
          <List
            dataSource={filterActions(dashboardData.by_urgency.medium)}
            renderItem={(action: any) => (
              <List.Item style={{ padding: 0 }}>
                <div style={{ width: '100%' }}>
                  <ActionCard
                    action={action}
                    onExecute={handleExecuteAction}
                    onViewDetails={handleViewDetails}
                  />
                </div>
              </List.Item>
            )}
          />
        </TabPane>
      </Tabs>

      {/* Execution Confirmation Modal */}
      <Modal
        title="Execute Action"
        open={executionModal.visible}
        onOk={confirmExecuteAction}
        onCancel={() => setExecutionModal({ visible: false })}
        okText="Execute Action"
        okType="primary"
      >
        {executionModal.action && (
          <div>
            <p><strong>Action:</strong> {executionModal.action.title}</p>
            <p><strong>Customer:</strong> {executionModal.action.customer_name}</p>
            <p><strong>Timeline:</strong> {executionModal.action.timeline}</p>
            <p><strong>Success Rate:</strong> {Math.round(executionModal.action.success_rate * 100)}%</p>
            <Alert
              message="Are you sure you want to execute this action?"
              description="This will mark the action as in progress and may trigger automated workflows."
              type="info"
              showIcon
              style={{ marginTop: 16 }}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ActionsPage; 