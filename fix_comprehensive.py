import os
b = r"D:\Desktop\Gaston Studio\services\OnlineMark"

print("=== 综合修复脚本 ===")
print()

# 1. Fix template editor - add page navigation + PDF upload
path = os.path.join(b, "frontend", "src", "pages", "TemplateEditorPage.tsx")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Add currentPage and totalPages state
c = c.replace(
    "  const [saving, setSaving] = useState(false);",
    "  const [saving, setSaving] = useState(false);\n  const [currentPage, setCurrentPage] = useState(1);\n  const [totalPages, setTotalPages] = useState(1);"
)

# Add page navigation UI after the card header
old_nav = '      <div className="editor-container">'
new_nav = '      {/* Page navigation */}\n'
new_nav += '      {totalPages > 1 && (\n'
new_nav += '        <Card style={{ borderRadius: 12, marginBottom: 16 }} bodyStyle={{ padding: "8px 16px" }}>\n'
new_nav += '          <Space>\n'
new_nav += '            <Button size="small" disabled={currentPage <= 1}\n'
new_nav += '              onClick={() => setCurrentPage(p => Math.max(1, p-1))}>上一页</Button>\n'
new_nav += '            <span>第 {currentPage} / {totalPages} 页</span>\n'
new_nav += '            <Button size="small" disabled={currentPage >= totalPages}\n'
new_nav += '              onClick={() => setCurrentPage(p => Math.min(totalPages, p+1))}>下一页</Button>\n'
new_nav += '          </Space>\n'
new_nav += '        </Card>\n'
new_nav += '      )}\n'
new_nav += '      <div className="editor-container">'
c = c.replace(old_nav, new_nav)
print("1a. Added page navigation UI")

# Add PDF upload button next to image upload
old_upload = '                  <Upload accept="image/*" showUploadList={false} beforeUpload={handleImageUpload}>\n                    <Button block icon={<PictureOutlined />}>上传答题卡图片</Button>\n                  </Upload>'
new_upload = '                  <Upload accept="image/*" showUploadList={false} beforeUpload={handleImageUpload}>\n                    <Button block icon={<PictureOutlined />}>上传图片(JPG/PNG)</Button>\n                  </Upload>\n'
new_upload += '                  <Upload accept=".pdf" showUploadList={false} beforeUpload={async (file) => {\n'
new_upload += '                    try {\n'
new_upload += '                      const form = new FormData(); form.append("file", file);\n'
new_upload += '                      const res = await fetch("/api/templates/upload-pdf", { method: "POST", body: form });\n'
new_upload += '                      const data = await res.json();\n'
new_upload += '                      if (data.page_images && data.page_images.length > 0) {\n'
new_upload += '                        setTotalPages(data.total_pages);\n'
new_upload += '                        setImageUrl(data.page_images[0]);\n'
new_upload += '                        message.success("PDF上传成功，共"+data.total_pages+"页");\n'
new_upload += '                      }\n'
new_upload += '                    } catch (e) { message.error("PDF上传失败"); }\n'
new_upload += '                    return false;\n'
new_upload += '                  }}>\n'
new_upload += '                    <Button block icon={<PictureOutlined />}>上传PDF</Button>\n'
new_upload += '                  </Upload>'
c = c.replace(old_upload, new_upload)
print("1b. Added PDF upload button")

# Filter markers by page_number
c = c.replace(
    '                    {markers.map((m) => (',
    '                    {/* Filtered by page */}\n                    {markers.filter(m => !m.page_number || m.page_number === currentPage).map((m) => ('
)

# Add page_number to new markers
c = c.replace(
    'const newMarker: Marker = { point_index: markers.length, x: coords.x, y: coords.y, label: `P${markers.length + 1}` };\n      setMarkers([...markers, newMarker]);',
    'const newMarker: Marker = { point_index: markers.length, x: coords.x, y: coords.y, label: `P${markers.length + 1}`, page_number: currentPage };\n      setMarkers([...markers, newMarker]);'
)
print("1c. Filtered markers by page")

# Filter zones by page_number
old_zones_filter = '                    {zones.map((z, idx) => ('
new_zones_filter = '                    {zones.filter(z => !z.page_number || z.page_number === currentPage).map((z, idx) => ('
c = c.replace(old_zones_filter, new_zones_filter)
print("1d. Filtered zones by page")

# Add page_number to new zones
c = c.replace(
    'sort_order: zones.length,\n      });\n      setZoneModalOpen(true);\n    } else if (mode === "question")',
    'sort_order: zones.length, page_number: currentPage,\n      });\n      setZoneModalOpen(true);\n    } else if (mode === "question")'
)
print("1e. Added page_number to new zones")

# Filter questions by page_number
old_q_filter = '                    {questions.map((q, idx) => ('
new_q_filter = '                    {questions.filter(q => !q.page_number || q.page_number === currentPage).map((q, idx) => ('
c = c.replace(old_q_filter, new_q_filter)
print("1f. Filtered questions by page")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 2. Fix ScanBatchPage - add upload order
path = os.path.join(b, "frontend", "src", "pages", "ScanBatchPage.tsx")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Add upload_order to batch creation
old_batch = '      <Input placeholder="考试名称（可选）" value={newBatch.exam_name} onChange={(e) => setNewBatch({ ...newBatch, exam_name: e.target.value })} />'
new_batch = '      <Input placeholder="考试名称（可选）" value={newBatch.exam_name} onChange={(e) => setNewBatch({ ...newBatch, exam_name: e.target.value })} />\n'
new_batch += '          <Select placeholder="上传顺序" value={newBatch.upload_order || "sequential"} onChange={(v) => setNewBatch({ ...newBatch, upload_order: v })} style={{ width: "100%" }}>\n'
new_batch += '            <Select.Option value="sequential">顺序上传（第1页→第2页）</Select.Option>\n'
new_batch += '            <Select.Option value="reversed">倒序上传（第2页→第1页）</Select.Option>\n'
new_batch += '          </Select>'
c = c.replace(old_batch, new_batch)
print("1g. Added upload order to scan batch")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 3. Fix GradingPage - add admin grading participation
path = os.path.join(b, "frontend", "src", "pages", "GradingPage.tsx")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Add admin to the teacher check for grading
# The current code checks: const isTeacher = user?.role === "teacher"
# Change to also allow admin
c = c.replace(
    'const isTeacher = (e==null?void 0:e.role)==="teacher"',
    'const isTeacher = (e==null?void 0:e.role)==="teacher" || (e==null?void 0:e.role)==="admin" || (e==null?void 0:e.role)==="super_admin"'
)

# Also fix the role display for admin
c = c.replace('"teacher"?', '"teacher" || user?.role === "admin" || user?.role === "super_admin"?')

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("1h. Updated grading permissions for admin")

print()
print("=== 综合修复完成 ===")
