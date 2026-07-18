<?php
/**
 * OnlineMark - MySQL Database Bridge API for InfinityFree
 * Routes all DB operations from the Python backend through PHP.
 */
header("Content-Type: application/json; charset=utf-8");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") { http_response_code(200); exit; }

$DB_HOST = getenv("DB_HOST") ?: "sql306.infinityfree.com";
$DB_USER = getenv("DB_USER") ?: "if0_39743066";
$DB_PASS = getenv("DB_PASSWORD") ?: "DouglasJP2026";
$DB_NAME = getenv("DB_NAME") ?: "if0_39743066_onlinemark";

function getDB(): mysqli {
    global $DB_HOST, $DB_USER, $DB_PASS, $DB_NAME;
    $conn = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
    if ($conn->connect_error) { http_response_code(500); echo json_encode(["error" => "DB: ".$conn->connect_error]); exit; }
    $conn->set_charset("utf8mb4"); return $conn;
}
function jsonInput(): array { return json_decode(file_get_contents("php://input"), true) ?: []; }
function jsonExit($d, int $c=200): void { http_response_code($c); echo json_encode($d, JSON_UNESCAPED_UNICODE); exit; }
function uuid(): string { return sprintf("%04x%04x-%04x-%04x-%04x-%04x%04x%04x", mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0x0fff)|0x4000, mt_rand(0,0x3fff)|0x8000, mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff)); }

$method = $_SERVER["REQUEST_METHOD"];
$uri = rtrim(parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH), "/");
if (preg_match("#^/api/(.+)#", $uri, $m)) $uri = "/".$m[1];
$uri = rtrim($uri, "/") ?: "/";

