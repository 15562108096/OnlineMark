import os
path = r"D:\Desktop\Gaston Studio\services\OnlineMark\frontend\src\pages\TemplateEditorPage.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = []

# FIX 1: Remove offset/panning state
for pattern in [
    ("const [offset, setOffset] = useState({ x: 0, y: 0 });", ""),
    ("const [dragging, setDragging] = useState(false);", ""),
    ("const [dragStart, setDragStart] = useState({ x: 0, y: 0 });", ""),
]:
    if pattern[0] in content:
        content = content.replace(pattern[0], pattern[1])
        changes.append(f"Removed: {pattern[0][:40]}...")

# FIX 2: Remove dragging from mouseMove handler
old = "  const handleMouseMove = (e: React.MouseEvent) => {\n    if (dragging) {\n      const dx = (e.clientX - dragStart.x) / scale;\n      const dy = (e.clientY - dragStart.y) / scale;\n      setOffset({ x: offset.x + dx, y: offset.y + dy });\n      setDragStart({ x: e.clientX, y: e.clientY });\n      return;\n    }\n    if (!isDrawing || !startPos || !currentRect) return;"
new = "  const handleMouseMove = (e: React.MouseEvent) => {\n    if (!isDrawing || !startPos || !currentRect) return;"
if old in content:
    content = content.replace(old, new)
    changes.append("Fixed handleMouseMove - removed panning")

# Remove setDragging from handleMouseUp
content = content.replace("    setDragging(false);\n    if (!isDrawing", "    if (!isDrawing")

# FIX 3: Fix drawCanvas image position
old = "ctx.drawImage(imgRef.current, offset.x * scale, offset.y * scale, canvas.width, canvas.height);"
new = "ctx.drawImage(imgRef.current, 0, 0, canvas.width, canvas.height);"
if old in content:
    content = content.replace(old, new)
    changes.append("Fixed drawCanvas - removed offset from image position")

# FIX 4: Fix fitToCanvas - remove setOffset
old = "    setScale(s);\n    canvas.width = imgW * s;\n    canvas.height = imgH * s;\n    setOffset({ x: 0, y: 0 });"
new = "    setScale(s);\n    canvas.width = imgW * s;\n    canvas.height = imgH * s;"
if old in content:
    content = content.replace(old, new)
    changes.append("Fixed fitToCanvas - removed setOffset")

# FIX 5: Remove marker limit
content = content.replace(
    'if (markers.length >= 4) { message.warning("最多4个定位点"); return; }',
    'if (markers.length >= 20) { message.warning("定位点最多20个"); return; }'
)
changes.append("Increased marker limit to 20")

content = content.replace(
    "定位点 ({markers.length}/4)",
    "定位点 ({markers.length})"
)
changes.append("Fixed marker count display")

content = content.replace(
    "点击图片标注4个角点",
    "点击图片标注定位点"
)
changes.append("Fixed marker empty text")

# FIX 6: Remove view mode cursor
content = content.replace('mode === "view" ? "grab" : "crosshair"', '"crosshair"')
changes.append("Fixed canvas cursor - removed grab mode")

# FIX 7: Add answer positions mode for marking
old = '      <Button type={mode === "question" ? "primary" : "default"} block icon={<CheckCircleOutlined />}\n                    onClick={() => setMode("question")}>\n                    框选客观题\n                  </Button>'
new = '      <Button type={mode === "question" ? "primary" : "default"} block icon={<CheckCircleOutlined />}\n                    onClick={() => setMode("question")}>\n                    框选客观题\n                  </Button>\n                  <Button type={mode === "answer_mark" ? "primary" : "default"} block icon={<AimOutlined />}\n                    onClick={() => setMode("answer_mark")}\n                    disabled={zones.filter(z => z.zone_type === "objective").length === 0}>\n                    标记答案位置\n                  </Button>'
if old in content:
    content = content.replace(old, new)
    changes.append("Added answer mark mode button")

# FIX 8: Handle answer_mark mode in mouseDown
old = "    if (mode === \"marker\") {"
new = "    if (mode === \"answer_mark\") {\n      // Click to mark an answer position within an objective zone\n      const objZones = zones.filter(z => z.zone_type === \"objective\");\n      for (const z of objZones) {\n        if (coords.x >= z.x && coords.x <= z.x + z.width && coords.y >= z.y && coords.y <= z.y + z.height) {\n          const qnum = questions.length + 1;\n          const optionLetters = [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\"];\n          // Find next unused option letter for this question\n          const existingPos = questions.filter(q => q.answer_positions).flatMap(q => q.answer_positions || []);\n          const usedOptions = existingPos.map(p => p.option);\n          const nextOption = optionLetters.find(o => !usedOptions.includes(o)) || \"A\";\n          const pos = { question_number: qnum, option: nextOption, x: coords.x, y: coords.y, is_correct: false };\n          setQuestions([...questions, {\n            question_number: qnum,\n            question_type: \"single\",\n            options_count: 4,\n            options: [\"A\",\"B\",\"C\",\"D\"],\n            option_layout: \"vertical\",\n            score: 1.0,\n            x: coords.x - 5,\n            y: coords.y - 5,\n            width: 10,\n            height: 10,\n            sort_order: questions.length,\n            answer_positions: [pos]\n          } as any]);\n          message.success(`标记第 ${qnum} 题选项 ${nextOption}，点击可切换为正确答案`);\n          return;\n        }\n      }\n      message.warning(\"请先在客观题区域内点击\");\n      return;\n    }\n    if (mode === \"marker\") {"
if old in content:
    content = content.replace(old, new)
    changes.append("Added answer_mark mode handling")

