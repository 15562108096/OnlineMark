import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
changes = []

# 1. LoginPage - merge roles
path = os.path.join(base, "frontend", "src", "pages", "LoginPage.tsx")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()
old = "{ key: \"super_admin\", label: \"超级管理员\" },\n  { key: \"admin\", label: \"管理员\" }"
new = "{ key: \"admin\", label: \"管理员\" }"
c = c.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
changes.append("LoginPage merged roles")

# 2. Backend auth - allow super_admin as admin
path = os.path.join(base, "backend", "app", "routers", "auth.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()
old = '    if user.role.value != req.role:\n        raise HTTPException(status_code=401, detail=f"身份不匹配，该账号不是{req.role}身份")'
new = '    if user.role.value == "super_admin" and req.role == "admin":\n        pass\n    elif user.role.value != req.role:\n        raise HTTPException(status_code=401, detail=f"身份不匹配，该账号不是{req.role}身份")'
c = c.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
changes.append("Backend auth allows super_admin login")

# 3. AppLayout footer
path = os.path.join(base, "frontend", "src", "components", "AppLayout.tsx")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("云教学服务平台 &copy; {new Date().getFullYear()} - 让教学更智能", "&copy; 2025 加斯顿之洞 版权所有")
c = c.replace('<span style={{ fontSize: 20, fontWeight: 700, color: "#1677ff" }}>云教学</span>', '<span style={{ fontSize: 20, fontWeight: 700, color: "#1677ff" }}>加斯顿之洞</span>')
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
changes.append("AppLayout footer + logo")

# 4. Dashboard role display
path = os.path.join(base, "frontend", "src", "pages", "DashboardPage.tsx")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()
old = '?role === "super_admin" ? "超级管理员" :\n           user?.role === "admin" ? "管理员" :\n           user?.role === "teacher" ? "教师" : "学生"'
new = '?role === "super_admin" || user?.role === "admin" ? "管理员" : user?.role === "teacher" ? "教师" : "学生"'
c = c.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
changes.append("Dashboard role display")

for ch in changes:
    print(f"  {ch}")
print(f"Done: {len(changes)} changes")
