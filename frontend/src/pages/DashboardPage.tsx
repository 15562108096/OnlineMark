import React, { useEffect, useState } from "react";
import { Card, Row, Col, Statistic, Table, Tag } from "antd";
import {
  FileTextOutlined,
  ScanOutlined,
  AuditOutlined,
  BarChartOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../store/AuthContext";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const statsCards = [
    { key: "templates", icon: <FileTextOutlined />, color: "#1677ff", bg: "#e6f4ff", label: "答题卡模板", value: "--", path: "/templates" },
    { key: "scan", icon: <ScanOutlined />, color: "#52c41a", bg: "#f6ffed", label: "扫描批次", value: "--", path: "/scan" },
    { key: "grading", icon: <AuditOutlined />, color: "#fa8c16", bg: "#fff7e6", label: "评卷任务", value: "--", path: "/grading" },
    { key: "scores", icon: <BarChartOutlined />, color: "#9c27b0", bg: "#f9f0ff", label: "成绩数据", value: "--", path: "/scores" },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, fontWeight: 600, margin: 0 }}>
          欢迎回来，{user?.real_name || user?.username}
        </h2>
        <p style={{ color: "#999", margin: "8px 0 0" }}>
          {user?.role === "super_admin" ? "超级管理员" :
           user?.role === "admin" ? "管理员" :
           user?.role === "teacher" ? "教师" : "学生"}
          {user?.role === "teacher" ? " - 您可以评阅分配的题目" : ""}
        </p>
      </div>

      <Row gutter={[16, 16]}>
        {statsCards.map((card) => (
          <Col span={6} key={card.key}>
            <Card
              hoverable
              onClick={() => navigate(card.path)}
              style={{ borderRadius: 12 }}
              bodyStyle={{ padding: 24 }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: card.bg,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 24,
                    color: card.color,
                  }}
                >
                  {card.icon}
                </div>
                <div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: "#1f1f1f" }}>
                    {card.value}
                  </div>
                  <div style={{ fontSize: 14, color: "#999" }}>{card.label}</div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Card title="快速操作" style={{ marginTop: 24, borderRadius: 12 }}>
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Card
              hoverable
              size="small"
              onClick={() => navigate("/templates/new")}
              style={{ borderRadius: 8, textAlign: "center", cursor: "pointer" }}
            >
              <FileTextOutlined style={{ fontSize: 24, color: "#1677ff" }} />
              <div style={{ marginTop: 8 }}>创建新模板</div>
            </Card>
          </Col>
          <Col span={6}>
            <Card
              hoverable
              size="small"
              onClick={() => navigate("/scan")}
              style={{ borderRadius: 8, textAlign: "center", cursor: "pointer" }}
            >
              <ScanOutlined style={{ fontSize: 24, color: "#52c41a" }} />
              <div style={{ marginTop: 8 }}>新建扫描批次</div>
            </Card>
          </Col>
          <Col span={6}>
            <Card
              hoverable
              size="small"
              onClick={() => navigate("/grading")}
              style={{ borderRadius: 8, textAlign: "center", cursor: "pointer" }}
            >
              <AuditOutlined style={{ fontSize: 24, color: "#fa8c16" }} />
              <div style={{ marginTop: 8 }}>开始评卷</div>
            </Card>
          </Col>
          <Col span={6}>
            <Card
              hoverable
              size="small"
              onClick={() => navigate("/scores")}
              style={{ borderRadius: 8, textAlign: "center", cursor: "pointer" }}
            >
              <BarChartOutlined style={{ fontSize: 24, color: "#9c27b0" }} />
              <div style={{ marginTop: 8 }}>查看成绩</div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default DashboardPage;