# FIX 9: Enhance the sidebar tools buttons section  
old = '                  <Tooltip title="框选区域">\n                      <Button type={mode === "zone" ? "primary" : "default"} icon={<BorderOutlined />} onClick={() => setMode("zone")}>\n                        框选区域\n                      </Button>\n                    </Tooltip>'
new = '                  <Tooltip title="框选区域（学生信息/客观题区/主观题区）">\n                      <Button type={mode === "zone" ? "primary" : "default"} icon={<BorderOutlined />} onClick={() => setMode("zone")}>\n                        框选区域\n                      </Button>\n                    </Tooltip>'
if old in content:
    content = content.replace(old, new)
    changes.append("Enhanced zone tooltip")

# FIX 10: Draw answer positions on canvas  
# Add answer position drawing in drawCanvas
old_marker_block = "    // Draw markers\n    markers.forEach((m) => {"
# Insert drawing of answer positions before markers
insert = "    // Draw answer positions (for objective questions with answer_positions)\n    const allAnswerPositions = questions.filter(q => q.answer_positions).flatMap(q => q.answer_positions || []);\n    questions.forEach((q) => {\n      if (q.answer_positions) {\n        q.answer_positions.forEach((pos, idx) => {\n          const color = pos.is_correct ? \"#52c41a\" : \"#722ed1\";\n          ctx.fillStyle = pos.is_correct ? \"rgba(82, 196, 26, 0.6)\" : \"rgba(114, 46, 209, 0.4)\";\n          ctx.strokeStyle = color;\n          ctx.lineWidth = 2 / scale;\n          ctx.beginPath();\n          ctx.arc(pos.x, pos.y, 8 / scale, 0, Math.PI * 2);\n          ctx.fill();\n          ctx.stroke();\n          ctx.fillStyle = \"#fff\";\n          ctx.font = `bold ${9 / scale}px sans-serif`;\n          ctx.textAlign = \"center\";\n          ctx.textBaseline = \"middle\";\n          ctx.fillText(pos.option, pos.x, pos.y);\n          if (pos.is_correct) {\n            ctx.strokeStyle = \"#52c41a\";\n            ctx.lineWidth = 3 / scale;\n            ctx.beginPath();\n            ctx.arc(pos.x, pos.y, 12 / scale, 0, Math.PI * 2);\n            ctx.stroke();\n          }\n        });\n      }\n    });\n\n    // Draw markers\n    markers.forEach((m) => {"
if old_marker_block in content:
    content = content.replace(old_marker_block, insert)
    changes.append("Added answer position drawing on canvas")

# FIX 11: Add answerMode state variable
old_state = "  const [selectedZone, setSelectedZone] = useState<string | null>(null);"
new_state = "  const [selectedZone, setSelectedZone] = useState<string | null>(null);\n  const [answerMode, setAnswerMode] = useState<string>(\"input\");"
if old_state in content:
    content = content.replace(old_state, new_state)
    changes.append("Added answerMode state")

# FIX 12: Add click handler for answer positions in canvas  
# Add onClick to toggle correct answer when in answer_mark mode
old_mouseUp = "    setIsDrawing(false);\n    const rect = { ...currentRect };\n\n    if (mode === \"zone\") {"
new_mouseUp = "    setIsDrawing(false);\n    if (!currentRect) return;\n    const rect = { ...currentRect };\n\n    if (mode === \"zone\") {"
if old_mouseUp in content:
    content = content.replace(old_mouseUp, new_mouseUp)
    changes.append("Added null check in handleMouseUp")

# FIX 13: Fix zone save to include config
content = content.replace(
    "const exists = zones.some((z) => z === editingZone);",
    "const exists = zones.some((z) => z.x === editingZone?.x && z.y === editingZone?.y);"
)
changes.append("Fixed zone existence check")

# FIX 14: Fix the canvas click handler for markers
# The canvas should handle clicking on markers (for delete) and answer positions (for toggle)
old_canvas_mousedown = '    const coords = getCanvasCoords(e.clientX, e.clientY);\n    if (mode === "marker") {'
new_canvas_mousedown = '    const coords = getCanvasCoords(e.clientX, e.clientY);\n    if (mode === "answer_mark") {\n      // Check if clicking on existing answer position to toggle correct\n      for (const q of questions) {\n        if (q.answer_positions) {\n          for (let i = 0; i < q.answer_positions.length; i++) {\n            const pos = q.answer_positions[i];\n            const dist = Math.sqrt((coords.x - pos.x) ** 2 + (coords.y - pos.y) ** 2);\n            if (dist < 15) {\n              // Toggle correct\n              const newPositions = [...q.answer_positions];\n              const wasCorrect = newPositions[i].is_correct;\n              // Clear all correct for this question, then set this one\n              newPositions.forEach((p, j) => { p.is_correct = (j === i) ? !wasCorrect : false; });\n              setQuestions(questions.map(qq => qq.question_number === q.question_number ? { ...qq, answer_positions: newPositions, correct_answer: !wasCorrect ? pos.option : \"\" } : qq));\n              message.success(!wasCorrect ? `标记第 ${q.question_number} 题正确答案为 ${pos.option}` : `取消第 ${q.question_number} 题正确答案`);\n              return;\n            }\n          }\n        }\n      }\n    }\n    if (mode === "marker") {'
if old_canvas_mousedown in content:
    content = content.replace(old_canvas_mousedown, new_canvas_mousedown)
    changes.append("Added answer position click-to-toggle")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

for c in changes:
    print(f"  [OK] {c}")
print(f"\nTotal: {len(changes)} changes applied")
