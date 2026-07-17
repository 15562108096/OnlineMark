import React, { useEffect, useState } from "react";
import { Card, Table, Button, Space, Tag, Modal, Select, message, InputNumber, Input, Divider, Progress, Tabs, List, Badge } from "antd";
import { PlusOutlined, UserAddOutlined, CheckCircleOutlined, AuditOutlined } from "@ant-design/icons";
import { gradingApi, userApi, scanApi } from "../services/api";
import { useAuth } from "../store/AuthContext";
import dayjs from "dayjs";

const GradingPage: React.FC = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [batches, setBatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [pendingGrading, setPendingGrading] = useState<any[]>([]);
  const [gradeModalOpen, setGradeModalOpen] = useState(false);
  const [currentPending, setCurrentPending] = useState<any>(null);
  const [currentImage, setCurrentImage] = useState<any>(null);
  const [gradeScore, setGradeScore] = useState<number>(0);
  const [newTask, setNewTask] = useState({ name: "", batch_id: "", template_id: "", threshold: 5.0 });
  const [assignData, setAssignData] = useState({ task_id: "", teacher_id: "", question_numbers: [] as number[] });
  const isTeacher = user?.role === "teacher";

  useEffect(() => {
    loadTasks();
    if (!isTeacher) loadTeachers();
    loadBatches();
    if (isTeacher) loadPending();
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    try { const res = await gradingApi.listTasks(); setTasks(res.data); } finally { setLoading(false); }
  };

  const loadTeachers = async () => {
    try { const res = await userApi.listTeachers(); setTeachers(res.data); } catch {}
  };

  const loadBatches = async () => {
    try { const res = await scanApi.listBatches(); setBatches(res.data); } catch {}
  };

  const loadPending = async () => {
    try { const res = await gradingApi.getPending(); setPendingGrading(res.data); } catch {}
  };

  const handleCreateTask = async () => {
    if (!newTask.name || !newTask.batch_id) { message.error("请填写完整信息"); return; }
    try {
      await gradingApi.createTask(newTask);
      message.success("任务创建成功");
      setCreateModalOpen(false);
      setNewTask({ name: "", batch_id: "", template_id: "", threshold: 5.0 });
      loadTasks();
    } catch { message.error("创建失败"); }
  };

  const handleAssign = async () => {
    if (!assignData.task_id || !assignData.teacher_id || assignData.question_numbers.length === 0) {
      message.error("请填写完整分配信息"); return;
    }
    try {
      await gradingApi.assign(assignData);
      message.success("分配成功");
      setAssignModalOpen(false);
      setAssignData({ task_id: "", teacher_id: "", question_numbers: [] });
      loadTasks();
    } catch { message.error("分配失败"); }
  };

  const handleGrade = async () => {
    if (!currentImage) { message.error("请选择待评图片"); return; }
    try {
      await gradingApi.submitGrade({
        assignment_id: currentPending.assignment_id,
        sheet_id: currentImage.sheet_id,
        subjective_image_id: currentImage.id,
        question_number: currentPending.question_number,
        score: gradeScore,
        grading_round: 1,
      });
      message.success("评分提交成功");
      setGradeModalOpen(false);
      loadPending();
    } catch { message.error("提交失败"); }
  };

  const taskColumns = [
    { title: "任务名称", dataIndex: "name", key: "name" },
    { title: "主观题数", dataIndex: "total_subjective", key: "total_subjective" },
    { title: "已评", dataIndex: "graded_count", key: "graded_count" },
    {
      title: "进度", key: "progress",
      render: (_: any, r: any) => r.total_subjective > 0
        ? <Progress percent={Math.round(r.graded_count / r.total_subjective * 100)} size="small" style={{ width: 120 }} />
        : "--"
    },
    { title: "阈值", dataIndex: "threshold", key: "threshold", render: (v: number) => `${v}分` },
    {
      title: "状态", dataIndex: "status", key: "status",
      render: (s: string) => {
        const map: Record<string, { color: string; text: string }> = {
          pending: { color: "default", text: "待分配" },
          in_progress: { color: "processing", text: "评阅中" },
          completed: { color: "success", text: "已完成" },
        };
        return <Tag color={map[s]?.color}>{map[s]?.text || s}</Tag>;
      }
    },
    { title: "创建时间", dataIndex: "created_at", key: "created_at",
      render: (v: string) => v ? dayjs(v).format("MM-DD HH:mm") : "--"
    },
    ...(isTeacher ? [] : [{
      title: "操作", key: "action", render: (_: any, r: any) => (
        <Button size="small" icon={<UserAddOutlined />} onClick={() => {
          setAssignData({ ...assignData, task_id: r.id });
          setAssignModalOpen(true);
        }}>分配教师</Button>
      )
    }]),
  ];

  return (
    <div>
      <Card title="评卷管理" extra={!isTeacher && <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>创建阅卷任务</Button>}
        style={{ borderRadius: 12 }}>
        <Table dataSource={tasks} columns={taskColumns} rowKey="id" loading={loading} pagination={false} />
      </Card>

      {isTeacher && (
        <Card title="我的待评阅" style={{ marginTop: 16, borderRadius: 12 }}>
          {pendingGrading.length === 0 && <div style={{ textAlign: "center", padding: 40, color: "#999" }}>暂无待评阅题目</div>}
          {pendingGrading.map((p) => (
            <Card key={p.assignment_id} size="small" style={{ marginBottom: 8, borderRadius: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <strong>{p.task_name}</strong> - 第{p.question_number}题
                  <span style={{ color: "#999", marginLeft: 8 }}>
                    ({p.graded_count}/{p.total_count})
                  </span>
                </div>
                <div>
                  {p.pending_images?.length > 0 && (
                    <Button type="primary" size="small" icon={<AuditOutlined />}
                      onClick={() => {
                        setCurrentPending(p);
                        setCurrentImage(p.pending_images[0]);
                        setGradeScore(p.pending_images[0]?.max_score || 0);
                        setGradeModalOpen(true);
                      }}>
                      开始评阅
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </Card>
      )}

      <Modal title="创建阅卷任务" open={createModalOpen} onOk={handleCreateTask} onCancel={() => setCreateModalOpen(false)}>
        <Space direction="vertical" style={{ width: "100%" }}>
          <Input placeholder="任务名称" value={newTask.name} onChange={(e) => setNewTask({ ...newTask, name: e.target.value })} />
          <Select placeholder="选择批次" value={newTask.batch_id || undefined} onChange={(v) => {
            const batch = batches.find((b) => b.id === v);
            setNewTask({ ...newTask, batch_id: v, template_id: batch?.template_id || "" });
          }} style={{ width: "100%" }}>
            {batches.map((b) => <Select.Option key={b.id} value={b.id}>{b.name}</Select.Option>)}
          </Select>
          <div>
            <span>差值阈值：</span>
            <InputNumber min={0.5} max={50} step={0.5} value={newTask.threshold}
              onChange={(v) => setNewTask({ ...newTask, threshold: v || 5 })} />
            <span style={{ color: "#999", fontSize: 12, marginLeft: 8 }}>分（两位教师评分差值超过此值需重评）</span>
          </div>
        </Space>
      </Modal>

      <Modal title="分配评阅教师" open={assignModalOpen} onOk={handleAssign} onCancel={() => setAssignModalOpen(false)}>
        <Space direction="vertical" style={{ width: "100%" }}>
          <Select placeholder="选择教师" value={assignData.teacher_id || undefined} onChange={(v) => setAssignData({ ...assignData, teacher_id: v })}
            style={{ width: "100%" }}>
            {teachers.map((t) => <Select.Option key={t.id} value={t.id}>{t.real_name || t.username}</Select.Option>)}
          </Select>
          <Select mode="multiple" placeholder="选择题号" value={assignData.question_numbers} onChange={(v) => setAssignData({ ...assignData, question_numbers: v })}
            style={{ width: "100%" }}>
            {[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20].map((n) =>
              <Select.Option key={n} value={n}>第{n}题</Select.Option>
            )}
          </Select>
        </Space>
      </Modal>

      <Modal title="主观题评阅" open={gradeModalOpen} onOk={handleGrade} onCancel={() => setGradeModalOpen(false)}
        okText="提交评分" width={800}>
        {currentImage && (
          <div>
            <div style={{ background: "#f0f0f0", borderRadius: 8, padding: 8, marginBottom: 16, textAlign: "center" }}>
              <img src={`/${currentImage.file_path}`} alt="主观题" style={{ maxWidth: "100%", maxHeight: 400 }} onError={(e) => {
                (e.target as HTMLImageElement).src = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='100'><text x='10' y='50' font-size='14' fill='%23999'>图片加载中...</text></svg>";
              }} />
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <span>评分：</span>
              <InputNumber min={0} max={currentImage.max_score || 100} step={0.5} value={gradeScore}
                onChange={(v) => setGradeScore(v || 0)} />
              <span style={{ color: "#999" }}>满分 {currentImage.max_score || "--"} 分</span>
              {currentPending?.pending_images?.length > 1 && (
                <Space>
                  {currentPending.pending_images.map((img: any, idx: number) => (
                    <Button key={img.id} type={currentImage.id === img.id ? "primary" : "default"} size="small"
                      onClick={() => { setCurrentImage(img); setGradeScore(img.max_score || 0); }}>
                      第{idx + 1}张
                    </Button>
                  ))}
                </Space>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default GradingPage;
