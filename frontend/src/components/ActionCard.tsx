import React from 'react';
import { Card, Tag, Button, Typography, Progress, Space, Tooltip } from 'antd';
import { 
  ClockCircleOutlined, 
  TrophyOutlined, 
  DollarOutlined,
  ThunderboltOutlined,
  PhoneOutlined,
  MailOutlined,
  UserOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

interface ActionCardProps {
  action: {
    id: string;
    title: string;
    description: string;
    category: string;
    urgency: string;
    effort: string;
    timeline: string;
    success_rate: number;
    business_impact: string;
    customer_name?: string;
    customer_mrr?: number;
    estimated_roi?: string;
    urgency_reason?: string;
    steps?: string[];
  };
  onExecute?: (actionId: string) => void;
  onViewDetails?: (actionId: string) => void;
  compact?: boolean;
}

const ActionCard: React.FC<ActionCardProps> = ({ 
  action, 
  onExecute, 
  onViewDetails, 
  compact = false 
}) => {
  // Get urgency color and icon
  const getUrgencyConfig = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return { color: 'red', icon: <ThunderboltOutlined />, text: 'Critical' };
      case 'high':
        return { color: 'orange', icon: <ClockCircleOutlined />, text: 'High Priority' };
      case 'medium':
        return { color: 'blue', icon: <SettingOutlined />, text: 'Medium Priority' };
      default:
        return { color: 'default', icon: <SettingOutlined />, text: 'Low Priority' };
    }
  };

  // Get category icon
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

  // Get action type icon
  const getActionIcon = (title: string) => {
    if (title.toLowerCase().includes('call')) return <PhoneOutlined />;
    if (title.toLowerCase().includes('email')) return <MailOutlined />;
    if (title.toLowerCase().includes('training')) return <TrophyOutlined />;
    return <SettingOutlined />;
  };

  const urgencyConfig = getUrgencyConfig(action.urgency);
  const successRate = Math.round(action.success_rate * 100);
  
  const cardTitle = (
    <Space size="small">
      {getCategoryIcon(action.category)}
      <Text strong>{action.title}</Text>
      {action.customer_name && (
        <Tag color="blue" style={{ marginLeft: 8 }}>
          {action.customer_name}
        </Tag>
      )}
    </Space>
  );

  const cardExtra = (
    <Space>
      <Tag color={urgencyConfig.color} icon={urgencyConfig.icon}>
        {urgencyConfig.text}
      </Tag>
      {!compact && (
        <Tag color="green" icon={<TrophyOutlined />}>
          {successRate}% success
        </Tag>
      )}
    </Space>
  );

  const cardActions = compact ? [] : [
    <Button 
      key="execute" 
      type="primary" 
      icon={getActionIcon(action.title)}
      onClick={() => onExecute?.(action.id)}
    >
      Execute
    </Button>,
    <Button 
      key="details" 
      onClick={() => onViewDetails?.(action.id)}
    >
      View Details
    </Button>
  ];

  return (
    <Card
      title={cardTitle}
      extra={cardExtra}
      actions={cardActions}
      style={{ 
        marginBottom: 16,
        borderLeft: `4px solid ${urgencyConfig.color === 'red' ? '#f5222d' : urgencyConfig.color === 'orange' ? '#fa8c16' : '#1890ff'}`
      }}
      size={compact ? "small" : "default"}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* Description */}
        <Text type="secondary">{action.description}</Text>

        {/* Key Metrics Row */}
        <Space wrap>
          <Tooltip title="Expected completion time">
            <Tag icon={<ClockCircleOutlined />} color="blue">
              {action.timeline}
            </Tag>
          </Tooltip>
          
          <Tooltip title="Effort level required">
            <Tag color={action.effort === 'high' ? 'red' : action.effort === 'medium' ? 'orange' : 'green'}>
              {action.effort} effort
            </Tag>
          </Tooltip>

          {action.estimated_roi && (
            <Tooltip title="Estimated return on investment">
              <Tag icon={<DollarOutlined />} color="gold">
                {action.estimated_roi}
              </Tag>
            </Tooltip>
          )}
        </Space>

        {/* Success Rate Progress */}
        {!compact && (
          <div>
            <Text strong style={{ fontSize: '12px' }}>Success Rate:</Text>
            <Progress 
              percent={successRate} 
              size="small" 
              strokeColor={successRate > 60 ? '#52c41a' : successRate > 40 ? '#fa8c16' : '#f5222d'}
              showInfo={false}
              style={{ marginTop: 4 }}
            />
            <Text type="secondary" style={{ fontSize: '12px' }}>{successRate}%</Text>
          </div>
        )}

        {/* Urgency Reason */}
        {action.urgency_reason && !compact && (
          <Text type="secondary" style={{ fontSize: '12px', fontStyle: 'italic' }}>
            💡 {action.urgency_reason}
          </Text>
        )}

        {/* Quick Steps Preview */}
        {action.steps && action.steps.length > 0 && !compact && (
          <div>
            <Text strong style={{ fontSize: '12px' }}>Key Steps:</Text>
            <ul style={{ margin: '4px 0', paddingLeft: '16px', fontSize: '12px' }}>
              {action.steps.slice(0, 2).map((step, index) => (
                <li key={index} style={{ color: '#666' }}>{step}</li>
              ))}
              {action.steps.length > 2 && (
                <li style={{ color: '#999' }}>
                  +{action.steps.length - 2} more steps...
                </li>
              )}
            </ul>
          </div>
        )}

        {/* Compact mode action buttons */}
        {compact && (
          <Space>
            <Button 
              size="small" 
              type="primary" 
              icon={getActionIcon(action.title)}
              onClick={() => onExecute?.(action.id)}
            >
              Execute
            </Button>
            <Button 
              size="small"
              onClick={() => onViewDetails?.(action.id)}
            >
              Details
            </Button>
          </Space>
        )}
      </Space>
    </Card>
  );
};

export default ActionCard; 