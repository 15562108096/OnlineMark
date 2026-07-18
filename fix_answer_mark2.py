import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "frontend", "src", "pages", "TemplateEditorPage.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Replace the buggy answer_mark handler using the exact text from the file
old_start = '    if (mode === "answer_mark") {\n      // Click to mark an answer position within an objective zone'
new_start = '    if (mode === "answer_mark") {'

# Find old handler bounds
idx = c.find(old_start)
if idx >= 0:
    # Find the closing brace of the answer_mark handler
    # It should end right before "if (mode === \"marker\")" 
    end_marker = '\n    if (mode === "marker")'
    idx_end = c.find(end_marker, idx)
    if idx_end >= 0:
        # The new handler
        new_handler = '''    if (mode === "answer_mark") {
      const objZones = zones.filter(z => z.zone_type === "objective");
      for (const z of objZones) {
        if (coords.x >= z.x && coords.x <= z.x + z.width && coords.y >= z.y && coords.y <= z.y + z.height) {
          // Toggle correct if clicking near existing position
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
          // Add position to nearby question
          let added = false;
          for (const q of questions) {
            if (q.answer_positions) {
              for (const p of q.answer_positions) {
                if (Math.abs(coords.x-p.x)<30 && Math.abs(coords.y-p.y)<30) {
                  const opts = ["A","B","C","D","E","F","G","H"];
                  const used = q.answer_positions.map(pp=>pp.option);
                  const next = opts.find(o=>!used.includes(o)) || "A";
                  const npos = [...q.answer_positions, {qnum:q.question_number, option:next, x:coords.x, y:coords.y, is_correct:false}];
                  setQuestions(questions.map(qq => qq.question_number==q.question_number ? {...qq, answer_positions: npos} : qq));
                  message.success("添加选项"+next); added = true; return;
                }
              }
            }
          }
          if (added) return;
          // Create new question
          const qnum = questions.length+1;
          setQuestions([...questions, {question_number: qnum, question_type:"single", options_count:4,
            options:["A","B","C","D"], option_layout:"vertical", score:1.0,
            x:coords.x-5, y:coords.y-5, width:10, height:10,
            sort_order:questions.length, answer_positions:[{qnum, option:"A", x:coords.x, y:coords.y, is_correct:false}]} as any]);
          message.success("新建第"+qnum+"题，可继续点击添加选项位置");
          return;
        }
      }
      message.warning("请在客观题区域内点击");
      return;
    }'''
        
        c = c[:idx] + new_handler + c[idx_end:]
        print("Answer_mark handler replaced successfully")
    else:
        print("WARN: end marker not found")
else:
    print("WARN: old handler start not found")

# Also fix the types file
type_path = os.path.join(base, "frontend", "src", "types", "index.ts")
with open(type_path, "r", encoding="utf-8") as f:
    t = f.read()

# Check if AnswerPosition exists
if "AnswerPosition" not in t:
    print("WARN: AnswerPosition interface missing! Checking Question type...")
    # Read full types file
    print(t[:2000])

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("Done")
