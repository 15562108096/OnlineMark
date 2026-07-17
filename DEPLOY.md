# 云教学服务平台 - 部署与迁移指南

本文档针对 `services/OnlineMark`，重点说明数据库部署与迁移。

## 1. 本地准备（必须）

1. 进入项目目录：
   - `cd services/OnlineMark`
2. 后端复制环境变量模板：
   - `cp backend/.env.example backend/.env`（Windows 可手动复制）
3. 编辑 `backend/.env`，至少设置：
   - `DB_TYPE`（`sqlite` 或 `mysql`）
   - `SECRET_KEY`
   - `ADMIN_USERNAME` / `ADMIN_PASSWORD`

## 2. 数据库部署

### 2.1 SQLite（简单，单机）

适用于小规模、单机部署。

`backend/.env` 示例：

```env
DB_TYPE=sqlite
DB_SQLITE_PATH=./online_mark.db
```

初始化数据库并创建管理员：

```bash
cd backend
python seed.py
```

### 2.2 MySQL（推荐服务器）

1. 在 MySQL 创建库与用户：

```sql
CREATE DATABASE onlinemark DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'onlinemark'@'%' IDENTIFIED BY 'StrongPassword!';
GRANT ALL PRIVILEGES ON onlinemark.* TO 'onlinemark'@'%';
FLUSH PRIVILEGES;
```

2. 配置 `backend/.env`：

```env
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=onlinemark
DB_PASSWORD=StrongPassword!
DB_NAME=onlinemark
SECRET_KEY=replace-with-long-random-secret
DEBUG=False
```

3. 初始化表结构与管理员：

```bash
cd backend
python seed.py
```

## 3. 启动方式

### 3.1 开发一键启动（本地）

在 `services/OnlineMark` 执行：

```bash
python start.py
```

### 3.2 生产启动（仅后端）

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

建议生产使用进程守护（如 `systemd` / `supervisor` / `pm2`）。

## 4. 迁移到服务器（你后续转移时按此执行）

## 4.1 迁移代码

推荐 Git：

```bash
git clone <your-repo-url>
cd OnlineMark/services/OnlineMark
```

也可直接压缩上传 `services/OnlineMark` 目录。

## 4.2 部署后端（Linux 示例）

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入生产数据库与密钥
python seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 4.3 前端部署

```bash
cd ../frontend
npm install
npm run build
```

将 `frontend/dist` 交给 Nginx 托管，API 反向代理到 `http://127.0.0.1:8000`。

## 4.4 旧库数据迁移

若你从旧服务器迁移 MySQL：

```bash
# 旧服务器导出
mysqldump -u onlinemark -p onlinemark > onlinemark.sql

# 新服务器导入
mysql -u onlinemark -p onlinemark < onlinemark.sql
```

若你从 SQLite 迁移：

1. 停服务，复制 `backend/online_mark.db` 到新服务器。
2. 新服务器 `.env` 保持：`DB_TYPE=sqlite`，并指向该文件。

## 5. 上线前检查

1. `DEBUG=False`
2. `SECRET_KEY` 已替换为高强度随机值
3. 管理员初始密码已修改
4. 数据库已完成备份策略（至少每日）
5. 服务器放行端口并配置 HTTPS
