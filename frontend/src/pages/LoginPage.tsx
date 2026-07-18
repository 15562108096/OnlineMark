import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Input, message, Form } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useAuth } from "../store/AuthContext";

const roles = [
  { key: "admin", label: "管理员" },
  { key: "teacher", label: "教师" },
  { key: "student", label: "学生" },
];

const LoginPage: React.FC = () => {
  const [role, setRole] = useState("admin");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password, role);
      message.success("欢迎回来！");
      navigate("/");
    } catch (err: any) {
      message.error(err.response?.data?.detail || "登录失败，请检查账号密码和身份");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>云教学服务平台</h1>
        <p>Online Marking System</p>

        <div className="role-selector">
          {roles.map((r) => (
            <div
              key={r.key}
              className={"role-btn " + (role === r.key ? "active" : "")}
              onClick={() => setRole(r.key)}
            >
              {r.label}
            </div>
          ))}
        </div>

        <Form onFinish={handleSubmit} layout="vertical" size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: "请输入账号" }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入账号" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登 录
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default LoginPage;
