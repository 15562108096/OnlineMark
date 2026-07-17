import React, { useEffect, useState } from "react";
import { Table, Button, Card, Space, Tag, Modal, message, Popconfirm } from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, ExportOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { templateApi } from "../services/api";
import { Template } from "../types";
import dayjs from "dayjs";

const TemplateListPage: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const res = await templateApi.list();
      setTemplates(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTemplates(); }, []);

  const handleDelete = async (id: string) => {
    try {
      await templateApi.delete(id);
      message.success("删除成功");
      loadTemplates();
    } catch { message.error("删除失败"); }
  };

  const columns = [
    { title: "模板名称", dataIndex: "name", key: "name", render: (t: string, r: Template) => <a onClick={() => navigate(`/templates/${r.id}/edit`)}>{t}</a> },
    { title: "科目", dataIndex: "subject", key: "subject", render: (v: string) => v || "--" },
    { title: "年级", dataIndex: "grade", key: "grade", render: (v: string) => v || "--" },
    { title: "总分", dataIndex: "total_score", key: "total_score", render: (v: number) => v || 0 },
    { title: "状态", dataIndex: "status", key: "status", render: (s: string) => {
      const map: Record<string, { color: string; text: string }> = {
        draft: { color: "default", text: "草稿" },
        active: { color: "green", text: "已启用" },
        archived: { color: "orange", text: "已归档" },
      };
      const info = map[s] || { color: "default", text: s };
      return <Tag color={info.color}>{info.text}</Tag>;
    }},
    { title: "创建时间", dataIndex: "created_at", key: "created_at", render: (v: string) => v ? dayjs(v).format("YYYY-MM-DD HH:mm") : "--" },
    { title: "操作", key: "action", render: (_: any, r: Template) => (
      <Space>
        <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => navigate(`/templates/${r.id}/edit`)}>编辑</Button>
        <Button type="link" size="small" icon={<ExportOutlined />} onClick={async () => {
          try {
            const res = await templateApi.export(r.id);
            const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a"); a.href = url; a.download = `${r.name}.json`; a.click();
          } catch { message.error("导出失败"); }
        }}>导出</Button>
        <Popconfirm title="确定删除此模板？" onConfirm={() => handleDelete(r.id)}>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
        </Popconfirm>
      </Space>
    )},
  ];

  return (
    <div>
      <Card
        title="答题卡模板"
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/templates/new")}>新建模板</Button>}
        style={{ borderRadius: 12 }}
      >
        <Table dataSource={templates} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
};

export default TemplateListPage;
