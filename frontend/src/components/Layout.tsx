import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Badge, Space, Typography } from 'antd';
import {
  DashboardOutlined,
  TeamOutlined,
  AlertOutlined,
  ThunderboltOutlined,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;

interface Props {
  children: React.ReactNode;
}

interface NavigationItem {
  key: string;
  icon: React.ReactElement;
  label: string;
  path: string;
}

const navigationItems: NavigationItem[] = [
  { key: 'dashboard', icon: <DashboardOutlined />, label: 'Dashboard', path: '/' },
  { key: 'customers', icon: <TeamOutlined />, label: 'Customers', path: '/customers' },
  { key: 'alerts', icon: <AlertOutlined />, label: 'Alerts', path: '/alerts' },
  { key: 'actions', icon: <ThunderboltOutlined />, label: 'Actions', path: '/actions' },
];

export default function Layout({ children }: Props) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Get current selected key based on path
  const getCurrentKey = () => {
    const currentItem = navigationItems.find(item => item.path === location.pathname);
    return currentItem ? currentItem.key : 'dashboard';
  };

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    const item = navigationItems.find(nav => nav.key === e.key);
    if (item) {
      navigate(item.path);
    }
  };

  // User dropdown menu
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div 
          style={{ 
            height: 32, 
            margin: 16, 
            textAlign: 'center',
            color: '#fff',
            fontSize: collapsed ? 14 : 18,
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {collapsed ? 'CS' : 'CS Copilot'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getCurrentKey()]}
          items={navigationItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label,
          }))}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <AntLayout style={{ marginLeft: collapsed ? 80 : 200, transition: 'margin-left 0.2s' }}>
        <Header 
          style={{ 
            padding: '0 24px', 
            background: '#fff', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
            position: 'sticky',
            top: 0,
            zIndex: 1,
          }}
        >
          <Space align="center">
            <div
              style={{ fontSize: 18, cursor: 'pointer' }}
              onClick={() => setCollapsed(!collapsed)}
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </div>
            <Title level={4} style={{ margin: 0, color: '#001529' }}>
              Customer Success Copilot
            </Title>
          </Space>
          
          <Space align="center" size="middle">
            <Badge count={5} size="small">
              <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
            </Badge>
            
            <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
              <Space style={{ cursor: 'pointer' }}>
                <Avatar size="small" icon={<UserOutlined />} />
                <span>Admin User</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content 
          style={{ 
            margin: '24px 24px 0', 
            overflow: 'initial',
            minHeight: 'calc(100vh - 112px)',
          }}
        >
          <div style={{ padding: 24, background: '#fff', borderRadius: 6 }}>
            {children}
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  );
} 