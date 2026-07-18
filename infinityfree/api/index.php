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

$DB_HOST = getenv("DB_HOST") ?: "localhost";
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
// Strip subdirectory prefix if present
if (preg_match("#^/services/OnlineMark/api/(.+)#", $uri, $m)) $uri = "/".$m[1];
elseif (preg_match("#^/api/(.+)#", $uri, $m)) $uri = "/".$m[1];
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

    // ─── Grading: tasks ──────────────────────────────
    if (preg_match("#^/grading/task/?$#", $uri) && $method === "GET") {
        $r = $db->query("SELECT * FROM grading_tasks ORDER BY created_at DESC");
        $list = [];
        while ($row = $r->fetch_assoc()) {
            $tid = $row["id"];
            $a = $db->query("SELECT id, teacher_id, question_number, total_count, graded_count, status FROM grading_assignments WHERE task_id = '$tid'");
            $assignments = [];
            while ($as = $a->fetch_assoc()) $assignments[] = $as;
            $list[] = [
                "id" => $row["id"], "name" => $row["name"],
                "batch_id" => $row["batch_id"], "template_id" => $row["template_id"],
                "status" => $row["status"], "total_subjective" => intval($row["total_subjective"]),
                "graded_count" => intval($row["graded_count"]),
                "threshold" => floatval($row["threshold"]),
                "created_at" => $row["created_at"],
                "assignments" => $assignments
            ];
        }
        jsonExit($list);
    }
    if (preg_match("#^/grading/task/?$#", $uri) && $method === "POST") {
        $input = jsonInput();
        $id = uuid();
        $n = $db->real_escape_string($input["name"]??"");
        $bid = $db->real_escape_string($input["batch_id"]??"");
        $tid = $db->real_escape_string($input["template_id"]??"");
        $th = floatval($input["threshold"]??5);
        $db->query("INSERT INTO grading_tasks (id, name, batch_id, template_id, status, total_subjective, graded_count, threshold, created_at) VALUES ('$id', '$n', '$bid', '$tid', 'pending', 0, 0, $th, NOW())");
        jsonExit(["message" => "阅卷任务创建成功", "task" => ["id" => $id, "name" => $n]]);
    }
    if (preg_match("#^/grading/assign/?$#", $uri) && $method === "POST") {
        $input = jsonInput();
        $tpid = $db->real_escape_string($input["task_id"]??"");
        $tchid = $db->real_escape_string($input["teacher_id"]??"");
        $qnums = $input["question_numbers"] ?? [];
        $inserted = 0;
        foreach ($qnums as $qn) {
            $aid = uuid();
            $qn2 = intval($qn);
            $db->query("INSERT INTO grading_assignments (id, task_id, teacher_id, question_number, question_type, total_count, graded_count, status, created_at) VALUES ('$aid', '$tpid', '$tchid', $qn2, 'subjective', 0, 0, 'pending', NOW())");
            $inserted++;
        }
        jsonExit(["message" => "分配成功", "count" => $inserted]);
    }

    // ─── AUTH PASSWORD ───────────────────────
    if (preg_match("#^/auth/password$#", $uri) && $method === "PUT") {
        $u = authUser($db); $input = jsonInput();
        if (!password_verify($input["old_password"]??"", $u["password_hash"])) jsonExit(["detail"=>"原密码错误"],400);
        $id=$db->real_escape_string($u["id"]); $hash=password_hash($input["new_password"]??"",PASSWORD_BCRYPT);
        $db->query("UPDATE users SET password_hash='$hash' WHERE id='$id'"); jsonExit(["message"=>"密码修改成功"]);
    }

    // ─── USERS ─────────────────────────────────
    if (preg_match("#^/users/?$#",$uri) && $method==="GET") {
        $u=authUser($db); $rf=$_GET["role"]??""; $sql="SELECT * FROM users";
        if($rf) $sql.=" WHERE role='".$db->real_escape_string($rf)."'";
        $r=$db->query($sql); $list=[]; while($row=$r->fetch_assoc()) $list[]=userDict($row); jsonExit($list);
    }
    if (preg_match("#^/users/?$#",$uri) && $method==="POST") {
        authUser($db); $input=jsonInput(); $u=$db->real_escape_string($input["username"]??"");
        if($db->query("SELECT id FROM users WHERE username='$u'")->num_rows) jsonExit(["detail"=>"用户名已存在"],400);
        $id=uuid(); $hash=password_hash($input["password"]??"123456",PASSWORD_BCRYPT);
        $role=$db->real_escape_string($input["role"]??"student"); $rn=$db->real_escape_string($input["real_name"]??"");
        $em=$db->real_escape_string($input["email"]??""); $ph=$db->real_escape_string($input["phone"]??"");
        $db->query("INSERT INTO users VALUES('$id','$u','$hash','$rn','$role','$em','$ph',1,NOW(),NULL,NULL)");
        jsonExit(["message"=>"创建成功"]);
    }
    if (preg_match("#^/users/teachers$#",$uri) && $method==="GET") {
        authUser($db); $r=$db->query("SELECT * FROM users WHERE role='teacher' AND is_active=1");
        $list=[]; while($row=$r->fetch_assoc()) $list[]=userDict($row); jsonExit($list);
    }
    if (preg_match("#^/users/([^/]+)/toggle-active$#",$uri,$m) && $method==="PUT") {
        authUser($db); $uid=$db->real_escape_string($m[1]);
        $r=$db->query("SELECT is_active FROM users WHERE id='$uid'"); $u=$r->fetch_assoc();
        if(!$u) jsonExit(["detail"=>"用户不存在"],404); $nv=$u["is_active"]?0:1;
        $db->query("UPDATE users SET is_active=$nv WHERE id='$uid'"); jsonExit(["message"=>"已更新","is_active"=>(bool)$nv]);
    }
    if (preg_match("#^/users/([^/]+)$#",$uri,$m) && $method==="DELETE") {
        authUser($db); $uid=$db->real_escape_string($m[1]);
        $db->query("DELETE FROM users WHERE id='$uid' AND role!='super_admin'"); jsonExit(["message"=>"删除成功"]);
    }

    // ─── SCAN BATCHES ─────────────────────────
    if (preg_match("#^/scan/batch/?$#",$uri) && $method==="GET") {
        authUser($db); $r=$db->query("SELECT * FROM scan_batches ORDER BY created_at DESC"); $list=[];
        while($row=$r->fetch_assoc()){$bid=$row["id"];
            $p=$db->query("SELECT COUNT(*)c FROM scanned_sheets WHERE batch_id='$bid' AND status='completed'")->fetch_assoc()["c"];
            $f=$db->query("SELECT COUNT(*)c FROM scanned_sheets WHERE batch_id='$bid' AND status='failed'")->fetch_assoc()["c"];
            $list[]=["id"=>$row["id"],"name"=>$row["name"],"template_id"=>$row["template_id"],"exam_name"=>$row["exam_name"],"total"=>intval($row["total_sheets"]),"processed"=>intval($p),"failed"=>intval($f),"status"=>$row["status"],"created_at"=>$row["created_at"]];
        } jsonExit($list);
    }
    if (preg_match("#^/scan/batch/?$#",$uri) && $method==="POST") {
        authUser($db); $input=jsonInput(); $id=uuid();
        $n=$db->real_escape_string($input["name"]??""); $tid=$db->real_escape_string($input["template_id"]??""); $exam=$db->real_escape_string($input["exam_name"]??"");
        $db->query("INSERT INTO scan_batches VALUES('$id','$n','$tid','$exam',0,0,'pending','',NOW(),NOW())");
        jsonExit(["message"=>"创建成功","batch"=>["id"=>$id,"name"=>$n]]);
    }
    if (preg_match("#^/scan/batch/([^/]+)$#",$uri,$m) && $method==="GET") {
        authUser($db); $bid=$db->real_escape_string($m[1]);
        $r=$db->query("SELECT * FROM scan_batches WHERE id='$bid'"); $b=$r->fetch_assoc();
        if(!$b) jsonExit(["detail"=>"批次不存在"],404);
        $s=$db->query("SELECT id,filename,student_id,student_name,status,error_message FROM scanned_sheets WHERE batch_id='$bid'");
        $sheets=[]; while($sh=$s->fetch_assoc()) $sheets[]=$sh;
        jsonExit(["batch"=>["id"=>$b["id"],"name"=>$b["name"],"template_id"=>$b["template_id"],"exam_name"=>$b["exam_name"],"total"=>intval($b["total_sheets"]),"processed"=>intval($b["processed_sheets"]),"status"=>$b["status"],"created_at"=>$b["created_at"]],"sheets"=>$sheets]);
    }

    // ─── SCORES ───────────────────────────────
    if (preg_match("#^/scores/calculate/([^/]+)$#",$uri,$m) && $method==="POST") {
        authUser($db);$bid=$db->real_escape_string($m[1]);$r=[];
        $sh=$db->query("SELECT * FROM scanned_sheets WHERE batch_id='$bid' AND status='completed'");
        while($s=$sh->fetch_assoc()){
            $sid=$s["id"];$obj=floatval($db->query("SELECT COALESCE(SUM(score),0)o FROM recognition_results WHERE sheet_id='$sid'")->fetch_assoc()["o"]);
            $subj=floatval($db->query("SELECT COALESCE(SUM(score),0)s FROM subjective_images WHERE sheet_id='$sid' AND graded=1")->fetch_assoc()["s"]);
            $t=$obj+$subj; $ex=$db->query("SELECT id FROM exam_scores WHERE sheet_id='$sid'");
            if($ex->num_rows) $db->query("UPDATE exam_scores SET objective_score=$obj,subjective_score=$subj,total_score=$t WHERE sheet_id='$sid'");
            else{$id=uuid();$sn=$db->real_escape_string($s["student_name"]??"");$db->query("INSERT INTO exam_scores VALUES('$id','$bid','$sid','{$s["student_id"]}','$sn',$obj,$subj,$t,0,'',NOW(),NOW())");}
            $r[]=["sheet_id"=>$sid,"total"=>$t];
        } $rr=$db->query("SELECT id FROM exam_scores WHERE batch_id='$bid' ORDER BY total_score DESC");$rk=1;$cn=$rr->num_rows;
        while($x=$rr->fetch_assoc()){$db->query("UPDATE exam_scores SET `rank`='$rk/$cn' WHERE id='{$x["id"]}'");$rk++;}
        jsonExit(["message"=>"计算完成","results"=>$r]);
    }
    if (preg_match("#^/scores/batch/([^/]+)$#",$uri,$m) && $method==="GET") {
        authUser($db);$bid=$db->real_escape_string($m[1]);
        $r=$db->query("SELECT * FROM exam_scores WHERE batch_id='$bid' ORDER BY total_score DESC");$list=[];
        while($row=$r->fetch_assoc()) $list[]=["id"=>$row["id"],"student_id"=>$row["student_id"],"student_name"=>$row["student_name"],"objective_score"=>floatval($row["objective_score"]),"subjective_score"=>floatval($row["subjective_score"]),"total_score"=>floatval($row["total_score"]),"full_score"=>floatval($row["full_score"]),"rank"=>$row["rank"]];
        jsonExit($list);
    }
    if (preg_match("#^/scores/statistics/([^/]+)$#",$uri,$m) && $method==="GET") {
        authUser($db);$bid=$db->real_escape_string($m[1]);
        $r=$db->query("SELECT * FROM exam_scores WHERE batch_id='$bid'");$all=[];while($row=$r->fetch_assoc()) $all[]=$row;
        if(!count($all)) jsonExit(["message"=>"暂无数据"]);
        $ts=array_map(fn($s)=>$s["total_score"],$all);$avg=count($ts)?round(array_sum($ts)/count($ts),2):0;
        $mx=max($ts)?:0;$mn=min($ts)?:0;$full=floatval($all[0]["full_score"]??0);
        $pass=$full?count(array_filter($ts,fn($s)=>$s>=$full*0.6)):0;
        jsonExit(["total_students"=>count($ts),"average"=>$avg,"max_score"=>$mx,"min_score"=>$mn,"pass_count"=>$pass,"pass_rate"=>count($ts)?round($pass/count($ts)*100,2):0,"full_score"=>$full]);
    }
    if (preg_match("#^/scores/export/([^/]+)$#",$uri,$m) && $method==="GET") {
        authUser($db);$bid=$db->real_escape_string($m[1]);
        $r=$db->query("SELECT * FROM exam_scores WHERE batch_id='$bid' ORDER BY total_score DESC");
        $ln=["排名,考号,姓名,客观题得分,主观题得分,总分,满分"];
        while($row=$r->fetch_assoc()) $ln[]=implode(",",[$row["rank"]??"",$row["student_id"]??"",$row["student_name"]??"",$row["objective_score"],$row["subjective_score"],$row["total_score"],$row["full_score"]]);
        jsonExit(["csv"=>implode("\n",$ln),"filename"=>"scores_$bid.csv"]);
    }

    // ─── TEMPLATES upload/update/delete/export ─
    if (preg_match("#^/templates/upload-image$#",$uri) && $method==="POST") {
        authUser($db); if(!isset($_FILES["file"])) jsonExit(["detail"=>"未上传文件"],400);
        $ext=strtolower(pathinfo($_FILES["file"]["name"],PATHINFO_EXTENSION))?:"png"; $fn=uuid().".$ext";
        $dir="$UPLOAD_DIR/templates"; @mkdir($dir,0777,true);
        move_uploaded_file($_FILES["file"]["tmp_name"],"$dir/$fn");
        jsonExit(["filename"=>$fn,"url"=>"/uploads/templates/$fn"]);
    }
    if (preg_match("#^/templates/([^/]+)$#",$uri,$m) && $method==="PUT") {
        authUser($db); $tid=$db->real_escape_string($m[1]); $input=jsonInput(); $sets=[];
        foreach(["name","description","subject","grade","exam_name","info_method","status"] as $k)
            if(isset($input[$k])) $sets[]="$k='".$db->real_escape_string($input[$k])."'";
        if(isset($input["total_score"])) $sets[]="total_score=".floatval($input["total_score"]);
        if(count($sets)) $db->query("UPDATE templates SET ".implode(",",$sets)." WHERE id='$tid'");
        jsonExit(["message"=>"更新成功"]);
    }
    if (preg_match("#^/templates/([^/]+)$#",$uri,$m) && $method==="DELETE") {
        authUser($db); $tid=$db->real_escape_string($m[1]);
        $db->query("DELETE FROM template_markers WHERE template_id='$tid'");
        $db->query("DELETE FROM template_zones WHERE template_id='$tid'");
        $db->query("DELETE FROM objective_questions WHERE template_id='$tid'");
        $db->query("DELETE FROM correct_answers WHERE template_id='$tid'");
        $db->query("DELETE FROM templates WHERE id='$tid'"); jsonExit(["message"=>"删除成功"]);
    }
    if (preg_match("#^/templates/([^/]+)/export$#",$uri,$m) && $method==="GET") {
        authUser($db); $tid=$db->real_escape_string($m[1]);
        $r=$db->query("SELECT * FROM templates WHERE id='$tid'"); $t=$r->fetch_assoc();
        if(!$t) jsonExit(["detail"=>"模板不存在"],404);
        jsonExit($t);
    }

    // ─── SCAN UPLOAD ───────────────────────────
    if (preg_match("#^/scan/upload$#",$uri) && $method==="POST") {
        authUser($db); $batchId=$_POST["batch_id"]??""; if(!$batchId||!isset($_FILES["files"])) jsonExit(["detail"=>"缺少参数"],400);
        $bid=$db->real_escape_string($batchId);
        if(!$db->query("SELECT id FROM scan_batches WHERE id='$bid'")->num_rows) jsonExit(["detail"=>"批次不存在"],404);
        $bd="$UPLOAD_DIR/scans/$bid"; @mkdir($bd,0777,true); $c=0;
        if(is_array($_FILES["files"]["name"])){for($i=0;$i<count($_FILES["files"]["name"]);$i++){
            $fn=uuid()."_".basename($_FILES["files"]["name"][$i]); move_uploaded_file($_FILES["files"]["tmp_name"][$i],"$bd/$fn");
            $db->query("INSERT INTO scanned_sheets(id,batch_id,filename,file_path,status,created_at) VALUES('".uuid()."','$bid','$fn','$fn','pending',NOW())");$c++;
        }}else{$fn=uuid()."_".basename($_FILES["files"]["name"]); move_uploaded_file($_FILES["files"]["tmp_name"],"$bd/$fn");
            $db->query("INSERT INTO scanned_sheets VALUES('".uuid()."','$bid','$fn','$fn','',NULL,'pending','',1,'front',NULL,NOW())");$c++;
        } $db->query("UPDATE scan_batches SET total_sheets=total_sheets+$c WHERE id='$bid'");
        jsonExit(["message"=>"上传成功 共{$c}张","count"=>$c]);
    }

    // ─── SCAN RECOGNIZE → Python ──────────────
    if (preg_match("#^/scan/recognize/([^/]+)$#",$uri,$m) && $method==="POST") {
        authUser($db); $bid=$db->real_escape_string($m[1]);
        header("Location: https://onlinemark-backend.onrender.com/api/scan/recognize/$bid",true,307); exit;
    }

    // ─── GRADING pending/grade ─────────────────
    if (preg_match("#^/grading/pending$#",$uri) && $method==="GET") {
        $u=authUser($db);$uid=$db->real_escape_string($u["id"]);
        $r=$db->query("SELECT a.id aid,a.task_id,a.question_number,a.total_count,a.graded_count,t.name tn FROM grading_assignments a JOIN grading_tasks t ON a.task_id=t.id WHERE a.teacher_id='$uid' AND a.status!='completed'");$list=[];
        while($row=$r->fetch_assoc()){$qn=intval($row["question_number"]);
            $s=$db->query("SELECT id,file_path,sheet_id,COALESCE(max_score,0)ms FROM subjective_images WHERE question_number=$qn AND graded=0 LIMIT 10");$imgs=[];
            while($im=$s->fetch_assoc()) $imgs[]=["id"=>$im["id"],"file_path"=>$im["file_path"],"sheet_id"=>$im["sheet_id"],"max_score"=>floatval($im["ms"])];
            $list[]=["assignment_id"=>$row["aid"],"task_name"=>$row["tn"],"question_number"=>$qn,"total_count"=>intval($row["total_count"]),"graded_count"=>intval($row["graded_count"]),"pending_images"=>$imgs];
        } jsonExit($list);
    }
    if (preg_match("#^/grading/grade$#",$uri) && $method==="POST") {
        $u=authUser($db);$input=jsonInput();$uid=$db->real_escape_string($u["id"]);
        $aid=$db->real_escape_string($input["assignment_id"]??"");
        if(!$db->query("SELECT id FROM grading_assignments WHERE id='$aid' AND teacher_id='$uid'")->num_rows) jsonExit(["detail"=>"无权限"],403);
        $qn=intval($input["question_number"]??0);$sc=floatval($input["score"]??0);
        $sid=$db->real_escape_string($input["sheet_id"]??"");$sii=$db->real_escape_string($input["subjective_image_id"]??"");
        $gid=uuid();$db->query("INSERT INTO grades VALUES('$gid','$aid','$sid','$sii',$qn,$sc,'$uid',1,NULL,NOW())");
        if($sii) $db->query("UPDATE subjective_images SET score=$sc,graded=1 WHERE id='$sii'");
        $db->query("UPDATE grading_assignments SET graded_count=graded_count+1 WHERE id='$aid'");
        $a=$db->query("SELECT graded_count,total_count FROM grading_assignments WHERE id='$aid'")->fetch_assoc();
        if(intval($a["graded_count"])>=intval($a["total_count"])) $db->query("UPDATE grading_assignments SET status='completed' WHERE id='$aid'");
        jsonExit(["message"=>"评分提交成功"]);
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
