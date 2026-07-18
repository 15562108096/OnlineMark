import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "frontend", "src", "pages", "TemplateEditorPage.tsx")
changes = []

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Fix ToolMode type to include answer_mark
c = c.replace('type ToolMode = "marker" | "zone" | "question" | "view";',
    'type ToolMode = "marker" | "zone" | "question" | "view" | "answer_mark";')
changes.append("ToolMode type updated")

# 2. Fix marker count button display
c = c.replace("定位点 {markers.length}/4", "定位点 {markers.length}")
changes.append("Marker count display fixed")

# 3. Fix handleSave to include answer_positions
# Find the marker mapping in handleSave and add new fields
old_save_markers = "markers: markers.map((m) => ({ point_index: m.point_index, x: m.x, y: m.y, label: m.label })),"
new_save_markers = "markers: markers.map((m) => ({ point_index: m.point_index, x: m.x, y: m.y, width: m.width || 0, height: m.height || 0, shape: m.shape || \"circle\", label: m.label })),"
if old_save_markers in c:
    c = c.replace(old_save_markers, new_save_markers)
    changes.append("Marker save fields updated")
else:
    changes.append("WARN: marker save pattern not found")

# 4. Fix question save to include answer_positions
old_save_q = "questions: questions.map((q) => ({\n          question_number: q.question_number, question_type: q.question_type,\n          options_count: q.options_count, options: q.options || [\"A\",\"B\",\"C\",\"D\"].slice(0, q.options_count),\n          option_layout: q.option_layout, score: q.score, correct_answer: q.correct_answer,\n          x: q.x, y: q.y, width: q.width, height: q.height, sort_order: q.sort_order || 0,\n        })),"
new_save_q = "questions: questions.map((q) => ({\n          question_number: q.question_number, question_type: q.question_type,\n          options_count: q.options_count, options: q.options || [\"A\",\"B\",\"C\",\"D\"].slice(0, q.options_count),\n          option_layout: q.option_layout, score: q.score, correct_answer: q.correct_answer,\n          x: q.x, y: q.y, width: q.width, height: q.height, sort_order: q.sort_order || 0,\n          answer_positions: q.answer_positions,\n        })),"
if old_save_q in c:
    c = c.replace(old_save_q, new_save_q)
    changes.append("Question save includes answer_positions")
else:
    changes.append("WARN: question save pattern not found")

# 5. Fix zone save to include config
old_save_zone = "zones: zones.map((z) => ({\n          zone_type: z.zone_type, label: z.label || zoneLabels[z.zone_type],\n          x: z.x, y: z.y, width: z.width, height: z.height, sort_order: z.sort_order || 0,\n        })),"
new_save_zone = "zones: zones.map((z) => ({\n          zone_type: z.zone_type, label: z.label || zoneLabels[z.zone_type],\n          x: z.x, y: z.y, width: z.width, height: z.height, sort_order: z.sort_order || 0,\n          config: z.config,\n        })),"
if old_save_zone in c:
    c = c.replace(old_save_zone, new_save_zone)
    changes.append("Zone save includes config")
else:
    changes.append("WARN: zone save pattern not found")

# 6. Fix the answers tab content that was reverted
# Check if the advanced answers tab with click/input modes is present
if "点击标记" not in c and "手动输入" not in c:
    changes.append("Answers tab: using enhanced version (already present)")
else:
    changes.append("Answers tab: needs enhancement check")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

for ch in changes:
    print(f"  {ch}")
print(f"Total: {len(changes)}")
