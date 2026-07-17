import React, { useEffect, useState } from "react";
import { Card, Table, Button, Space, Tag, Modal, Select, message, Statistic, Row, Col, Empty, Descriptions } from "antd";
import { BarChartOutlined, DownloadOutlined, CalculatorOutlined, EyeOutlined } from "@ant-design/icons";
import { scoreApi, scanApi } from "../services/api";

const ScoresPage: React.FC = () => {
  const [batches, setBatches] = useState<any[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<string>("");
  const [scores, setScores] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);

  useEffect(() => { loadBatches(); }, []);

  const loadBatches = async () => {
    try { const res = await scanApi.listBatches(); setBatches(res.data); } catch {}
  };

  const loadScores = async (batchId: string) => {
    if (!batchId) return;
    setLoading(true);
    try {
      const res = await scoreApi.getBatchScores(batchId);
      setScores(res.data);
    } catch { message.error("获取成绩失败"); }
    finally { setLoading(false); }
  };

  const loadStats = async (batchId: string) => {
    if (!batchId) return;
    setStatsLoading(true);
    try {
      const res = await scoreApi.getStatistics(batchId);
      setStatistics(res.data);
    } catch { setStatistics(null); }
    finally { setStatsLoading(false); }
  };

  const handleBatchChange = (batchId: string) => {
    setSelectedBatch(batchId);
    loadScores(batchId);
    loadStats(batchId);
  };

  const handleCalculate = async () => {
    if (!selectedBatch) { message.error("请选择批次"); return; }
    try {
      await scoreApi.calculate(selectedBatch);
      message.success("成绩计算完成");
      loadScores(selectedBatch);
      loadStats(selectedBatch);
    } catch { message.error("计算失败"); }
  };

  const handleExport = async () => {
    if (!selectedBatch) { message.error("请选择批次"); return; }
    try {
      const res = await scoreApi.export(selectedBatch);
      const csvContent = res.data.csv;
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = res.data.filename || `scores_${selectedBatch}.csv`;
      a.click();
      message.success("导出成功");
    } catch { message.error("导出失败"); }
  };

  const columns = [
    { title: "排名", dataIndex: "rank", key: "rank", width: 80 },
    { title: "考号", dataIndex: "student_id", key: "student_id", render: (v: string) => v || "--" },
    { title: "姓名", dataIndex: "student_name", key: "student_name", render: (v: string) => v || "--" },
    { title: "客观题", dataIndex: "objective_score", key: "objective_score",
      render: (v: number) => <span style={{ color: "#1677ff", fontWeight: 600 }}>{v.toFixed(1)}</span>
    },
    { title: "主观题", dataIndex: "subjective_score", key: "subjective_score",
      render: (v: number) => <span style={{ color: "#fa8c16", fontWeight: 600 }}>{v.toFixed(1)}</span>
    },
    { title: "总分", dataIndex: "total_score", key: "total_score",
      render: (v: number) => <span style={{ fontWeight: 700, fontSize: 16 }}>{v.toFixed(1)}</span>
    },
    { title: "满分", dataIndex: "full_score", key: "full_score", render: (v: number) => v || "--" },
  ];

  return (
    <div>
      <Card title="成绩管理" style={{ borderRadius: 12 }}>
        <Space style={{ marginBottom: 16 }}>
          <Select placeholder="选择批次" value={selectedBatch || undefined} onChange={handleBatchChange} style={{ width: 300 }}>
            {batches.map((b) => <Select.Option key={b.id} value={b.id}>{b.name}</Select.Option>)}
          </Select>
          <Button icon={<CalculatorOutlined />} onClick={handleCalculate}>计算成绩</Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport} disabled={!selectedBatch}>导出Excel</Button>
        </Space>

        {statistics && (
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={4}><Card size="small"><Statistic title="总人数" value={statistics.total_students} /></Card></Col>
            <Col span={4}><Card size="small"><Statistic title="平均分" value={statistics.average} precision={1} /></Card></Col>
            <Col span={4}><Card size="small"><Statistic title="最高分" value={statistics.max_score} valueStyle={{ color: "#52c41a" }} /></Card></Col>
            <Col span={4}><Card size="small"><Statistic title="最低分" value={statistics.min_score} valueStyle={{ color: "#ff4d4f" }} /></Card></Col>
            <Col span={4}><Card size="small"><Statistic title="及格人数" value={statistics.pass_count} suffix={`/ ${statistics.total_students}`} /></Card></Col>
            <Col span={4}><Card size="small"><Statistic title="及格率" value={statistics.pass_rate} suffix="%" precision={1} /></Card></Col>
          </Row>
        )}

        <Table dataSource={scores} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 20 }}
          summary={() => scores.length > 0 ? (
            <Table.Summary.Row>
              <Table.Summary.Cell index={0}>合计</Table.Summary.Cell>
              <Table.Summary.Cell index={1}></Table.Summary.Cell>
              <Table.Summary.Cell index={2}></Table.Summary.Cell>
              <Table.Summary.Cell index={3}>
                {scores.reduce((s, r) => s + (r.objective_score || 0), 0).toFixed(1)}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={4}>
                {scores.reduce((s, r) => s + (r.subjective_score || 0), 0).toFixed(1)}
              </Table.Summary.Cell>
              <Table.Summary.Cell index={5}>
                <strong>{scores.reduce((s, r) => s + (r.total_score || 0), 0).toFixed(1)}</strong>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={6}></Table.Summary.Cell>
            </Table.Summary.Row>
          ) : null
        } />
      </Card>
    </div>
  );
};

export default ScoresPage;
