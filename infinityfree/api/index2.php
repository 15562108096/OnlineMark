<?php
header("Content-Type: application/json; charset=utf-8");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") { http_response_code(200); exit; }

$DB_HOST = getenv("DB_HOST") ?: "sql306.infinityfree.com";
$DB_USER = getenv("DB_USER") ?: "if0_39743066";
$DB_PASS = getenv("DB_PASSWORD") ?: "DouglasJP2026";
$DB_NAME = getenv("DB_NAME") ?: "if0_39743066_onlinemark";
$UPLOAD_DIR = __DIR__ . "/../uploads";

function getDB(): mysqli {
    global $DB_HOST, $DB_USER, $DB_PASS, $DB_NAME;
    $conn = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
    if ($conn->connect_error) { http_response_code(500); echo json_encode(["error"=>"DB: ".$conn->connect_error]); exit; }
    $conn->set_charset("utf8mb4"); return $conn;
}
function jsonInput(): array { return json_decode(file_get_contents("php://input"), true) ?: []; }
function jsonExit($d, int $c=200): void { http_response_code($c); echo json_encode($d, JSON_UNESCAPED_UNICODE); exit; }
function uuid(): string { return sprintf("%04x%04x-%04x-%04x-%04x-%04x%04x%04x", mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0x0fff)|0x4000, mt_rand(0,0x3fff)|0x8000, mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff)); }
function authUser(mysqli $db): array {
    $auth = $_SERVER["HTTP_AUTHORIZATION"] ?? "";
    if (!preg_match("/^Bearer\s+(.+)$/i", $auth, $m)) jsonExit(["detail"=>"未登录"], 401);
    $parts = explode(".", $m[1]); if (count($parts)!==3) jsonExit(["detail"=>"令牌无效"], 401);
    $payload = json_decode(base64_decode($parts[1]), true);
    if (!$payload || ($payload["exp"]??0) < time()) jsonExit(["detail"=>"令牌过期"], 401);
    $uid = $db->real_escape_string($payload["sub"]);
    $r = $db->query("SELECT * FROM users WHERE id = '$uid' AND is_active = 1");
    $u = $r ? $r->fetch_assoc() : null;
    if (!$u) jsonExit(["detail"=>"用户不存在"], 401);
    return $u;
}
function mkToken(array $user): string {
    $header = rtrim(base64_encode('{"alg":"HS256","typ":"JWT"}'), "=");
    $secret = getenv("SECRET_KEY") ?: "onlinemark-2026-jwt-secret";
    $payload = rtrim(base64_encode(json_encode(["sub"=>$user["id"],"role"=>$user["role"],"exp"=>time()+28800])), "=");
    $sig = rtrim(base64_encode(hash_hmac("sha256", "$header.$payload", $secret, true)), "=");
    return "$header.$payload.$sig";
}
function userDict(array $u): array {
    return ["id"=>$u["id"],"username"=>$u["username"],"real_name"=>$u["real_name"],"role"=>$u["role"],"email"=>$u["email"],"phone"=>$u["phone"],"is_active"=>(bool)$u["is_active"],"created_at"=>$u["created_at"],"created_by"=>$u["created_by"]??null];
}

$method = $_SERVER["REQUEST_METHOD"];
$uri = rtrim(parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH), "/");
if (preg_match("#^/api/(.+)#", $uri, $m)) $uri = "/".$m[1];
$uri = rtrim($uri, "/") ?: "/";

try { $db = getDB();
