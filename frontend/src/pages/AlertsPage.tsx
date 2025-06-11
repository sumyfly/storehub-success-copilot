import React, { useState } from 'react';
import {
  Table,
  Tag,
  Button,
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Space,
  Avatar,
  Select,
  Input,
  Badge,
  Alert,
  Spin,
  Tooltip,
  Modal,
} from 'antd';
import {
  AlertOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  SearchOutlined,
  FilterOutlined,
  BellOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { apiService, Alert as AlertType } from '../services/api';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

const AlertsPage: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  const { data: alerts, isLoading } = useQuery<AlertType[]>(
    'alerts',
    apiService.getAlerts,
    { refetchInterval: 30000 }
  );

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'green';
      default: return 'blue';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <ExclamationCircleOutlined />;
      case 'medium': return <ClockCircleOutlined />;
      case 'low': return <CheckCircleOutlined />;
      default: return <AlertOutlined />;
    }
  };

  // Filter alerts based on search and filters
  const filteredAlerts = alerts?.filter(alert => {
    const matchesSearch = 
      alert.customer_name.toLowerCase().includes(searchText.toLowerCase()) ||
      alert.message.toLowerCase().includes(searchText.toLowerCase()) ||
      alert.type.toLowerCase().includes(searchText.toLowerCase());
    
    const matchesSeverity = filterSeverity === 'all' || alert.severity === filterSeverity;
    const matchesType = filterType === 'all' || alert.type === filterType;
    
    return matchesSearch && matchesSeverity && matchesType;
  });

  // Get unique alert types for filter
  const alertTypes = [...new Set(alerts?.map(alert => alert.type) || [])];

  const columns: ColumnsType<AlertType> = [
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => (
        <Space>
          {getSeverityIcon(severity)}
          <Tag color={getSeverityColor(severity)}>
            {severity.toUpperCase()}
          </Tag>
        </Space>
      ),
      sorter: (a, b) => {
        const order = { critical: 3, medium: 2, low: 1 };
        return order[a.severity as keyof typeof order] - order[b.severity as keyof typeof order];
      },
      defaultSortOrder: 'descend',
    },
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
      sorter: (a, b) => a.customer_name.localeCompare(b.customer_name),
    },
    {
      title: 'Alert Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color="blue">
          {type.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
      filters: alertTypes.map(type => ({ text: type.replace('_', ' ').toUpperCase(), value: type })),
      onFilter: (value, record) => record.type === value,
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: {
        showTitle: false,
      },
      render: (message: string) => (
        <Tooltip placement="topLeft" title={message}>
          <Text>{message}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => (
        <Text type="secondary">
          {new Date(date).toLocaleDateString()}
        </Text>
      ),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record: AlertType) => (
        <Space>
          <Tooltip title="View Details">
            <Button size="small" icon={<AlertOutlined />}>
              View
            </Button>
          </Tooltip>
          <Tooltip title="Resolve">
            <Button size="small" type="primary">
              Resolve
            </Button>
          </Tooltip>
        </Space>
      ),
    },
  ];

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  const criticalAlerts = alerts?.filter(a => a.severity === 'critical').length || 0;
  const mediumAlerts = alerts?.filter(a => a.severity === 'medium').length || 0;
  const lowAlerts = alerts?.filter(a => a.severity === 'low').length || 0;

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        <Space>
          <BellOutlined />
          Alert Management
        </Space>
      </Title>

      {/* Alert Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Alerts"
              value={alerts?.length || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Critical Alerts"
              value={criticalAlerts}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Medium Priority"
              value={mediumAlerts}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Low Priority"
              value={lowAlerts}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Critical Alerts Banner */}
      {criticalAlerts > 0 && (
        <Alert
          message={`You have ${criticalAlerts} critical alerts requiring immediate attention`}
          type="error"
          showIcon
          action={
            <Button size="small" danger>
              Review Critical
            </Button>
          }
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Filters and Search */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Search
              placeholder="Search alerts..."
              allowClear
              enterButton={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={4}>
            <Select
              placeholder="Severity"
              value={filterSeverity}
              onChange={setFilterSeverity}
              style={{ width: '100%' }}
            >
              <Option value="all">All Severities</Option>
              <Option value="critical">Critical</Option>
              <Option value="medium">Medium</Option>
              <Option value="low">Low</Option>
            </Select>
          </Col>
          <Col xs={24} sm={4}>
            <Select
              placeholder="Type"
              value={filterType}
              onChange={setFilterType}
              style={{ width: '100%' }}
            >
              <Option value="all">All Types</Option>
              {alertTypes.map(type => (
                <Option key={type} value={type}>
                  {type.replace('_', ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={4}>
            <Button icon={<FilterOutlined />} style={{ width: '100%' }}>
              More Filters
            </Button>
          </Col>
          <Col xs={24} sm={4}>
            <Text type="secondary">
              Showing {filteredAlerts?.length || 0} of {alerts?.length || 0} alerts
            </Text>
          </Col>
        </Row>
      </Card>

      {/* Alerts Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredAlerts}
          rowKey={(record, index) => `${record.customer_id}-${index}`}
          pagination={{
            total: filteredAlerts?.length,
            pageSize: 15,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} alerts`,
          }}
          scroll={{ x: 800 }}
          rowClassName={(record) => {
            switch (record.severity) {
              case 'critical': return 'critical-row';
              case 'medium': return 'medium-row';
              default: return '';
            }
          }}
        />
      </Card>

      {/* Custom CSS for row highlighting */}
      <style>{`
        .critical-row {
          background-color: #fff2f0 !important;
          border-left: 4px solid #ff4d4f;
        }
        .medium-row {
          background-color: #fffbe6 !important;
          border-left: 4px solid #faad14;
        }
      `}</style>
    </div>
  );
};

export default AlertsPage; 