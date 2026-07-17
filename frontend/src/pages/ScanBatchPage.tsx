import React, { useEffect, useState } from "react";
import { Card, Table, Button, Space, Tag, Modal, Upload, message, Select, Input, Progress, Statistic, Row, Col } from "antd";
import { PlusOutlined, UploadOutlined, PlayCircleOutlined, EyeOutlined, InboxOutlined } from "@ant-design/icons";
import { scanApi, templateApi } from "../services/api";
import { ScanBatch, Template } from "../types";
import dayjs from "dayjs";

const { Dragger } = Upload;

const ScanBatchPage: React.FC = () => {
  const [batches, setBatches] = useState<any[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<any>(null);
  const [batchDetail, setBatchDetail] = useState<any>(null);
  const [newBatch, setNewBatch] = useState({ name: "", template_id: "", exam_name: "" });
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [recognizing, setRecognizing] = useState(false);

  useEffect(() => {
    loadData();
    loadTemplates();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await scanApi.listBatches();
      setBatches(res.data);
    } finally { setLoading(false); }
  };

  const loadTemplates = async () => {
    try {
      const res = await templateApi.list();
      setTemplates(res.data);
    } catch {}
  };

  const handleCreate = async () => {
    if (!newBatch.name || !newBatch.template_id) { message.error("请填写完整信息"); return; }
    try {
      await scanApi.createBatch(newBatch);
      message.success("批次创建成功");
      setCreateModalOpen(false);
      setNewBatch({ name: "", template_id: "", exam_name: "" });
      loadData();
    } catch { message.error("创建失败"); }
  };

  const handleUpload = async () => {
    if (!selectedBatch || uploadFiles.length === 0) { message.error("请选择文件"); return; }
    try {
      await scanApi.uploadSheets(selectedBatch.id, uploadFiles);
      message.success("上传成功");
      setUploadModalOpen(false);
      setUploadFiles([]);
      loadData();
    } catch { message.error("上传失败"); }
  };

  const handleRecognize = async (batchId: string) => {
    setRecognizing(true);
    try {
      const res = await scanApi.recognize(batchId);
      message.success(res.data.message || "识别完成");
      loadData();
    } catch { message.error("识别失败"); }
    finally { setRecognizing(false); }
  };

  const handleViewDetail = async (batch: any) => {
    setSelectedBatch(batch);
    try {
      const res = await scanApi.getBatch(batch.id);
      setBatchDetail(res.data);
      setDetailModalOpen(true);
    } catch { message.error("获取详情失败"); }
  };

  const columns = [
    { title: "批次名称", dataIndex: "name", key: "name" },
    { title: "考试", dataIndex: "exam_name", key: "exam_name", render: (v: string) => v || "--" },
    { title: "总数", dataIndex: "total", key: "total" },
    { title: "已识别", dataIndex: "processed", key: "processed",
      render: (v: number, r: any) => r.total > 0 ? `${v}/${r.total}` : "--"
    },
    { title: "失败", dataIndex: "failed", key: "failed",
      render: (v: number) => v > 0 ? <span style={{ color: "#ff4d4f" }}>{v}</span> : v
    },
    { title: "状态", dataIndex: "status", key: "status",
      render: (s: string) => {
        const map: Record<string, { color: string; text: string }> = {
          pending: { color: "default", text: "待识别" },
          processing: { color: "processing", text: "识别中" },
          completed: { color: "success", text: "已完成" },
        };
        return <Tag color={(map[s] || {}).color}>{map[s]?.text || s}</Tag>;
      }
    },
    { title: "创建时间", dataIndex: "created_at", key: "created_at",
      render: (v: string) => v ? dayjs(v).format("MM-DD HH:mm") : "--"
    },
    { title: "操作", key: "action", render: (_: any, r: any) => (
      <Space>
        <Button size="small" icon={<UploadOutlined />} onClick={() => { setSelectedBatch(r); setUploadModalOpen(true); }}>上传</Button>
        <Button size="small" icon={<PlayCircleOutlined />} loading={recognizing} onClick={() => handleRecognize(r.id)}>识别</Button>
        <Button size="small" icon={<EyeOutlined />} onClick={() => handleViewDetail(r)}>详情</Button>
      </Space>
    )},
  ];

  return (
    <div>
      <Card title="扫描批次" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>新建批次</Button>}
        style={{ borderRadius: 12 }}>
        <Table dataSource={batches} columns={columns} rowKey="id" loading={loading} pagination={false} />
      </Card>

      <Modal title="新建批次" open={createModalOpen} onOk={handleCreate} onCancel={() => setCreateModalOpen(false)}>
        <Space direction="vertical" style={{ width: "100%" }}>
          <Input placeholder="批次名称" value={newBatch.name} onChange={(e) => setNewBatch({ ...newBatch, name: e.target.value })} />
          <Select placeholder="选择模板" value={newBatch.template_id || undefined} onChange={(v) => setNewBatch({ ...newBatch, template_id: v })}
            style={{ width: "100%" }}>
            {templates.map((t) => <Select.Option key={t.id} value={t.id}>{t.name}</Select.Option>)}
          </Select>
          <Input placeholder="考试名称（可选）" value={newBatch.exam_name} onChange={(e) => setNewBatch({ ...newBatch, exam_name: e.target.value })} />
        </Space>
      </Modal>

      <Modal title="上传答题卡" open={uploadModalOpen} onOk={handleUpload} onCancel={() => { setUploadModalOpen(false); setUploadFiles([]); }}
        okText="开始上传">
        <Dragger multiple accept="image/*" beforeUpload={(file) => {
          setUploadFiles((prev) => [...prev, file]);
          return false;
        }}>
          <p className="ant-upload-drag-icon"><InboxOutlined /></p>
          <p>点击或拖拽答题卡图片到此处</p>
          <p style={{ color: "#999", fontSize: 12 }}>支持 JPG / PNG / TIFF，建议分辨率300dpi以上</p>
        </Dragger>
        {uploadFiles.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <p>已选择 {uploadFiles.length} 个文件</p>
            {uploadFiles.map((f, i) => <div key={i} style={{ fontSize: 12, color: "#666" }}>{f.name}</div>)}
          </div>
        )}
      </Modal>

      <Modal title="批次详情" open={detailModalOpen} onCancel={() => setDetailModalOpen(false)} width={800} footer={null}>
        {batchDetail && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}><Statistic title="总数" value={batchDetail.batch.total} /></Col>
              <Col span={6}><Statistic title="已识别" value={batchDetail.batch.processed} /></Col>
              <Col span={6}><Statistic title="失败" value={batchDetail.batch.status === "failed" ? 1 : 0} /></Col>
              <Col span={6}><Statistic title="状态" value={batchDetail.batch.status === "completed" ? "完成" : "进行中"} /></Col>
            </Row>
            <Table dataSource={batchDetail.sheets} rowKey="id" pagination={false} size="small"
              columns={[
                { title: "文件名", dataIndex: "filename", key: "filename" },
                { title: "考号", dataIndex: "student_id", key: "student_id", render: (v: string) => v || "--" },
                { title: "姓名", dataIndex: "student_name", key: "student_name", render: (v: string) => v || "--" },
                { title: "状态", dataIndex: "status", key: "status",
                  render: (s: string) => {
                    const colors: Record<string, string> = { completed: "green", pending: "default", processing: "blue", failed: "red" };
                    const labels: Record<string, string> = { completed: "成功", pending: "待处理", processing: "处理中", failed: "失败" };
                    return <Tag color={colors[s] || "default"}>{labels[s] || s}</Tag>;
                  }
                },
                { title: "错误信息", dataIndex: "error_message", key: "error_message", render: (v: string) => v || "--" },
              ]}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ScanBatchPage;