try {
    $db = getDB();

    // ─── Auth: login ──────────────────────────────────
    if (preg_match("#^/auth/login$#", $uri) && $method === "POST") {
        $input = jsonInput();
        $u = $db->real_escape_string($input["username"] ?? "");
        $r = $db->query("SELECT * FROM users WHERE username = '$u' AND is_active = 1");
        $user = $r ? $r->fetch_assoc() : null;
        if (!$user || !password_verify($input["password"] ?? "", $user["password_hash"])) {
            jsonExit(["detail" => "用户名或密码错误"], 401);
        }
        $header = rtrim(base64_encode('{"alg":"HS256","typ":"JWT"}'), "=");
        $secret = "onlinemark-2026-jwt-secret";
        $payload = rtrim(base64_encode(json_encode(["sub"=>$user["id"],"role"=>$user["role"],"exp"=>time()+28800])), "=");
        $sig = rtrim(base64_encode(hash_hmac("sha256", "$header.$payload", $secret, true)), "=");
        $token = "$header.$payload.$sig";
        jsonExit(["access_token"=>$token,"token_type"=>"bearer","user"=>[
            "id"=>$user["id"],"username"=>$user["username"],"real_name"=>$user["real_name"],
            "role"=>$user["role"],"email"=>$user["email"],"phone"=>$user["phone"],
            "is_active"=>(bool)$user["is_active"],"created_at"=>$user["created_at"]
        ]]);
    }

    // ─── Auth: me ─────────────────────────────────────
    if (preg_match("#^/auth/me$#", $uri) && $method === "GET") {
        $auth = $_SERVER["HTTP_AUTHORIZATION"] ?? "";
        if (!preg_match("/^Bearer\s+(.+)$/i", $auth, $m)) jsonExit(["detail"=>"未登录"], 401);
        $parts = explode(".", $m[1]);
        if (count($parts) !== 3) jsonExit(["detail"=>"令牌无效"], 401);
        $payload = json_decode(base64_decode($parts[1]), true);
        if (!$payload || ($payload["exp"]??0) < time()) jsonExit(["detail"=>"令牌过期"], 401);
        $uid = $db->real_escape_string($payload["sub"]);
        $r = $db->query("SELECT * FROM users WHERE id = '$uid' AND is_active = 1");
        $user = $r ? $r->fetch_assoc() : null;
        if (!$user) jsonExit(["detail"=>"用户不存在"], 401);
        jsonExit(["id"=>$user["id"],"username"=>$user["username"],"real_name"=>$user["real_name"],
            "role"=>$user["role"],"email"=>$user["email"],"phone"=>$user["phone"],
            "is_active"=>(bool)$user["is_active"],"created_at"=>$user["created_at"]]);
    }

    // ─── Seed: init admin ─────────────────────────────
    if (preg_match("#^/seed$#", $uri) && $method === "POST") {
        $input = jsonInput();
        $username = $input["username"] ?? "37108220071109031X";
        $password = $input["password"] ?? "Zyw20071109";
        $realName = $input["real_name"] ?? "超级管理员";
        $u = $db->real_escape_string($username);
        $ex = $db->query("SELECT id FROM users WHERE username = '$u'");
        if ($ex && $ex->num_rows > 0) jsonExit(["message" => "管理员已存在，跳过"]);
        $id = uuid();
        $hash = password_hash($password, PASSWORD_BCRYPT);
        $rn = $db->real_escape_string($realName);
        $db->query("INSERT INTO users (id, username, password_hash, real_name, role, is_active, created_at) VALUES ('$id', '$u', '$hash', '$rn', 'super_admin', 1, NOW())");
        jsonExit(["message" => "管理员创建成功", "username" => $username]);
    }

    // ─── Templates: list ──────────────────────────────
    if (preg_match("#^/templates/?$#", $uri) && $method === "GET") {
        $r = $db->query("SELECT * FROM templates ORDER BY created_at DESC");
        $list = [];
        while ($row = $r->fetch_assoc()) {
            $tid = $row["id"];
            $mk = $db->query("SELECT id,point_index,x,y,width,height,shape,label,COALESCE(page_number,0) pn FROM template_markers WHERE template_id='$tid'");
            $markers=[]; while($m=$mk->fetch_assoc()) $markers[]=["id"=>$m["id"],"point_index"=>intval($m["point_index"]),"x"=>floatval($m["x"]),"y"=>floatval($m["y"]),"width"=>floatval($m["width"]),"height"=>floatval($m["height"]),"shape"=>$m["shape"],"label"=>$m["label"],"page_number"=>intval($m["pn"])];
            $zr = $db->query("SELECT * FROM template_zones WHERE template_id='$tid'");
            $zones=[]; while($z=$zr->fetch_assoc()) $zones[]=["id"=>$z["id"],"zone_type"=>$z["zone_type"],"label"=>$z["label"],"x"=>floatval($z["x"]),"y"=>floatval($z["y"]),"width"=>floatval($z["width"]),"height"=>floatval($z["height"]),"sort_order"=>intval($z["sort_order"]??0),"page_number"=>intval($z["page_number"]??0),"config"=>$z["config"]?json_decode($z["config"],true):null,"answer_positions"=>$z["answer_positions"]?json_decode($z["answer_positions"],true):null];
            $qr = $db->query("SELECT * FROM objective_questions WHERE template_id='$tid' ORDER BY sort_order");
            $questions=[]; while($q=$qr->fetch_assoc()) $questions[]=["id"=>$q["id"],"question_number"=>intval($q["question_number"]),"question_type"=>$q["question_type"],"options_count"=>intval($q["options_count"]),"options"=>$q["options"]?json_decode($q["options"],true):null,"option_layout"=>$q["option_layout"],"score"=>floatval($q["score"]),"x"=>$q["x"]?floatval($q["x"]):null,"y"=>$q["y"]?floatval($q["y"]):null,"width"=>$q["width"]?floatval($q["width"]):null,"height"=>$q["height"]?floatval($q["height"]):null,"correct_answer"=>$q["correct_answer"],"answer_positions"=>$q["answer_positions"]?json_decode($q["answer_positions"],true):null,"sort_order"=>intval($q["sort_order"]??0)];
            $list[]=["id"=>$row["id"],"name"=>$row["name"],"description"=>$row["description"],"subject"=>$row["subject"],"grade"=>$row["grade"],"exam_name"=>$row["exam_name"],"image_path"=>$row["image_path"]??"","image_width"=>$row["image_width"]?intval($row["image_width"]):null,"image_height"=>$row["image_height"]?intval($row["image_height"]):null,"total_score"=>floatval($row["total_score"]??0),"objective_score"=>floatval($row["objective_score"]??0),"subjective_score"=>floatval($row["subjective_score"]??0),"info_method"=>$row["info_method"]??"omr","status"=>$row["status"]??"draft","created_at"=>$row["created_at"],"markers"=>$markers,"zones"=>$zones,"questions"=>$questions];
        }
        jsonExit($list);
    }

    // ─── Templates: create ────────────────────────────
    if (preg_match("#^/templates/?$#", $uri) && $method === "POST") {
        $input = jsonInput();
        $id = uuid();
        $n = $db->real_escape_string($input["name"]??"");
        $d = $db->real_escape_string($input["description"]??"");
        $s = $db->real_escape_string($input["subject"]??"");
        $g = $db->real_escape_string($input["grade"]??"");
        $e = $db->real_escape_string($input["exam_name"]??"");
        $im = $db->real_escape_string($input["info_method"]??"omr");
        $tp = intval($input["total_pages"]??1);
        $pp = $db->real_escape_string($input["pdf_path"]??"");
        $db->query("INSERT INTO templates (id,name,description,subject,grade,exam_name,image_path,pdf_path,total_pages,info_method,status,created_at) VALUES ('$id','$n','$d','$s','$g','$e','$pp','$pp',$tp,'$im','draft',NOW())");
        if (isset($input["markers"])) foreach($input["markers"] as $mk) {
            $mi=uuid(); $pi=intval($mk["point_index"]??0); $mx=floatval($mk["x"]??0); $my=floatval($mk["y"]??0);
            $mw=floatval($mk["width"]??0); $mh=floatval($mk["height"]??0);
            $sh=$db->real_escape_string($mk["shape"]??"circle"); $lb=$db->real_escape_string($mk["label"]??"");
            $db->query("INSERT INTO template_markers (id,template_id,point_index,x,y,width,height,shape,label) VALUES ('$mi','$id',$pi,$mx,$my,$mw,$mh,'$sh','$lb')");
        }
        if (isset($input["zones"])) foreach($input["zones"] as $z) {
            $zi=uuid(); $zt=$db->real_escape_string($z["zone_type"]??"objective"); $zl=$db->real_escape_string($z["label"]??"");
            $zx=floatval($z["x"]??0); $zy=floatval($z["y"]??0); $zw=floatval($z["width"]??0); $zh=floatval($z["height"]??0);
            $so=intval($z["sort_order"]??0); $ap=isset($z["answer_positions"])?$db->real_escape_string(json_encode($z["answer_positions"],JSON_UNESCAPED_UNICODE)):"null";
            $db->query("INSERT INTO template_zones (id,template_id,zone_type,label,x,y,width,height,sort_order,answer_positions) VALUES ('$zi','$id','$zt','$zl',$zx,$zy,$zw,$zh,$so,'$ap')");
        }
        if (isset($input["questions"])) foreach($input["questions"] as $q) {
            $qi=uuid(); $qn=intval($q["question_number"]??0); $qt=$db->real_escape_string($q["question_type"]??"single");
            $oc=intval($q["options_count"]??4); $opts=isset($q["options"])?$db->real_escape_string(json_encode($q["options"],JSON_UNESCAPED_UNICODE)):"null";
            $ol=$db->real_escape_string($q["option_layout"]??"vertical"); $sc=floatval($q["score"]??1);
            $qx=$q["x"]!==null?floatval($q["x"]):"null"; $qy=$q["y"]!==null?floatval($q["y"]):"null";
            $qw=$q["width"]!==null?floatval($q["width"]):"null"; $qh=$q["height"]!==null?floatval($q["height"]):"null";
            $ca=$db->real_escape_string($q["correct_answer"]??"");
            $ap2=isset($q["answer_positions"])?$db->real_escape_string(json_encode($q["answer_positions"],JSON_UNESCAPED_UNICODE)):"null";
            $so2=intval($q["sort_order"]??0);
            $db->query("INSERT INTO objective_questions (id,template_id,question_number,question_type,options_count,options,option_layout,score,x,y,width,height,correct_answer,answer_positions,sort_order) VALUES ('$qi','$id',$qn,'$qt',$oc,'$opts','$ol',$sc,$qx,$qy,$qw,$qh,'$ca','$ap2',$so2)");
        }
        jsonExit(["message"=>"模板创建成功","template"=>["id"=>$id,"name"=>$n]]);
    }

    // ─── Templates: get ───────────────────────────────
    if (preg_match("#^/templates/([^/]+)$#", $uri, $m) && $method === "GET") {
        $tid = $db->real_escape_string($m[1]);
        $r = $db->query("SELECT * FROM templates WHERE id = '$tid'");
        $t = $r->fetch_assoc();
        if (!$t) jsonExit(["detail"=>"模板不存在"],404);
        // Build full template with markers, zones, questions (reuse query logic)
        $tid = $t["id"]; $mk=$db->query("SELECT * FROM template_markers WHERE template_id='$tid'");
        $markers=[]; while($m2=$mk->fetch_assoc()) $markers[]=["id"=>$m2["id"],"point_index"=>intval($m2["point_index"]),"x"=>floatval($m2["x"]),"y"=>floatval($m2["y"]),"width"=>floatval($m2["width"]??0),"height"=>floatval($m2["height"]??0),"shape"=>$m2["shape"],"label"=>$m2["label"],"page_number"=>intval($m2["page_number"]??0)];
        $zr=$db->query("SELECT * FROM template_zones WHERE template_id='$tid'"); $zones=[];
        while($z=$zr->fetch_assoc()) $zones[]=["id"=>$z["id"],"zone_type"=>$z["zone_type"],"label"=>$z["label"],"x"=>floatval($z["x"]),"y"=>floatval($z["y"]),"width"=>floatval($z["width"]),"height"=>floatval($z["height"]),"sort_order"=>intval($z["sort_order"]??0),"page_number"=>intval($z["page_number"]??0),"config"=>$z["config"]?json_decode($z["config"],true):null,"answer_positions"=>$z["answer_positions"]?json_decode($z["answer_positions"],true):null];
        $qr=$db->query("SELECT * FROM objective_questions WHERE template_id='$tid' ORDER BY sort_order"); $questions=[];
        while($q=$qr->fetch_assoc()) $questions[]=["id"=>$q["id"],"question_number"=>intval($q["question_number"]),"question_type"=>$q["question_type"],"options_count"=>intval($q["options_count"]),"options"=>$q["options"]?json_decode($q["options"],true):null,"option_layout"=>$q["option_layout"],"score"=>floatval($q["score"]),"x"=>$q["x"]?floatval($q["x"]):null,"y"=>$q["y"]?floatval($q["y"]):null,"width"=>$q["width"]?floatval($q["width"]):null,"height"=>$q["height"]?floatval($q["height"]):null,"correct_answer"=>$q["correct_answer"],"answer_positions"=>$q["answer_positions"]?json_decode($q["answer_positions"],true):null,"sort_order"=>intval($q["sort_order"]??0)];
        jsonExit(["id"=>$t["id"],"name"=>$t["name"],"description"=>$t["description"],"subject"=>$t["subject"],"grade"=>$t["grade"],"exam_name"=>$t["exam_name"],"image_path"=>$t["image_path"]??"","image_width"=>$t["image_width"]?intval($t["image_width"]):null,"image_height"=>$t["image_height"]?intval($t["image_height"]):null,"total_score"=>floatval($t["total_score"]??0),"objective_score"=>floatval($t["objective_score"]??0),"subjective_score"=>floatval($t["subjective_score"]??0),"info_method"=>$t["info_method"]??"omr","status"=>$t["status"]??"draft","created_at"=>$t["created_at"],"markers"=>$markers,"zones"=>$zones,"questions"=>$questions]);
    }

    // ─── Health ────────────────────────────────────────
    if (preg_match("#^/?$#", $uri) || $uri === "/health") {
        jsonExit(["name"=>"OnlineMark PHP Bridge","status"=>"running"]);
    }

    // ─── Fallback ──────────────────────────────────────
    jsonExit(["detail"=>"Not Found","uri"=>$uri], 404);

} catch (Throwable $e) {
    jsonExit(["detail"=>"Error: ".$e->getMessage()], 500);
}
