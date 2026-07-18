import os
b = r"D:\Desktop\Gaston Studio\services\OnlineMark"
p = os.path.join(b, "frontend", "src", "types", "index.ts")

with open(p, "r", encoding="utf-8") as f:
    c = f.read()

changes = []

# page_number to Marker
if "page_number?: number" not in c:
    c = c.replace("  label?: string;\n}", "  label?: string;\n  page_number?: number;\n}")
    changes.append("Marker: added page_number")

# page_number to Zone
if "page_number?: number" not in c.split("export interface Question")[0].split("export interface Zone")[1]:
    c = c.replace("  sort_order?: number;\n  config?: any;\n}", "  sort_order?: number;\n  page_number?: number;\n  config?: any;\n}")
    changes.append("Zone: added page_number")

# page_number to Question
if "page_number?: number" not in c.split("export interface AnswerPosition")[0]:
    c = c.replace("  sort_order?: number;\n  answer_positions?: AnswerPosition[];\n}", "  sort_order?: number;\n  page_number?: number;\n  answer_positions?: AnswerPosition[];\n}")
    changes.append("Question: added page_number")

# pdf_path + total_pages to Template
if "pdf_path?: string" not in c:
    c = c.replace("  image_path: string;\n", "  image_path: string;\n  pdf_path?: string;\n  total_pages?: number;\n")
    changes.append("Template: added pdf_path, total_pages")

# upload_order to ScanBatch
if "upload_order" not in c:
    c = c.replace("  status: string;\n  created_at?: string;\n}", "  status: string;\n  upload_order?: string;\n  created_at?: string;\n}")
    changes.append("ScanBatch: added upload_order")

# page_number + side to ScannedSheet
if "page_number?: number" not in c.split("export interface GradingTask")[0]:
    c = c.replace("  status: string;\n  error_message?: string;\n}", "  status: string;\n  page_number?: number;\n  side?: string;\n  error_message?: string;\n}")
    changes.append("ScannedSheet: added page_number, side")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)

for ch in changes:
    print(f"  {ch}")
print(f"Total: {len(changes)} type updates")
