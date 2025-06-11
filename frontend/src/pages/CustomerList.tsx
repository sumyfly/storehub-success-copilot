import React, { useState } from 'react';
import {
  Table,
  Tag,
  Progress,
  Button,
  Modal,
  Descriptions,
  Typography,
  Space,
  Avatar,
  Card,
  Row,
  Col,
  Statistic,
  Tooltip,
  Input,
  Select,
  Spin,
} from 'antd';
import {
  EyeOutlined,
  UserOutlined,
  DollarOutlined,
  PhoneOutlined,
  TrophyOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { apiService, Customer, CustomerHealth } from '../services/api';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

const CustomerList: React.FC = () => {
  const [selectedCustomer, setSelectedCustomer] = useState<number | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [filterRisk, setFilterRisk] = useState<string>('all');

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
    if (score >= 0.8) return { label: 'Excellent', color: 'green' };
    if (score >= 0.6) return { label: 'Good', color: 'blue' };
    if (score >= 0.3) return { label: 'At Risk', color: 'orange' };
    return { label: 'Critical', color: 'red' };
  };

  const getPaymentStatusColor = (status?: string) => {
    switch (status) {
      case 'current': return 'green';
      case 'late': return 'orange';
      case 'overdue': return 'red';
      default: return 'blue';
    }
  };

  // Filter customers based on search and risk level
  const filteredCustomers = customers?.filter(customer => {
    const matchesSearch = customer.name.toLowerCase().includes(searchText.toLowerCase()) ||
                         (customer.customer_label || '').toLowerCase().includes(searchText.toLowerCase());
    
    if (filterRisk === 'all') return matchesSearch;
    
    const riskLevel = getRiskLevel(customer.health_score).label.toLowerCase();
    return matchesSearch && riskLevel === filterRisk.toLowerCase();
  });

  const columns: ColumnsType<Customer> = [
    {
      title: 'Customer',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Customer) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <div>
            <Text strong>{name}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.customer_type}
            </Text>
          </div>
        </Space>
      ),
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Label',
      dataIndex: 'customer_label',
      key: 'customer_label',
      render: (label: string) => <Tag color="blue">{label}</Tag>,
      filters: [
        { text: 'Enterprise', value: 'Enterprise' },
        { text: 'Growth', value: 'Growth' },
        { text: 'Startup', value: 'Startup' },
      ],
      onFilter: (value, record) => record.customer_label === value,
    },
    {
      title: 'Health Score',
      dataIndex: 'health_score',
      key: 'health_score',
      render: (score: number) => {
        const percentage = Math.round(score * 100);
        const riskLevel = getRiskLevel(score);
        return (
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Progress
              percent={percentage}
              status={percentage >= 70 ? 'success' : percentage >= 30 ? 'normal' : 'exception'}
              size="small"
              format={(percent) => `${percent}%`}
            />
            <Tag color={riskLevel.color}>{riskLevel.label}</Tag>
          </Space>
        );
      },
      sorter: (a, b) => a.health_score - b.health_score,
      defaultSortOrder: 'ascend',
    },
    {
      title: 'MRR',
      dataIndex: 'mrr',
      key: 'mrr',
      render: (mrr: number) => (
        <Text strong style={{ color: '#52c41a' }}>
          ${mrr.toLocaleString()}
        </Text>
      ),
      sorter: (a, b) => a.mrr - b.mrr,
    },
    {
      title: 'Payment Status',
      dataIndex: 'payment_status',
      key: 'payment_status',
      render: (status: string = 'current') => (
        <Tag color={getPaymentStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'Current', value: 'current' },
        { text: 'Late', value: 'late' },
        { text: 'Overdue', value: 'overdue' },
      ],
      onFilter: (value, record) => (record.payment_status || 'current') === value,
    },
    {
      title: 'Support Tickets',
      dataIndex: 'support_tickets',
      key: 'support_tickets',
      render: (tickets: number) => (
        <Tag color={tickets > 5 ? 'red' : tickets > 2 ? 'orange' : 'green'}>
          {tickets}
        </Tag>
      ),
      sorter: (a, b) => a.support_tickets - b.support_tickets,
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
      sorter: (a, b) => a.last_login_days - b.last_login_days,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record: Customer) => (
        <Tooltip title="View detailed health report">
          <Button
            type="primary"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => handleViewDetails(record.id)}
          >
            Details
          </Button>
        </Tooltip>
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

  const selectedCustomerData = customers?.find(c => c.id === selectedCustomer);

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Customer Health Overview
      </Title>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Customers"
              value={customers?.length || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Healthy Customers"
              value={customers?.filter(c => c.health_score >= 0.7).length || 0}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="At Risk"
              value={customers?.filter(c => c.health_score < 0.6).length || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total MRR"
              value={customers?.reduce((sum, c) => sum + c.mrr, 0) || 0}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
              formatter={(value) => `$${Number(value).toLocaleString()}`}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters and Search */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12}>
            <Search
              placeholder="Search customers..."
              allowClear
              enterButton={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Select
              placeholder="Filter by risk level"
              value={filterRisk}
              onChange={setFilterRisk}
              style={{ width: '100%' }}
            >
              <Option value="all">All Risk Levels</Option>
              <Option value="excellent">Excellent</Option>
              <Option value="good">Good</Option>
              <Option value="at risk">At Risk</Option>
              <Option value="critical">Critical</Option>
            </Select>
          </Col>
          <Col xs={24} sm={6}>
            <Text type="secondary">
              Showing {filteredCustomers?.length || 0} of {customers?.length || 0} customers
            </Text>
          </Col>
        </Row>
      </Card>

      {/* Customer Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredCustomers}
          rowKey="id"
          pagination={{
            total: filteredCustomers?.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} customers`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* Customer Details Modal */}
      <Modal
        title={
          <Space>
            <Avatar icon={<UserOutlined />} />
            <span>{selectedCustomerData?.name} - Health Details</span>
          </Space>
        }
        open={detailsOpen}
        onCancel={handleCloseDetails}
        footer={[
          <Button key="close" onClick={handleCloseDetails}>
            Close
          </Button>,
          <Button key="contact" type="primary" icon={<PhoneOutlined />}>
            Contact Customer
          </Button>,
        ]}
        width={800}
      >
        {selectedCustomerData && (
          <div>
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="Health Score"
                    value={Math.round(selectedCustomerData.health_score * 100)}
                    suffix="%"
                    valueStyle={{
                      color: selectedCustomerData.health_score >= 0.7 ? '#52c41a' : 
                             selectedCustomerData.health_score >= 0.3 ? '#faad14' : '#ff4d4f'
                    }}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="Monthly Revenue"
                    value={selectedCustomerData.mrr}
                    prefix="$"
                    formatter={(value) => Number(value).toLocaleString()}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="Support Tickets"
                    value={selectedCustomerData.support_tickets}
                    valueStyle={{
                      color: selectedCustomerData.support_tickets > 5 ? '#ff4d4f' : 
                             selectedCustomerData.support_tickets > 2 ? '#faad14' : '#52c41a'
                    }}
                  />
                </Card>
              </Col>
            </Row>

            <Descriptions bordered column={2}>
              <Descriptions.Item label="Customer Type" span={1}>
                <Tag color="blue">{selectedCustomerData.customer_type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Customer Label" span={1}>
                <Tag color="green">{selectedCustomerData.customer_label}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Payment Status" span={1}>
                <Tag color={getPaymentStatusColor(selectedCustomerData.payment_status)}>
                  {(selectedCustomerData.payment_status || 'current').toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Last Login" span={1}>
                <Tag color={selectedCustomerData.last_login_days > 14 ? 'red' : 
                           selectedCustomerData.last_login_days > 7 ? 'orange' : 'green'}>
                  {selectedCustomerData.last_login_days} days ago
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Usage Score" span={1}>
                <Progress
                  percent={Math.round(selectedCustomerData.usage_score * 100)}
                  size="small"
                  status={selectedCustomerData.usage_score >= 0.6 ? 'success' : 
                          selectedCustomerData.usage_score >= 0.3 ? 'normal' : 'exception'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="Risk Level" span={1}>
                <Tag color={getRiskLevel(selectedCustomerData.health_score).color}>
                  {getRiskLevel(selectedCustomerData.health_score).label}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            {customerHealth && (
              <Card title="Health Breakdown" style={{ marginTop: 16 }}>
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Text strong>Usage Score: </Text>
                    <Progress
                      percent={Math.round(customerHealth.factors.usage_score * 100)}
                      size="small"
                      format={(percent) => `${percent}%`}
                    />
                  </Col>
                  <Col span={12}>
                    <Text strong>Engagement Score: </Text>
                    <Progress
                      percent={Math.round(customerHealth.factors.engagement_score * 100)}
                      size="small"
                      format={(percent) => `${percent}%`}
                    />
                  </Col>
                  <Col span={12}>
                    <Text strong>NPS Score: </Text>
                    <Progress
                      percent={customerHealth.factors.nps_score ? (customerHealth.factors.nps_score + 100) / 2 : 50}
                      size="small"
                      format={(percent) => `${customerHealth.factors.nps_score || 0}`}
                    />
                  </Col>
                  <Col span={12}>
                    <Text strong>Support Tickets: </Text>
                    <Tag color={customerHealth.factors.support_tickets > 5 ? 'red' : 
                              customerHealth.factors.support_tickets > 2 ? 'orange' : 'green'}>
                      {customerHealth.factors.support_tickets}
                    </Tag>
                  </Col>
                </Row>
              </Card>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default CustomerList; 