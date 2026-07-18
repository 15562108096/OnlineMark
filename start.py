# -*- coding: utf-8 -*-
"""
云教学服务平台 - 启动脚本
同时启动后端API服务和前端开发服务器
"""
import subprocess
import sys
import os
import time
import shutil
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def start_backend():
    print("[后端] 启动API服务 (端口 8000)...")
    env = os.environ.copy()

    if not os.path.isdir(BACKEND_DIR):
        raise NotADirectoryError(f"后端目录不存在: {BACKEND_DIR}")

    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
        env=env
    )

def start_frontend():
    print("[前端] 启动开发服务器 (端口 3000)...")

    if not os.path.isdir(FRONTEND_DIR):
        raise NotADirectoryError(f"前端目录不存在: {FRONTEND_DIR}")

    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    if shutil.which(npm_cmd) is None and shutil.which("npm") is None:
        raise RuntimeError("未检测到 npm，请先安装 Node.js LTS")

    return subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR
    )

def main():
    print("=" * 50)
    print("  云教学服务平台 - Online Mark System")
    print("=" * 50)
    print()

    backend = start_backend()
    time.sleep(3)

    # Check backend health
    try:
        import urllib.request
        resp = urllib.request.urlopen("http://localhost:8000/", timeout=5)
        print(f"[后端] 启动成功! {json.loads(resp.read())}")
    except Exception as e:
        print(f"[后端] 启动中... ({e})")

    try:
        frontend = start_frontend()
    except Exception:
        backend.terminate()
        raise

    print()
    print("=" * 50)
    print("  服务已启动!")
    print("  前端: http://localhost:3000")
    print("  后端: http://localhost:8000")
    print("  超级管理员: 37108220071109031X / Zyw20071109")
    print("=" * 50)
    print("  按 Ctrl+C 停止所有服务")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend.terminate()
        frontend.terminate()
        print("服务已停止")

if __name__ == "__main__":
    main()
