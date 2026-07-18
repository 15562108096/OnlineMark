import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "frontend", "src", "pages", "TemplateEditorPage.tsx")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()
start = -1
for i, l in enumerate(lines):
    if 'if (mode === "answer_mark")' in l and start < 0:
        start = i
    if start >= 0 and 'message.warning("请先在客观题区域内点击")' in l:
        end = i + 2
        break
if start >= 0 and end > start:
    new_lines = [
        '    if (mode === "answer_mark") {\n',
        '      const objZones = zones.filter(z => z.zone_type === "objective");\n',
        '      for (const z of objZones) {\n',
        '        if (coords.x >= z.x && coords.x <= z.x + z.width && coords.y >= z.y && coords.y <= z.y + z.height) {\n',
        '          for (const q of questions) {\n',
        '            if (q.answer_positions) {\n',
        '              for (let i = 0; i < q.answer_positions.length; i++) {\n',
        '                const p = q.answer_positions[i];\n',
        '                if (Math.sqrt((coords.x-p.x)**2 + (coords.y-p.y)**2) < 15) {\n',
        '                  const npos = [...q.answer_positions];\n',
        '                  const was = npos[i].is_correct;\n',
        '                  npos.forEach((pp,j) => { pp.is_correct = (j==i) ? !was : false; });\n',
        '                  setQuestions(questions.map(qq => qq.question_number==q.question_number\n',
        '                    ? {...qq, answer_positions: npos, correct_answer: !was ? p.option : ""} : qq));\n',
        '                  message.success(!was ? "标记第"+q.question_number+"题答案"+p.option : "取消标记");\n',
        '                  return;\n',
        '                }\n',
        '              }\n',
        '            }\n',
        '          }\n',
        '          let added = false;\n',
        '          for (const q of questions) {\n',
        '            if (q.answer_positions) {\n',
        '              for (const p of q.answer_positions) {\n',
        '                if (Math.abs(coords.x-p.x)<30 && Math.abs(coords.y-p.y)<30) {\n',
        '                  const opts = ["A","B","C","D","E","F","G","H"];\n',
        '                  const used = q.answer_positions.map(pp=>pp.option);\n',
        '                  const next = opts.find(o=>!used.includes(o)) || "A";\n',
        '                  const npos = [...q.answer_positions, {question_number: q.question_number, option: next, x: coords.x, y: coords.y, is_correct: false}];\n',
        '                  setQuestions(questions.map(qq => qq.question_number==q.question_number ? {...qq, answer_positions: npos} : qq));\n',
        '                  message.success("添加选项"+next); added = true; return;\n',
        '                }\n',
        '              }\n',
        '            }\n',
        '          }\n',
        '          if (added) return;\n',
        '          const qnum = questions.length+1;\n',
        '          setQuestions([...questions, {question_number: qnum, question_type:"single", options_count:4,\n',
        '            options:["A","B","C","D"], option_layout:"vertical", score:1.0,\n',
        '            x:coords.x-5, y:coords.y-5, width:10, height:10,\n',
        '            sort_order:questions.length, answer_positions:[{question_number:qnum, option:"A", x:coords.x, y:coords.y, is_correct:false}]} as any]);\n',
        '          message.success("新建第"+qnum+"题，可继续点击添加选项位置");\n',
        '          return;\n',
        '        }\n',
        '      }\n',
        '      message.warning("请在客观题区域内点击");\n',
        '      return;\n',
        '    }\n'
    ]
    lines[start:end] = new_lines
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"OK: Answer_mark handler replaced (lines {start+1}-{end})")
else:
    print(f"ERR: Handler not found")
