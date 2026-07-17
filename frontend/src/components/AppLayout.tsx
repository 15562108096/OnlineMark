import React from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Button, Dropdown, Avatar, Space } from "antd";
import {
  DashboardOutlined,
  FileTextOutlined,
  ScanOutlined,
  AuditOutlined,
  BarChartOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useAuth } from "../store/AuthContext";

const { Header, Content, Footer, Sider } = Layout;

const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: "/", icon: <DashboardOutlined />, label: "工作台" },
    { key: "/templates", icon: <FileTextOutlined />, label: "模板管理" },
    { key: "/scan", icon: <ScanOutlined />, label: "扫描识别" },
    { key: "/grading", icon: <AuditOutlined />, label: "评卷管理" },
    { key: "/scores", icon: <BarChartOutlined />, label: "成绩管理" },
  ];

  if (user?.role === "super_admin" || user?.role === "admin") {
    menuItems.push({ key: "/users", icon: <UserOutlined />, label: "用户管理" });
  }

  const selectedKey = "/" + location.pathname.split("/").filter(Boolean)[0];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        width={220}
        style={{
          background: "#fff",
          borderRight: "1px solid #f0f0f0",
          position: "fixed",
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            height: 56,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderBottom: "1px solid #f0f0f0",
            cursor: "pointer",
          }}
          onClick={() => navigate("/")}
        >
          <span style={{ fontSize: 20, fontWeight: 700, color: "#1677ff" }}>云教学</span>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0, marginTop: 8 }}
        />
      </Sider>
      <Layout style={{ marginLeft: 220 }}>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            borderBottom: "1px solid #f0f0f0",
            height: 56,
            position: "sticky",
            top: 0,
            zIndex: 9,
          }}
        >
          <Space>
            <span style={{ color: "#999" }}>
              {user?.role === "super_admin" ? "超级管理员" :
               user?.role === "admin" ? "管理员" :
               user?.role === "teacher" ? "教师" : "学生"}
            </span>
            <Dropdown
              menu={{
                items: [
                  { key: "profile", icon: <UserOutlined />, label: `${user?.real_name || user?.username}` },
                  { type: "divider" },
                  { key: "logout", icon: <LogoutOutlined />, label: "退出登录", danger: true },
                ],
                onClick: ({ key }) => {
                  if (key === "logout") {
                    logout();
                    navigate("/login");
                  }
                },
              }}
            >
              <Avatar
                size={32}
                style={{ backgroundColor: "#1677ff", cursor: "pointer" }}
                icon={<UserOutlined />}
              />
            </Dropdown>
          </Space>
        </Header>
        <Content style={{ padding: 24, minHeight: "calc(100vh - 112px)" }}>
          <Outlet />
        </Content>
        <Footer
          style={{
            textAlign: "center",
            color: "#999",
            fontSize: 13,
            padding: "12px 50px",
            background: "#f0f2f5",
          }}
        >
          云教学服务平台 &copy; {new Date().getFullYear()} - 让教学更智能
        </Footer>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
