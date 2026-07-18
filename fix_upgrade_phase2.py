import os
b = r"D:\Desktop\Gaston Studio\services\OnlineMark"

# 1. Create PDF processor
code = []
code.append("import os")
code.append("import fitz")
code.append("from PIL import Image")
code.append("from typing import List")
code.append("")
code.append("class PDFProcessor:")
code.append("    @staticmethod")
code.append("    def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200) -> List[str]:")
code.append('        """Convert PDF pages to images"""')
code.append("        os.makedirs(output_dir, exist_ok=True)")
code.append("        doc = fitz.open(pdf_path)")
code.append("        img_paths = []")
code.append("        for page_num in range(len(doc)):")
code.append("            page = doc[page_num]")
code.append("            mat = fitz.Matrix(dpi/72, dpi/72)")
code.append("            pix = page.get_pixmap(matrix=mat)")
code.append("            img_path = os.path.join(output_dir, f\"page_{page_num+1}.png\")")
code.append("            pix.save(img_path)")
code.append("            img_paths.append(img_path)")
code.append("        doc.close()")
code.append("        return img_paths")
code.append("")
code.append("    @staticmethod")
code.append("    def get_page_count(pdf_path: str) -> int:")
code.append("        doc = fitz.open(pdf_path)")
code.append("        count = len(doc)")
code.append("        doc.close()")
code.append("        return count")

path = os.path.join(b, "backend", "app", "services", "pdf_processor.py")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(code))
print("1. PDF processor created")

# 2. Update templates router for PDF upload
path = os.path.join(b, "backend", "app", "routers", "templates.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Add PDF upload endpoint before the image upload
old = '@router.post("/upload-image")'
new = '@router.post("/upload-pdf")\nasync def upload_template_pdf(file: UploadFile = File(...)):\n    import fitz\n    import uuid\n    ext = os.path.splitext(file.filename)[1] or ".pdf"\n    if ext.lower() not in [".pdf"]:\n        raise HTTPException(status_code=400, detail="只支持PDF文件")\n    filename = f"{uuid.uuid4()}{ext}"\n    filepath = os.path.join(settings.TEMPLATE_DIR, filename)\n    with open(filepath, "wb") as f:\n        content = await file.read()\n        f.write(content)\n    # Convert PDF to images\n    from app.services.pdf_processor import PDFProcessor\n    try:\n        img_dir = os.path.join(settings.TEMPLATE_DIR, filename.replace(".pdf", ""))\n        img_paths = PDFProcessor.pdf_to_images(filepath, img_dir)\n        total_pages = len(img_paths)\n        first_page = img_paths[0] if img_paths else filepath\n        return {"filename": filename, "filepath": filepath, "url": f"/uploads/templates/{filename}",\n                "total_pages": total_pages, "page_images": [f"/uploads/templates/{filename.replace(chr(46)+chr(112)+chr(100)+chr(102),chr(47))}{os.path.basename(p)}" for p in img_paths]}\n    except Exception as e:\n        raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")\n\n@router.post("/upload-image")'
c = c.replace(old, new)
print("2. Added PDF upload endpoint")

# Update create_template to handle total_pages and pdf_path
old = '    temp = Template(\n        name=req.name, description=req.description,\n        subject=req.subject, grade=req.grade, exam_name=req.exam_name,\n        info_method=req.info_method, created_by=current_user.id\n    )'
new = '    temp = Template(\n        name=req.name, description=req.description,\n        subject=req.subject, grade=req.grade, exam_name=req.exam_name,\n        info_method=req.info_method, total_pages=req.total_pages or 1,\n        pdf_path=req.pdf_path, created_by=current_user.id\n    )'
c = c.replace(old, new)
print("3. Updated create_template for multi-page")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 3. Update grading router for role permissions
path = os.path.join(b, "backend", "app", "routers", "grading.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Replace teacher check to not be restricted
old = '    if current_user.role != UserRole.TEACHER:\n        raise HTTPException(status_code=403, detail="仅教师可查看待评阅列表")'
new = '    # Teachers and admins can grade\n    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:\n        raise HTTPException(status_code=403, detail="仅教师和管理员可查看待评阅列表")'
c = c.replace(old, new)
# Also update submit_grade to allow admins
old2 = '                 current_user: User = Depends(require_role(UserRole.TEACHER))'
new2 = '                 current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN))'
c = c.replace(old2, new2)
print("4. Updated grading permissions for admin participation")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 4. Update scan router for multi-page
path = os.path.join(b, "backend", "app", "routers", "scan.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Add page_number, side and upload_order to batch creation
old = '    batch = ScanBatch(name=name, template_id=template_id, exam_name=exam_name, created_by=current_user.id)'
new = '    batch = ScanBatch(name=name, template_id=template_id, exam_name=exam_name, upload_order="sequential", created_by=current_user.id)'
c = c.replace(old, new)
print("5. Scan batch default upload_order")

# Add page_number and side to sheet creation in upload
old = '        sheet = ScannedSheet(batch_id=batch_id, filename=file.filename, file_path=filepath)'
new = '        sheet = ScannedSheet(batch_id=batch_id, filename=file.filename, file_path=filepath, page_number=1, side="front")'
c = c.replace(old, new)
print("6. ScannedSheet creation with page/side")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("\nPhase 2+3 complete: PDF processor, API updates, grading permissions")
