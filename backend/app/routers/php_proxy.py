"""
OnlineMark - PHP Bridge Proxy Router
Forwards all database-related routes to the PHP API on InfinityFree.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
import requests as http_requests
from app.config import settings

router = APIRouter()

async def _proxy(request: Request) -> Response:
    path = request.url.path
    query = request.url.query
    php_url = settings.PHP_API_URL.rstrip("/") + path
    if query:
        php_url += "?" + query

    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}

    try:
        resp = http_requests.request(
            method=request.method,
            url=php_url,
            data=body,
            headers=headers,
            timeout=60
        )
        content_type = resp.headers.get("content-type", "application/json")
        return Response(content=resp.content, status_code=resp.status_code, media_type=content_type)
    except Exception as e:
        return JSONResponse({"detail": f"PHP bridge error: {str(e)}"}, status_code=502)

# ─── Auth ────────────────────────────────────────────────
@router.api_route("/api/auth/login", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def auth_login(request: Request): return await _proxy(request)
@router.api_route("/api/auth/me", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def auth_me(request: Request): return await _proxy(request)
@router.api_route("/api/auth/password", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def auth_password(request: Request): return await _proxy(request)

# ─── Users ───────────────────────────────────────────────
@router.api_route("/api/users", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def users_root(request: Request): return await _proxy(request)
@router.api_route("/api/users/{path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def users_path(request: Request): return await _proxy(request)

# ─── Templates ───────────────────────────────────────────
@router.api_route("/api/templates", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def templates_root(request: Request): return await _proxy(request)
@router.api_route("/api/templates/{path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def templates_path(request: Request): return await _proxy(request)

# ─── Scan batches (DB CRUD only — upload/recognize stay in Python) ─
@router.api_route("/api/scan/batch", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def scan_batch_root(request: Request): return await _proxy(request)
@router.api_route("/api/scan/batch/{path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def scan_batch_path(request: Request): return await _proxy(request)

# ─── Scores ──────────────────────────────────────────────
@router.api_route("/api/scores", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def scores_root(request: Request): return await _proxy(request)
@router.api_route("/api/scores/{path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS"])
async def scores_path(request: Request): return await _proxy(request)
