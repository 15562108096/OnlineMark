"""
OnlineMark - Database Bridge Module
Replaces SQLAlchemy with HTTP calls to the PHP API on InfinityFree.
"""
import os
import json
import requests
from typing import Optional, Any
from datetime import datetime

PHP_API_URL = os.environ.get(
    "PHP_API_URL",
    "https://if0-39743066.ix-infinity.com"  # CHANGE THIS to your infinityfree domain
)

def _url(path: str) -> str:
    return PHP_API_URL.rstrip("/") + "/api" + path

def _headers(token: Optional[str] = None) -> dict:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    return h

def _get(path: str, token: Optional[str] = None) -> Any:
    resp = requests.get(_url(path), headers=_headers(token), timeout=30)
    if resp.status_code >= 400:
        raise Exception(f"PHP API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if isinstance(data, dict) and "detail" in data:
        from fastapi import HTTPException
        raise HTTPException(status_code=resp.status_code, detail=data["detail"])
    return data

def _post(path: str, body: dict, token: Optional[str] = None) -> Any:
    resp = requests.post(_url(path), json=body, headers=_headers(token), timeout=30)
    if resp.status_code >= 400:
        raise Exception(f"PHP API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if isinstance(data, dict) and "detail" in data:
        from fastapi import HTTPException
        raise HTTPException(status_code=resp.status_code, detail=data["detail"])
    return data

def _put(path: str, body: dict, token: Optional[str] = None) -> Any:
    resp = requests.put(_url(path), json=body, headers=_headers(token), timeout=30)
    if resp.status_code >= 400:
        raise Exception(f"PHP API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if isinstance(data, dict) and "detail" in data:
        from fastapi import HTTPException
        raise HTTPException(status_code=resp.status_code, detail=data["detail"])
    return data

def _delete(path: str, token: Optional[str] = None) -> Any:
    resp = requests.delete(_url(path), headers=_headers(token), timeout=30)
    if resp.status_code >= 400:
        raise Exception(f"PHP API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if isinstance(data, dict) and "detail" in data:
        from fastapi import HTTPException
        raise HTTPException(status_code=resp.status_code, detail=data["detail"])
    return data

# ─── Auth ────────────────────────────────────────────────
def auth_login(username: str, password: str, role: str) -> dict:
    return _post("/auth/login", {"username": username, "password": password, "role": role})

def auth_get_me(token: str) -> dict:
    return _get("/auth/me", token)

# ─── Users ───────────────────────────────────────────────
def users_list(token: str, role: Optional[str] = None) -> list:
    path = "/users" + (f"?role={role}" if role else "")
    return _get(path, token)

def users_create(token: str, data: dict) -> dict:
    return _post("/users", data, token)

def users_delete(token: str, user_id: str) -> dict:
    return _delete(f"/users/{user_id}", token)

def users_toggle_active(token: str, user_id: str) -> dict:
    return _put(f"/users/{user_id}/toggle-active", {}, token)

def users_teachers(token: str) -> list:
    return _get("/users/teachers", token)

# ─── Templates ───────────────────────────────────────────
def templates_list(token: str) -> list:
    return _get("/templates", token)

def templates_get(token: str, template_id: str) -> dict:
    return _get(f"/templates/{template_id}", token)

def templates_create(token: str, data: dict) -> dict:
    return _post("/templates", data, token)

def templates_update(token: str, template_id: str, data: dict) -> dict:
    return _put(f"/templates/{template_id}", data, token)

def templates_delete(token: str, template_id: str) -> dict:
    return _delete(f"/templates/{template_id}", token)

# ─── Scan Batches ────────────────────────────────────────
def scan_batches_list(token: str) -> list:
    return _get("/scan/batch", token)

def scan_batch_create(token: str, data: dict) -> dict:
    return _post("/scan/batch", data, token)

def scan_batch_get(token: str, batch_id: str) -> dict:
    return _get(f"/scan/batch/{batch_id}", token)

# ─── Scores ──────────────────────────────────────────────
def scores_calculate(token: str, batch_id: str) -> dict:
    return _post(f"/scores/calculate/{batch_id}", {}, token)

def scores_batch(token: str, batch_id: str) -> list:
    return _get(f"/scores/batch/{batch_id}", token)

def scores_statistics(token: str, batch_id: str) -> dict:
    return _get(f"/scores/statistics/{batch_id}", token)

def scores_export(token: str, batch_id: str) -> dict:
    return _get(f"/scores/export/{batch_id}", token)
