import React, { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Button, Card, Input, Select, Form, message, Space, Tag, Modal, Tooltip,
  Tabs, InputNumber, Divider, Upload, Radio, Switch, Popconfirm, Empty,
} from "antd";
import {
  SaveOutlined, ArrowLeftOutlined, PlusOutlined, DeleteOutlined,
  EditOutlined, AimOutlined, BorderOutlined, PictureOutlined,
  CheckCircleOutlined, SettingOutlined, UndoOutlined,
} from "@ant-design/icons";
import { templateApi } from "../services/api";
import { Template, Marker, Zone, Question } from "../types";
import { useAuth } from "../store/AuthContext";

interface Rect {
  x: number; y: number; w: number; h: number;
}

type ToolMode = "marker" | "zone" | "question" | "view" | "answer_mark";

const zoneColors: Record<string, string> = {
  student_info: "#0099ff",
  objective: "#52c41a",
  subjective: "#fa8c16",
};

const zoneLabels: Record<string, string> = {
  student_info: "学生信息",
  objective: "客观题",
  subjective: "主观题",
};

const TemplateEditorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(new Image());

  const [templateName, setTemplateName] = useState("");
  const [subject, setSubject] = useState("");
  const [grade, setGrade] = useState("");
  const [examName, setExamName] = useState("");
  const [infoMethod, setInfoMethod] = useState<"omr" | "barcode">("omr");
  const [imageUrl, setImageUrl] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageSize, setImageSize] = useState({ w: 0, h: 0 });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Annotation data
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);

  // Tool state
  const [mode, setMode] = useState<ToolMode>("marker");
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [currentRect, setCurrentRect] = useState<Rect | null>(null);
  const [scale, setScale] = useState(1);
  
  
  
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [answerMode, setAnswerMode] = useState<string>("input");
  const [selectedMarker, setSelectedMarker] = useState<number | null>(null);

  // Zone/Question modals
  const [zoneModalOpen, setZoneModalOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<Partial<Zone> | null>(null);
  const [questionModalOpen, setQuestionModalOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<Partial<Question> | null>(null);
  const [answerModalOpen, setAnswerModalOpen] = useState(false);
  const [editingAnswer, setEditingAnswer] = useState<{ qnum: number; answer: string } | null>(null);

  useEffect(() => {
    if (id) loadTemplate();
  }, [id]);

  const loadTemplate = async () => {
    try {
      const res = await templateApi.get(id!);
      const t: Template = res.data;
      setTemplateName(t.name);
      setSubject(t.subject || "");
      setGrade(t.grade || "");
      setExamName(t.exam_name || "");
      setInfoMethod(t.info_method);
      setImageUrl(t.image_path);
      setMarkers(t.markers || []);
      setZones(t.zones || []);
      setQuestions(t.questions || []);
      loadImage(t.image_path);
    } catch { message.error("加载模板失败"); }
  };

  const loadImage = (path: string) => {
    const img = imgRef.current;
    img.onload = () => {
      setImageSize({ w: img.naturalWidth, h: img.naturalHeight });
      fitToCanvas(img.naturalWidth, img.naturalHeight);
      drawCanvas();
    };
    img.src = path.startsWith("http") ? path : `/${path}`;
  };

  const handleImageUpload = async (file: File) => {
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = imgRef.current;
      img.onload = () => {
        setImageSize({ w: img.naturalWidth, h: img.naturalHeight });
        fitToCanvas(img.naturalWidth, img.naturalHeight);
        drawCanvas();
      };
      img.src = e.target?.result as string;
    };
    reader.readAsDataURL(file);
    return false;
  };

  const fitToCanvas = (imgW: number, imgH: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const maxW = canvas.parentElement?.clientWidth || 800;
    const maxH = canvas.parentElement?.clientHeight || 600;
    const sx = (maxW - 40) / imgW;
    const sy = (maxH - 40) / imgH;
    const s = Math.min(sx, sy, 1.5);
    setScale(s);
    canvas.width = imgW * s;
    canvas.height = imgH * s;
  };

  const getCanvasCoords = (clientX: number, clientY: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: (clientX - rect.left) / scale,
      y: (clientY - rect.top) / scale,
    };
  };

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (imgRef.current.complete && imgRef.current.naturalWidth > 0) {
      ctx.drawImage(imgRef.current, 0, 0, canvas.width, canvas.height);
    }

    ctx.save();
    ctx.scale(scale, scale);

    // Draw answer positions (for objective questions with answer_positions)
    const allAnswerPositions = questions.filter(q => q.answer_positions).flatMap(q => q.answer_positions || []);
    questions.forEach((q) => {
      if (q.answer_positions) {
        q.answer_positions.forEach((pos, idx) => {
          const color = pos.is_correct ? "#52c41a" : "#722ed1";
          ctx.fillStyle = pos.is_correct ? "rgba(82, 196, 26, 0.6)" : "rgba(114, 46, 209, 0.4)";
          ctx.strokeStyle = color;
          ctx.lineWidth = 2 / scale;
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, 8 / scale, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
          ctx.fillStyle = "#fff";
          ctx.font = `bold ${9 / scale}px sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(pos.option, pos.x, pos.y);
          if (pos.is_correct) {
            ctx.strokeStyle = "#52c41a";
            ctx.lineWidth = 3 / scale;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, 12 / scale, 0, Math.PI * 2);
            ctx.stroke();
          }
        });
      }
    });

    // Draw markers
    markers.forEach((m) => {
      ctx.fillStyle = "#ff4d4f";
      ctx.strokeStyle = "#ff4d4f";
      ctx.lineWidth = 2 / scale;
      ctx.beginPath();
      ctx.arc(m.x, m.y, 6 / scale, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1.5 / scale;
      ctx.stroke();
      ctx.fillStyle = "#ff4d4f";
      ctx.font = `${12 / scale}px sans-serif`;
      ctx.fillText(`P${m.point_index + 1}`, m.x + 10 / scale, m.y - 8 / scale);
    });

    // Draw zones
    zones.forEach((z) => {
      const color = zoneColors[z.zone_type] || "#1677ff";
      ctx.strokeStyle = color;
      ctx.lineWidth = 2 / scale;
      ctx.setLineDash([5 / scale, 3 / scale]);
      ctx.strokeRect(z.x, z.y, z.width, z.height);
      ctx.setLineDash([]);
      ctx.fillStyle = color + "20";
      ctx.fillRect(z.x, z.y, z.width, z.height);
      ctx.fillStyle = color;
      ctx.font = `bold ${12 / scale}px sans-serif`;
      const label = z.label || zoneLabels[z.zone_type] || z.zone_type;
      ctx.fillText(label, z.x + 4 / scale, z.y + 14 / scale);
    });

    // Draw questions
    questions.forEach((q) => {
      if (q.x != null && q.y != null && q.width && q.height) {
        ctx.strokeStyle = "#722ed1";
        ctx.lineWidth = 1.5 / scale;
        ctx.strokeRect(q.x, q.y, q.width, q.height);
        ctx.fillStyle = "#722ed120";
        ctx.fillRect(q.x, q.y, q.width, q.height);
        ctx.fillStyle = "#722ed1";
        ctx.font = `${11 / scale}px sans-serif`;
        const label = `Q${q.question_number}`;
        ctx.fillText(label, q.x + 3 / scale, q.y + 12 / scale);
        if (q.correct_answer) {
          ctx.fillText(`[${q.correct_answer}]`, q.x + 3 / scale, q.y + 24 / scale);
        }
      }
    });

    // Draw current drawing rect
    if (currentRect && isDrawing) {
      ctx.strokeStyle = "#1677ff";
      ctx.lineWidth = 2 / scale;
      ctx.setLineDash([4 / scale, 4 / scale]);
      ctx.strokeRect(currentRect.x, currentRect.y, currentRect.w, currentRect.h);
      ctx.setLineDash([]);
    }

    ctx.restore();
  }, [markers, zones, questions, currentRect, isDrawing, scale]);

  useEffect(() => { drawCanvas(); }, [drawCanvas]);

  // Mouse events
  const handleMouseDown = (e: React.MouseEvent) => {
    const coords = getCanvasCoords(e.clientX, e.clientY);
    if (mode === "answer_mark") {
      const objZones = zones.filter(z => z.zone_type === "objective");
      for (const z of objZones) {
        if (coords.x >= z.x && coords.x <= z.x + z.width && coords.y >= z.y && coords.y <= z.y + z.height) {
          for (const q of questions) {
            if (q.answer_positions) {
              for (let i = 0; i < q.answer_positions.length; i++) {
                const p = q.answer_positions[i];
                if (Math.sqrt((coords.x-p.x)**2 + (coords.y-p.y)**2) < 15) {
                  const npos = [...q.answer_positions];
                  const was = npos[i].is_correct;
                  npos.forEach((pp,j) => { pp.is_correct = (j==i) ? !was : false; });
                  setQuestions(questions.map(qq => qq.question_number==q.question_number
                    ? {...qq, answer_positions: npos, correct_answer: !was ? p.option : ""} : qq));
                  message.success(!was ? "标记第"+q.question_number+"题答案"+p.option : "取消标记");
                  return;
                }
              }
            }
          }
          let added = false;
          for (const q of questions) {
            if (q.answer_positions) {
              for (const p of q.answer_positions) {
                if (Math.abs(coords.x-p.x)<30 && Math.abs(coords.y-p.y)<30) {
                  const opts = ["A","B","C","D","E","F","G","H"];
                  const used = q.answer_positions.map(pp=>pp.option);
                  const next = opts.find(o=>!used.includes(o)) || "A";
                  const npos = [...q.answer_positions, {question_number: q.question_number, option: next, x: coords.x, y: coords.y, is_correct: false}];
                  setQuestions(questions.map(qq => qq.question_number==q.question_number ? {...qq, answer_positions: npos} : qq));
                  message.success("添加选项"+next); added = true; return;
                }
              }
            }
          }
          if (added) return;
          const qnum = questions.length+1;
          setQuestions([...questions, {question_number: qnum, question_type:"single", options_count:4,
            options:["A","B","C","D"], option_layout:"vertical", score:1.0,
            x:coords.x-5, y:coords.y-5, width:10, height:10,
            sort_order:questions.length, answer_positions:[{question_number:qnum, option:"A", x:coords.x, y:coords.y, is_correct:false}]} as any]);
          message.success("新建第"+qnum+"题，可继续点击添加选项位置");
          return;
        }
      }
      message.warning("请在客观题区域内点击");
      return;
    }
    if (mode === "marker") {
      if (markers.length >= 20) { message.warning("定位点最多20个"); return; }
      const newMarker: Marker = { point_index: markers.length, x: coords.x, y: coords.y, label: `P${markers.length + 1}`, page_number: currentPage };
      setMarkers([...markers, newMarker]);
    } else {
      setIsDrawing(true);
      setStartPos(coords);
      setCurrentRect({ x: coords.x, y: coords.y, w: 0, h: 0 });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing || !startPos || !currentRect) return;
    const coords = getCanvasCoords(e.clientX, e.clientY);
    setCurrentRect({
      x: Math.min(startPos.x, coords.x),
      y: Math.min(startPos.y, coords.y),
      w: Math.abs(coords.x - startPos.x),
      h: Math.abs(coords.y - startPos.y),
    });
  };

  const handleMouseUp = () => {
    if (!isDrawing || !currentRect || currentRect.w < 5 || currentRect.h < 5) {
      setIsDrawing(false);
      setCurrentRect(null);
      return;
    }
    setIsDrawing(false);

    const rect = { ...currentRect };

    if (mode === "zone") {
      setEditingZone({
        zone_type: "objective",
        label: "",
        x: rect.x,
        y: rect.y,
        width: rect.w,
        height: rect.h,
        sort_order: zones.length, page_number: currentPage,
      });
      setZoneModalOpen(true);
    } else if (mode === "question") {
      setEditingQuestion({
        question_number: questions.length + 1,
        question_type: "single",
        options_count: 4,
        options: ["A", "B", "C", "D"],
        option_layout: "vertical",
        score: 1.0,
        x: rect.x,
        y: rect.y,
        width: rect.w,
        height: rect.h,
        sort_order: questions.length,
      });
      setQuestionModalOpen(true);
    }
    setCurrentRect(null);
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (e.cancelable) {
      e.preventDefault();
    }
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setScale((s) => Math.max(0.2, Math.min(3, s * delta)));
  };

  // Save template
  const handleSave = async () => {
    if (!templateName) { message.error("请输入模板名称"); return; }

    let imgPath = imageUrl;
    if (imageFile) {
      try {
        const res = await templateApi.uploadImage(imageFile);
        imgPath = "uploads/templates/" + res.data.filename;
      } catch { message.error("图片上传失败"); return; }
    }

    setSaving(true);
    try {
      const data = {
        name: templateName,
        subject, grade, exam_name: examName,
        info_method: infoMethod,
        markers: markers.map((m) => ({ point_index: m.point_index, x: m.x, y: m.y, width: m.width || 0, height: m.height || 0, shape: m.shape || "circle", label: m.label })),
        zones: zones.map((z) => ({
          zone_type: z.zone_type, label: z.label || zoneLabels[z.zone_type],
          x: z.x, y: z.y, width: z.width, height: z.height, sort_order: z.sort_order || 0,
          config: z.config,
        })),
        questions: questions.map((q) => ({
          question_number: q.question_number, question_type: q.question_type,
          options_count: q.options_count, options: q.options || ["A","B","C","D"].slice(0, q.options_count),
          option_layout: q.option_layout, score: q.score, correct_answer: q.correct_answer,
          x: q.x, y: q.y, width: q.width, height: q.height, sort_order: q.sort_order || 0,
          answer_positions: q.answer_positions,
        })),
      };

      if (id) {
        await templateApi.update(id, data);
        message.success("模板已更新");
      } else {
        await templateApi.create(data);
        message.success("模板创建成功");
      }
      navigate("/templates");
    } catch { message.error("保存失败"); }
    finally { setSaving(false); }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/templates")}>返回</Button>
          <h3 style={{ margin: 0 }}>{id ? "编辑模板" : "新建模板"}</h3>
        </Space>
        <Space>
          <Button icon={<UndoOutlined />} onClick={() => { setMarkers([]); setZones([]); setQuestions([]); }}>重置标注</Button>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={saving}>保存模板</Button>
        </Space>
      </div>

      <Card style={{ borderRadius: 12, marginBottom: 16 }} bodyStyle={{ padding: 12 }}>
        <Space wrap>
          <Input placeholder="模板名称" value={templateName} onChange={(e) => setTemplateName(e.target.value)} style={{ width: 200 }} />
          <Input placeholder="科目" value={subject} onChange={(e) => setSubject(e.target.value)} style={{ width: 120 }} />
          <Input placeholder="年级" value={grade} onChange={(e) => setGrade(e.target.value)} style={{ width: 120 }} />
          <Input placeholder="考试名称" value={examName} onChange={(e) => setExamName(e.target.value)} style={{ width: 160 }} />
          <Select value={infoMethod} onChange={setInfoMethod} style={{ width: 120 }}>
            <Select.Option value="omr">OMR考号</Select.Option>
            <Select.Option value="barcode">条形码</Select.Option>
          </Select>
        </Space>
      </Card>

      {/* Page navigation */}
      {totalPages > 1 && (
        <Card style={{ borderRadius: 12, marginBottom: 16 }} bodyStyle={{ padding: "8px 16px" }}>
          <Space>
            <Button size="small" disabled={currentPage <= 1}
              onClick={() => setCurrentPage(p => Math.max(1, p-1))}>上一页</Button>
            <span>第 {currentPage} / {totalPages} 页</span>
            <Button size="small" disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(p => Math.min(totalPages, p+1))}>下一页</Button>
          </Space>
        </Card>
      )}
      {/* Page navigation */}
      {totalPages > 1 && (
        <Card style={{ borderRadius: 12, marginBottom: 16 }} bodyStyle={{ padding: "8px 16px" }}>
          <Space>
            <Button size="small" disabled={currentPage <= 1}
              onClick={() => setCurrentPage(p => Math.max(1, p-1))}>上一页</Button>
            <span>第 {currentPage} / {totalPages} 页</span>
            <Button size="small" disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(p => Math.min(totalPages, p+1))}>下一页</Button>
          </Space>
        </Card>
      )}
      <div className="editor-container">
        <div className="editor-canvas-wrap" onWheel={handleWheel}>
          {!imageUrl && !imageFile && (
            <div style={{ textAlign: "center", color: "#fff" }}>
              <PictureOutlined style={{ fontSize: 48, opacity: 0.5 }} />
              <p style={{ marginTop: 16 }}>请上传空白答题卡扫描图</p>
              <Upload accept="image/*" showUploadList={false} beforeUpload={handleImageUpload}>
                <Button type="primary" ghost>选择图片</Button>
              </Upload>
            </div>
          )}
          {(imageUrl || imageFile) && (
            <canvas
              ref={canvasRef}
              style={{ cursor: mode === "marker" ? "crosshair" : "crosshair", maxWidth: "100%", maxHeight: "100%" }}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onContextMenu={(e) => e.preventDefault()}
            />
          )}
          <div style={{ position: "absolute", bottom: 8, right: 8, color: "#fff" }}>
            <Tag>缩放: {Math.round(scale * 100)}%</Tag>
            {imageSize.w > 0 && <Tag>{imageSize.w}x{imageSize.h}</Tag>}
          </div>
        </div>

        <div className="editor-sidebar">
          <Tabs items={[
            {
              key: "tools", label: "标注工具",
              children: (
                <Space direction="vertical" style={{ width: "100%" }}>
                  <Upload accept="image/*" showUploadList={false} beforeUpload={(file) => { handleImageUpload(file); return false; }}>
                    <Button block icon={<PictureOutlined />}>上传答题卡图片</Button>
                  </Upload>
                  <Divider style={{ margin: "8px 0" }} />
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                    <Tooltip title="点击图片标注定位点">
                      <Button type={mode === "marker" ? "primary" : "default"} icon={<AimOutlined />} onClick={() => setMode("marker")}>
                        定位点 {markers.length}
                      </Button>
                    </Tooltip>
                    <Tooltip title="拖拽框选区域">
                      <Button type={mode === "zone" ? "primary" : "default"} icon={<BorderOutlined />} onClick={() => setMode("zone")}>
                        框选区域
                      </Button>
                    </Tooltip>
                  </div>
                  <Button type={mode === "question" ? "primary" : "default"} block icon={<CheckCircleOutlined />}
                    onClick={() => setMode("question")}>
                    框选客观题
                  </Button>
                  <Button type={mode === "answer_mark" ? "primary" : "default"} block icon={<AimOutlined />}
                    onClick={() => setMode("answer_mark")}
                    disabled={zones.filter(z => z.zone_type === "objective").length === 0}>
                    标记答案位置
                  </Button>
                  <Divider style={{ margin: "8px 0" }} />

                  <div>
                    <div style={{ fontWeight: 600, marginBottom: 8 }}>定位点 ({markers.length})</div>
                    {markers.length === 0 && <p style={{ color: "#999", fontSize: 12 }}>点击图片标注定位点</p>}
                    {/* Filtered by page */}
                    {markers.filter(m => !m.page_number || m.page_number === currentPage).map((m) => (
                      <div key={m.point_index} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}>
                        <span className="zone-tag marker">P{m.point_index + 1}</span>
                        <span style={{ fontSize: 12, color: "#999" }}>({Math.round(m.x)}, {Math.round(m.y)})</span>
                        <Button type="link" size="small" danger icon={<DeleteOutlined />}
                          onClick={() => setMarkers(markers.filter((_, i) => i !== m.point_index).map((mm, i) => ({ ...mm, point_index: i })))} />
                      </div>
                    ))}
                  </div>

                  <Divider style={{ margin: "8px 0" }} />

                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ fontWeight: 600 }}>区域 ({zones.length})</span>
                      <Button type="link" size="small" icon={<PlusOutlined />} onClick={() => setMode("zone")}>添加</Button>
                    </div>
                    {zones.length === 0 && <p style={{ color: "#999", fontSize: 12 }}>使用框选工具标注区域</p>}
                    {zones.filter(z => !z.page_number || z.page_number === currentPage).map((z, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", alignItems: "center" }}>
                        <span className={`zone-tag ${z.zone_type}`}>{z.label || zoneLabels[z.zone_type]}</span>
                        <Space size={4}>
                          <Button type="link" size="small" icon={<EditOutlined />}
                            onClick={() => { setEditingZone(z); setZoneModalOpen(true); }} />
                          <Button type="link" size="small" danger icon={<DeleteOutlined />}
                            onClick={() => setZones(zones.filter((_, i) => i !== idx))} />
                        </Space>
                      </div>
                    ))}
                  </div>

                  <Divider style={{ margin: "8px 0" }} />

                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ fontWeight: 600 }}>客观题 ({questions.length})</span>
                      <Button type="link" size="small" icon={<PlusOutlined />} onClick={() => setMode("question")}>添加</Button>
                    </div>
                    {questions.length === 0 && <p style={{ color: "#999", fontSize: 12 }}>框选或点击添加客观题</p>}
                    {questions.filter(q => !q.page_number || q.page_number === currentPage).map((q, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", alignItems: "center" }}>
                        <Space>
                          <span className="zone-tag objective">Q{q.question_number}</span>
                          <span style={{ fontSize: 12, color: "#999" }}>
                            {q.question_type === "single" ? "单选" : q.question_type === "multiple" ? "多选" : "判断"}
                            {q.correct_answer ? ` [${q.correct_answer}]` : ""}
                          </span>
                        </Space>
                        <Space size={4}>
                          <Button type="link" size="small" icon={<EditOutlined />}
                            onClick={() => { setEditingQuestion(q); setQuestionModalOpen(true); }} />
                          <Button type="link" size="small" danger icon={<DeleteOutlined />}
                            onClick={() => setQuestions(questions.filter((_, i) => i !== idx))} />
                        </Space>
                      </div>
                    ))}
                  </div>
                </Space>
              ),
            },
            {
              key: "answers", label: "正确答案",
              children: (
                <div>
                  <p style={{ color: "#999", fontSize: 13, marginBottom: 12 }}>为每道客观题录入正确答案</p>
                  {questions.length === 0 && <Empty description="请先添加客观题" />}
                  {questions.map((q) => (
                    <div key={q.question_number} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid #f0f0f0" }}>
                      <span>第{q.question_number}题</span>
                      <Input
                        style={{ width: 120 }}
                        size="small"
                        placeholder="如 A / AB"
                        value={q.correct_answer || ""}
                        onChange={(e) => {
                          setQuestions(questions.map((qq) =>
                            qq.question_number === q.question_number
                              ? { ...qq, correct_answer: e.target.value.toUpperCase() }
                              : qq
                          ));
                        }}
                      />
                    </div>
                  ))}
                </div>
              ),
            },
          ]} />
        </div>
      </div>

      {/* Zone Modal */}
      <Modal title="区域配置" open={zoneModalOpen} onOk={() => {
        if (editingZone) {
          const exists = zones.some((z) => z.x === editingZone?.x && z.y === editingZone?.y);
          if (!exists) {
            setZones([...zones, editingZone as Zone]);
          } else {
            setZones(zones.map((z) => z === editingZone ? editingZone as Zone : z));
          }
        }
        setZoneModalOpen(false);
        setEditingZone(null);
      }} onCancel={() => { setZoneModalOpen(false); setEditingZone(null); }}>
        <Form layout="vertical">
          <Form.Item label="区域类型">
            <Select value={editingZone?.zone_type} onChange={(v) => setEditingZone({ ...editingZone, zone_type: v })}>
              <Select.Option value="student_info">学生信息区</Select.Option>
              <Select.Option value="objective">客观题区</Select.Option>
              <Select.Option value="subjective">主观题区</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="标签">
            <Input value={editingZone?.label} onChange={(e) => setEditingZone({ ...editingZone, label: e.target.value })} />
          </Form.Item>
          <Space>
            <Form.Item label="X"><InputNumber value={Math.round(editingZone?.x || 0)} disabled /></Form.Item>
            <Form.Item label="Y"><InputNumber value={Math.round(editingZone?.y || 0)} disabled /></Form.Item>
            <Form.Item label="宽"><InputNumber value={Math.round(editingZone?.width || 0)} disabled /></Form.Item>
            <Form.Item label="高"><InputNumber value={Math.round(editingZone?.height || 0)} disabled /></Form.Item>
          </Space>
        </Form>
      </Modal>

      {/* Question Modal */}
      <Modal title="客观题配置" open={questionModalOpen} onOk={() => {
        if (editingQuestion) {
          const opts = editingQuestion.options || ["A","B","C","D"].slice(0, editingQuestion.options_count || 4);
          const exists = questions.some((q) => q.question_number === editingQuestion.question_number);
          if (!exists) {
            setQuestions([...questions, { ...editingQuestion, options: opts } as Question]);
          } else {
            setQuestions(questions.map((q) => q.question_number === editingQuestion.question_number ? { ...editingQuestion, options: opts } as Question : q));
          }
        }
        setQuestionModalOpen(false);
        setEditingQuestion(null);
      }} onCancel={() => { setQuestionModalOpen(false); setEditingQuestion(null); }}>
        <Form layout="vertical">
          <Form.Item label="题号">
            <InputNumber min={1} value={editingQuestion?.question_number} onChange={(v) => setEditingQuestion({ ...editingQuestion, question_number: v || 1 })} />
          </Form.Item>
          <Form.Item label="题型">
            <Select value={editingQuestion?.question_type} onChange={(v) => setEditingQuestion({ ...editingQuestion, question_type: v })}>
              <Select.Option value="single">单选题</Select.Option>
              <Select.Option value="multiple">多选题</Select.Option>
              <Select.Option value="judge">判断题</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="选项数量">
            <InputNumber min={2} max={10} value={editingQuestion?.options_count} onChange={(v) => {
              const cnt = v || 4;
              const opts = "ABCDEFGHIJ".split("").slice(0, cnt);
              setEditingQuestion({ ...editingQuestion, options_count: cnt, options: opts });
            }} />
          </Form.Item>
          <Form.Item label="选项排列">
            <Radio.Group value={editingQuestion?.option_layout} onChange={(e) => setEditingQuestion({ ...editingQuestion, option_layout: e.target.value })}>
              <Radio value="vertical">竖排</Radio>
              <Radio value="horizontal">横排</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item label="分值">
            <InputNumber min={0.5} step={0.5} value={editingQuestion?.score} onChange={(v) => setEditingQuestion({ ...editingQuestion, score: v || 1 })} />
          </Form.Item>
          <Form.Item label="正确答案">
            <Input value={editingQuestion?.correct_answer || ""} placeholder="如 A / AB / T" onChange={(e) => setEditingQuestion({ ...editingQuestion, correct_answer: e.target.value.toUpperCase() })} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TemplateEditorPage;
