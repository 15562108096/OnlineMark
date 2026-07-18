import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "frontend", "src", "pages", "TemplateEditorPage.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Check if answer_mark handler has the buggy version
# The buggy version creates a new Question on every click
# We need to fix it to add positions to existing questions

old_handler = """    if (mode === \"answer_mark\") {
      // Click to mark an answer position within an objective zone
      const objZones = zones.filter(z => z.zone_type === \"objective\");
      for (const z of objZones) {
        if (coords.x >= z.x && coords.x <= z.x + z.width && coords.y >= z.y && coords.y <= z.y + z.height) {
          const qnum = questions.length + 1;
          const optionLetters = [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\"];
          // Find next unused option letter for this question
          const existingPos = questions.filter(q => q.answer_positions).flatMap(q => q.answer_positions || []);
          const usedOptions = existingPos.map(p => p.option);
          const nextOption = optionLetters.find(o => !usedOptions.includes(o)) || \"A\";
          const pos = { question_number: qnum, option: nextOption, x: coords.x, y: coords.y, is_correct: false };
          setQuestions([...questions, {
            question_number: qnum,
            question_type: \"single\",
            options_count: 4,
            options: [\"A\",\"B\",\"C\",\"D\"],
            option_layout: \"vertical\",
            score: 1.0,
            x: coords.x - 5,
            y: coords.y - 5,
            width: 10,
            height: 10,
            sort_order: questions.length,
            answer_positions: [pos]
          } as any]);
          message.success(\"\u6807\u8bb0\u7b2c\" + qnum + \"\u9898\u9009\u9879\" + nextOption + \"\uff0c\u70b9\u51fb\u53ef\u5207\u6362\u4e3a\u6b63\u786e\u7b54\u6848\");
          return;
        }
      }
      message.warning(\"\u8bf7\u5148\u5728\u5ba2\u89c2\u9898\u533a\u57df\u5185\u70b9\u51fb\");
      return;
    }"""

new_handler = """    if (mode === \"answer_mark\") {
      const objZones = zones.filter(z => z.zone_type === \"objective\");
      for (const z of objZones) {
        if (coords.x >= z.x && coords.x <= z.x + z.width && coords.y >= z.y && coords.y <= z.y + z.height) {
          // Check if clicking on an existing answer position (to toggle correct)
          let found = false;
          for (const q of questions) {
            if (q.answer_positions) {
              for (let i = 0; i < q.answer_positions.length; i++) {
                const pos = q.answer_positions[i];
                const dist = Math.sqrt((coords.x - pos.x) ** 2 + (coords.y - pos.y) ** 2);
                if (dist < 15) {
                  const newPositions = [...q.answer_positions];
                  const wasCorrect = newPositions[i].is_correct;
                  newPositions.forEach((p, j) => { p.is_correct = (j === i) ? !wasCorrect : false; });
                  setQuestions(questions.map(qq => qq.question_number === q.question_number
                    ? { ...qq, answer_positions: newPositions, correct_answer: !wasCorrect ? pos.option : \"\" } : qq));
                  message.success(!wasCorrect ? \"\u6807\u8bb0\u7b2c\" + q.question_number + \"\u9898\u6b63\u786e\u7b54\u6848\u4e3a\" + pos.option : \"\u53d6\u6d88\u7b2c\" + q.question_number + \"\u9898\u6b63\u786e\u7b54\u6848\");
                  found = true; return;
                }
              }
            }
          }
          if (found) return;
          
          // Check if near an existing question (within 30px) -> add position to it
          const optionLetters = [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\"];
          let addedToExisting = false;
          for (const q of questions) {
            if (q.answer_positions) {
              for (const pos of q.answer_positions) {
                if (Math.abs(coords.x - pos.x) < 30 && Math.abs(coords.y - pos.y) < 30) {
                  const newPositions = [...q.answer_positions];
                  const usedOptions = newPositions.map(p => p.option);
                  const nextOpt = optionLetters.find(o => !usedOptions.includes(o)) || \"A\";
                  newPositions.push({ question_number: q.question_number, option: nextOpt, x: coords.x, y: coords.y, is_correct: false });
                  setQuestions(questions.map(qq => qq.question_number === q.question_number
                    ? { ...qq, answer_positions: newPositions } : qq));
                  message.success(\"\u6dfb\u52a0\u9009\u9879\" + nextOpt);
                  addedToExisting = true; return;
                }
              }
            }
          }
          if (addedToExisting) return;
          
          // Create new question with this position
          const qnum = questions.length + 1;
          const pos = { question_number: qnum, option: \"A\", x: coords.x, y: coords.y, is_correct: false };
          setQuestions([...questions, {
            question_number: qnum, question_type: \"single\", options_count: 4,
            options: [\"A\",\"B\",\"C\",\"D\"], option_layout: \"vertical\", score: 1.0,
            x: coords.x - 5, y: coords.y - 5, width: 10, height: 10,
            sort_order: questions.length, answer_positions: [pos]
          } as any]);
          message.success(\"\u521b\u5efa\u7b2c\" + qnum + \"\u9898\uff0c\u70b9\u51fb\u53ef\u6dfb\u52a0\u66f4\u591a\u9009\u9879\u4f4d\u7f6e\");
          return;
        }
      }
      message.warning(\"\u8bf7\u5728\u5ba2\u89c2\u9898\u533a\u57df\u5185\u70b9\u51fb\");
      return;
    }"""

if old_handler in c:
    c = c.replace(old_handler, new_handler)
    print("answer_mark handler fixed - no more duplicate questions")
else:
    print("WARN: answer_mark handler pattern not found")
    # Try to find what's different - check for key phrases
    for phrase in ["answer_mark", "coords.x >= z.x", "optionLetters", "is_correct"]:
        if phrase in c:
            idx = c.find(phrase)
            print(f"  Found '{phrase}' at position {idx}")
            print(f"  Context: ...{c[idx-40:idx+80]}...")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# Also check types/index.ts for answer_positions
type_path = os.path.join(base, "frontend", "src", "types", "index.ts")
with open(type_path, "r", encoding="utf-8") as f:
    t = f.read()

if "answer_positions" not in t:
    print("FIX: Adding answer_positions to Question type")
    old_type = "export interface Question {\n  id?: string;\n  question_number: number;\n  question_type: \"single\" | \"multiple\" | \"judge\";\n  options_count: number;\n  options?: string[];\n  option_layout: \"horizontal\" | \"vertical\";\n  score: number;\n  correct_answer?: string;\n  x?: number;\n  y?: number;\n  width?: number;\n  height?: number;\n  sort_order?: number;\n}"
    new_type = "export interface AnswerPosition {\n  question_number: number;\n  option: string;\n  x: number;\n  y: number;\n  is_correct?: boolean;\n}\n\nexport interface Question {\n  id?: string;\n  question_number: number;\n  question_type: \"single\" | \"multiple\" | \"judge\";\n  options_count: number;\n  options?: string[];\n  option_layout: \"horizontal\" | \"vertical\";\n  score: number;\n  correct_answer?: string;\n  x?: number;\n  y?: number;\n  width?: number;\n  height?: number;\n  sort_order?: number;\n  answer_positions?: AnswerPosition[];\n}"
    if old_type in t:
        t = t.replace(old_type, new_type)
        with open(type_path, "w", encoding="utf-8") as f:
            f.write(t)
        print("  types/index.ts updated")
    else:
        print("  WARN: Question type not found in types.ts")
else:
    print("OK: answer_positions already in Question type")

if "AnswerPosition" not in t:
    print("WARN: AnswerPosition interface not found")
else:
    print("OK: AnswerPosition interface exists")
