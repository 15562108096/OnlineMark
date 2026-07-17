import React, { useEffect, useState } from "react";
import { Card, Table, Button, Space, Tag, Modal, Input, Select, message, Popconfirm, Form, Switch } from "antd";
import { PlusOutlined, DeleteOutlined, UserOutlined, LockOutlined } from "@ant-design/icons";
import { userApi } from "../services/api";
import { useAuth } from "../store/AuthContext";
import { User } from "../types";

const UserManagementPage: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newUser, setNewUser] = useState({ username: "", password: "", real_name: "", role: "student", email: "", phone: "" });

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try { const res = await userApi.list(); setUsers(res.data); } finally { setLoading(false); }
  };

  const handleCreate = async () => {
    if (!newUser.username || !newUser.password) { message.error("请填写账号密码"); return; }
    try {
      await userApi.create(newUser);
      message.success("创建成功");
      setCreateModalOpen(false);
      setNewUser({ username: "", password: "", real_name: "", role: "student", email: "", phone: "" });
      loadUsers();
    } catch (err: any) { message.error(err.response?.data?.detail || "创建失败"); }
  };

  const handleDelete = async (id: string) => {
    try { await userApi.delete(id); message.success("删除成功"); loadUsers(); } catch { message.error("删除失败"); }
  };

  const handleToggleActive = async (id: string) => {
    try { await userApi.toggleActive(id); loadUsers(); } catch { message.error("操作失败"); }
  };

  const roleColors: Record<string, string> = {
    super_admin: "red", admin: "orange", teacher: "blue", student: "green",
  };
  const roleLabels: Record<string, string> = {
    super_admin: "超级管理员", admin: "管理员", teacher: "教师", student: "学生",
  };

  const columns = [
    { title: "账号", dataIndex: "username", key: "username" },
    { title: "姓名", dataIndex: "real_name", key: "real_name", render: (v: string) => v || "--" },
    { title: "角色", dataIndex: "role", key: "role",
      render: (r: string) => <Tag color={roleColors[r]}>{roleLabels[r] || r}</Tag>
    },
    { title: "邮箱", dataIndex: "email", key: "email", render: (v: string) => v || "--" },
    { title: "手机", dataIndex: "phone", key: "phone", render: (v: string) => v || "--" },
    { title: "状态", dataIndex: "is_active", key: "is_active",
      render: (active: boolean, record: User) => (
        <Switch checked={active} size="small" disabled={record.role === "super_admin"}
          onChange={() => handleToggleActive(record.id)} />
      )
    },
    { title: "操作", key: "action", render: (_: any, record: User) => (
      record.role !== "super_admin" ? (
        <Popconfirm title="确定删除此用户？" onConfirm={() => handleDelete(record.id)}>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
        </Popconfirm>
      ) : <Tag>不可操作</Tag>
    )},
  ];

  return (
    <div>
      <Card title="用户管理" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>创建用户</Button>}
        style={{ borderRadius: 12 }}>
        <Table dataSource={users} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 15 }} />
      </Card>

      <Modal title="创建用户" open={createModalOpen} onOk={handleCreate} onCancel={() => setCreateModalOpen(false)}>
        <Form layout="vertical">
          <Form.Item label="账号" required>
            <Input prefix={<UserOutlined />} value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })} />
          </Form.Item>
          <Form.Item label="密码" required>
            <Input.Password prefix={<LockOutlined />} value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} />
          </Form.Item>
          <Form.Item label="姓名">
            <Input value={newUser.real_name} onChange={(e) => setNewUser({ ...newUser, real_name: e.target.value })} />
          </Form.Item>
          <Form.Item label="角色">
            <Select value={newUser.role} onChange={(v) => setNewUser({ ...newUser, role: v })}
              disabled={user?.role !== "super_admin"}>
              {user?.role === "super_admin" && <Select.Option value="admin">管理员</Select.Option>}
              <Select.Option value="teacher">教师</Select.Option>
              <Select.Option value="student">学生</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="邮箱">
            <Input value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
          </Form.Item>
          <Form.Item label="手机">
            <Input value={newUser.phone} onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagementPage;
