import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "frontend", "src", "index.css")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# The old login CSS block to replace
old_start = ".login-container {"
old_end = "role-btn.active {\n  border-color: #1677ff;\n  background: #f0f5ff;\n  color: #1677ff;\n  font-weight: 600;\n}"

new_css = """.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  position: relative;
}

.login-card {
  width: 400px;
  padding: 48px 40px 36px;
  background: #fff;
  z-index: 1;
  position: relative;
}

.login-card h1 {
  text-align: center;
  font-size: 24px;
  font-weight: 400;
  color: #202124;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.login-card > p {
  text-align: center;
  color: #5f6368;
  margin-bottom: 32px;
  font-size: 16px;
  font-weight: 400;
}

.role-selector {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  border: 1px solid #dadce0;
  border-radius: 8px;
  overflow: hidden;
}

.role-btn {
  flex: 1;
  padding: 10px 8px;
  border: none;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 400;
  transition: all 0.15s;
  text-align: center;
  color: #5f6368;
  border-right: 1px solid #dadce0;
}

.role-btn:last-child {
  border-right: none;
}

.role-btn:hover {
  background: #f8f9fa;
  color: #202124;
}

.role-btn.active {
  background: #e8f0fe;
  color: #1a73e8;
  font-weight: 500;
}"""

# Find where the old login CSS starts and ends
idx_start = c.find(old_start)
if idx_start >= 0:
    idx_end = c.find(old_end, idx_start)
    if idx_end >= 0:
        idx_end += len(old_end)
        c = c[:idx_start] + new_css + c[idx_end:]
        print("Login CSS replaced with Google-like design")
    else:
        print("WARN: end of login CSS not found")
else:
    print("WARN: start of login CSS not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("CSS fix complete")
