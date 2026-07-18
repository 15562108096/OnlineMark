import base64, os
# Read current file
p = r'D:\Desktop\Gaston Studio\services\OnlineMark\infinityfree\api\index.php'
with open(p, 'r', encoding='utf-8') as f:
    old = f.read()

# These are the sections that need to be added before '// ─── Health ───'
insert = r'''
    // ─── AUTH PASSWORD ───────────────────────
    if (preg_match("#^/auth/password$#", ) &&  === "PUT") {
        \ = authUser(\); \ = jsonInput();
        if (!password_verify(\["old_password"]??"", \["password_hash"])) jsonExit(["detail"=>"原密码错误"],400);
        \=\->real_escape_string(\["id"]); \=password_hash(\["new_password"]??"",PASSWORD_BCRYPT);
        \->query("UPDATE users SET password_hash='\' WHERE id='\'"); jsonExit(["message"=>"密码修改成功"]);
    }

    // ─── USERS ──────────────────────────────────
    if (preg_match("#^/users/?\$#",\) && \==="GET") {
        \=authUser(\);
        \=\["role"]??""; \="SELECT * FROM users";
        if(\) \.=" WHERE role='".\->real_escape_string(\)."'";
        \=\->query(\); \=[]; while(\=\->fetch_assoc()) \[]=userDict(\); jsonExit(\);
    }
    if (preg_match("#^/users/?\$#",\) && \==="POST") {
        authUser(\); \=jsonInput();
        \=\->real_escape_string(\["username"]??"");
        if(\->query("SELECT id FROM users WHERE username='\'")->num_rows) jsonExit(["detail"=>"用户名已存在"],400);
        \=uuid(); \=password_hash(\["password"]??"123456",PASSWORD_BCRYPT);
        \=\->real_escape_string(\["role"]??"student");
        \=\->real_escape_string(\["real_name"]??"");
        \=\->real_escape_string(\["email"]??"");
        \=\->real_escape_string(\["phone"]??"");
        \->query("INSERT INTO users VALUES('\','\','\','\','\','\','\',1,NOW(),NULL,NULL)");
        jsonExit(["message"=>"创建成功"]);
    }
    if (preg_match("#^/users/teachers\$#",\) && \==="GET") {
        authUser(\); \=\->query("SELECT * FROM users WHERE role='teacher' AND is_active=1");
        \=[]; while(\=\->fetch_assoc()) \[]=userDict(\); jsonExit(\);
    }
    if (preg_match("#^/users/([^/]+)/toggle-active\$#",\,\) && \==="PUT") {
        authUser(\); \=\->real_escape_string(\[1]);
        \=\->query("SELECT is_active FROM users WHERE id='\'"); \=\->fetch_assoc();
        if(!\) jsonExit(["detail"=>"用户不存在"],404); \=\["is_active"]?0:1;
        \->query("UPDATE users SET is_active=\ WHERE id='\'"); jsonExit(["message"=>"已更新","is_active"=>(bool)\]);
    }
    if (preg_match("#^/users/([^/]+)\$#",\,\) && \==="DELETE") {
        authUser(\); \=\->real_escape_string(\[1]);
        \->query("DELETE FROM users WHERE id='\' AND role!='super_admin'"); jsonExit(["message"=>"删除成功"]);
    }

    // ─── TEMPLATES: update/delete/export/upload ──
    if (preg_match("#^/templates/upload-image\$#",\) && \==="POST") {
        authUser(\); if(!isset(\["file"])) jsonExit(["detail"=>"未上传文件"],400);
        \=strtolower(pathinfo(\["file"]["name"],PATHINFO_EXTENSION))?:"png"; \=uuid().".\";
        \="\/templates"; @mkdir(\,0777,true);
        move_uploaded_file(\["file"]["tmp_name"],"\/\");
        jsonExit(["filename"=>\,"url"=>"/uploads/templates/\"]);
    }
    if (preg_match("#^/templates/([^/]+)\$#",\,\) && \==="PUT") {
        authUser(\); \=\->real_escape_string(\[1]); \=jsonInput(); \=[];
        foreach(["name","description","subject","grade","exam_name","info_method","status"] as \)
            if(isset(\[\])) \[]="\='".\->real_escape_string(\[\])."'";
        if(isset(\["total_score"])) \[]="total_score=".floatval(\["total_score"]);
        if(count(\)) \->query("UPDATE templates SET ".implode(",",\)." WHERE id='\'");
        jsonExit(["message"=>"更新成功"]);
    }
    if (preg_match("#^/templates/([^/]+)\$#",\,\) && \==="DELETE") {
        authUser(\); \=\->real_escape_string(\[1]);
        \->query("DELETE FROM template_markers WHERE template_id='\'");
        \->query("DELETE FROM template_zones WHERE template_id='\'");
        \->query("DELETE FROM objective_questions WHERE template_id='\'");
        \->query("DELETE FROM correct_answers WHERE template_id='\'");
        \->query("DELETE FROM templates WHERE id='\'"); jsonExit(["message"=>"删除成功"]);
    }
    if (preg_match("#^/templates/([^/]+)/export\$#",\,\) && \==="GET") {
        authUser(\); \=\->real_escape_string(\[1]);
        \=\->query("SELECT * FROM templates WHERE id='\'"); \=\->fetch_assoc();
        if(!\) jsonExit(["detail"=>"模板不存在"],404);
        jsonExit(["id"=>\["id"],"name"=>\["name"]]);
    }

    // ─── SCAN BATCHES ──────────────────────────
    if (preg_match("#^/scan/batch/?\$#",\) && \==="GET") {
        authUser(\); \=\->query("SELECT * FROM scan_batches ORDER BY created_at DESC"); \=[];
        while(\=\->fetch_assoc()){\=\["id"];
            \=\->query("SELECT COUNT(*)c FROM scanned_sheets WHERE batch_id='\' AND status='completed'")->fetch_assoc()["c"];
            \=\->query("SELECT COUNT(*)c FROM scanned_sheets WHERE batch_id='\' AND status='failed'")->fetch_assoc()["c"];
            \[]=["id"=>\["id"],"name"=>\["name"],"template_id"=>\["template_id"],"exam_name"=>\["exam_name"],"total"=>intval(\["total_sheets"]),"processed"=>intval(\),"failed"=>intval(\),"status"=>\["status"],"created_at"=>\["created_at"]];
        } jsonExit(\);
    }
    if (preg_match("#^/scan/batch/?\$#",\) && \==="POST") {
        authUser(\); \=jsonInput(); \=uuid();
        \=\->real_escape_string(\["name"]??"");
        \=\->real_escape_string(\["template_id"]??"");
        \=\->real_escape_string(\["exam_name"]??"");
        \->query("INSERT INTO scan_batches VALUES('\','\','\','\',0,0,'pending','',NOW(),NOW())");
        jsonExit(["message"=>"创建成功","batch"=>["id"=>\,"name"=>\]]);
    }
    if (preg_match("#^/scan/batch/([^/]+)\$#",\,\) && \==="GET") {
        authUser(\); \=\->real_escape_string(\[1]);
        \=\->query("SELECT * FROM scan_batches WHERE id='\'"); \=\->fetch_assoc();
        if(!\) jsonExit(["detail"=>"批次不存在"],404);
        \=\->query("SELECT id,filename,student_id,student_name,status,error_message FROM scanned_sheets WHERE batch_id='\'");
        \=[]; while(\=\->fetch_assoc()) \[]=\;
        jsonExit(["batch"=>["id"=>\["id"],"name"=>\["name"],"template_id"=>\["template_id"],"exam_name"=>\["exam_name"],"total"=>intval(\["total_sheets"]),"processed"=>intval(\["processed_sheets"]),"status"=>\["status"],"created_at"=>\["created_at"]],"sheets"=>\]);
    }

    // ─── SCAN UPLOAD ────────────────────────────
    if (preg_match("#^/scan/upload\$#",\) && \==="POST") {
        authUser(\); \=\["batch_id"]??""; if(!\||!isset(\["files"])) jsonExit(["detail"=>"缺少参数"],400);
        \=\->real_escape_string(\);
        if(!\->query("SELECT id FROM scan_batches WHERE id='\'")->num_rows) jsonExit(["detail"=>"批次不存在"],404);
        \="\/scans/\"; @mkdir(\,0777,true); \=0;
        if(is_array(\["files"]["name"])){for(\=0;\<count(\["files"]["name"]);\++){
            \=uuid()."_".basename(\["files"]["name"][\]); move_uploaded_file(\["files"]["tmp_name"][\],"\/\");
            \->query("INSERT INTO scanned_sheets(id,batch_id,filename,file_path,status,created_at) VALUES('".uuid()."','\','\','\','pending',NOW())");\++;
        }} else { \=uuid()."_".basename(\["files"]["name"]); move_uploaded_file(\["files"]["tmp_name"],"\/\");
            \->query("INSERT INTO scanned_sheets VALUES('".uuid()."','\','\','\','',NULL,'pending','',1,'front',NULL,NOW())");\++;
        } \->query("UPDATE scan_batches SET total_sheets=total_sheets+\ WHERE id='\'");
        jsonExit(["message"=>"上传成功，共{\}张","count"=>\]);
    }

    // ─── SCAN RECOGNIZE → PYTHON ──────────────
    if (preg_match("#^/scan/recognize/([^/]+)\$#",\,\) && \==="POST") {
        authUser(\); \=\->real_escape_string(\[1]);
        header("Location: https://onlinemark-backend.onrender.com/api/scan/recognize/\",true,307); exit;
    }

    // ─── SCORES ────────────────────────────────
    if (preg_match("#^/scores/calculate/([^/]+)\$#",\,\) && \==="POST") {
        authUser(\);\=\->real_escape_string(\[1]);\=[];
        \=\->query("SELECT * FROM scanned_sheets WHERE batch_id='\' AND status='completed'");
        while(\=\->fetch_assoc()){
            \=\["id"];\=floatval(\->query("SELECT COALESCE(SUM(score),0)o FROM recognition_results WHERE sheet_id='\'")->fetch_assoc()["o"]);
            \=floatval(\->query("SELECT COALESCE(SUM(score),0)s FROM subjective_images WHERE sheet_id='\' AND graded=1")->fetch_assoc()["s"]);
            \=\+\; \=\->query("SELECT id FROM exam_scores WHERE sheet_id='\'");
            if(\->num_rows) \->query("UPDATE exam_scores SET objective_score=\,subjective_score=\,total_score=\ WHERE sheet_id='\'");
            else{\=uuid();\=\->real_escape_string(\["student_name"]??"");\->query("INSERT INTO exam_scores VALUES('\','\','\','{\["student_id"]}','\',\,\,\,0,'',NOW(),NOW())");}
            \[]=["sheet_id"=>\,"total"=>\];
        } // update ranks
        \=\->query("SELECT id FROM exam_scores WHERE batch_id='\' ORDER BY total_score DESC");\=1;\=\->num_rows;
        while(\=\->fetch_assoc()){\->query("UPDATE exam_scores SET ank='\/\' WHERE id='{\["id"]}'");\++;}
        jsonExit(["message"=>"计算完成","results"=>\]);
    }
    if (preg_match("#^/scores/batch/([^/]+)\$#",\,\) && \==="GET") {
        authUser(\);\=\->real_escape_string(\[1]);
        \=\->query("SELECT * FROM exam_scores WHERE batch_id='\' ORDER BY total_score DESC");\=[];
        while(\=\->fetch_assoc()) \[]=["id"=>\["id"],"student_id"=>\["student_id"],"student_name"=>\["student_name"],"objective_score"=>floatval(\["objective_score"]),"subjective_score"=>floatval(\["subjective_score"]),"total_score"=>floatval(\["total_score"]),"full_score"=>floatval(\["full_score"]),"rank"=>\["rank"]];
        jsonExit(\);
    }
    if (preg_match("#^/scores/statistics/([^/]+)\$#",\,\) && \==="GET") {
        authUser(\);\=\->real_escape_string(\[1]);
        \=\->query("SELECT * FROM exam_scores WHERE batch_id='\'");\=[];while(\=\->fetch_assoc()) \[]=\;
        if(!count(\)) jsonExit(["message"=>"暂无数据"]);
        \=array_map(fn(\)=>\["total_score"],\);\=count(\)?round(array_sum(\)/count(\),2):0;
        \=max(\)?:0;\=min(\)?:0;\=floatval(\[0]["full_score"]??0);
        \=\(array_filter(\,fn(\)=>\>=\*0.6)):0;
        jsonExit(["total_students"=>count(\),"average"=>\,"max_score"=>\,"min_score"=>\,"pass_count"=>\,"pass_rate"=>count(\)?round(\/count(\)*100,2):0,"full_score"=>\]);
    }
    if (preg_match("#^/scores/export/([^/]+)\$#",\,\) && \==="GET") {
        authUser(\);\=\->real_escape_string(\[1]);
        \=\->query("SELECT * FROM exam_scores WHERE batch_id='\' ORDER BY total_score DESC");
        \=["排名,考号,姓名,客观题得分,主观题得分,总分,满分"];
        while(\=\->fetch_assoc()) \[]=implode(",",[\["rank"]??"",\["student_id"]??"",\["student_name"]??"",\["objective_score"],\["subjective_score"],\["total_score"],\["full_score"]]);
        jsonExit(["csv"=>implode("\n",\),"filename"=>"scores_\.csv"]);
    }

    // ─── GRADING pending/submit ─────────────────
    if (preg_match("#^/grading/pending\$#",\) && \==="GET") {
        \=authUser(\);\=\->real_escape_string(\["id"]);
        \=\->query("SELECT a.id aid,a.task_id,a.question_number,a.total_count,a.graded_count,t.name tn FROM grading_assignments a JOIN grading_tasks t ON a.task_id=t.id WHERE a.teacher_id='\' AND a.status!='completed'");\=[];
        while(\=\->fetch_assoc()){\=intval(\["question_number"]);
            \=\->query("SELECT id,file_path,sheet_id,COALESCE(max_score,0)ms FROM subjective_images WHERE question_number=\ AND graded=0 LIMIT 10");\=[];
            while(\=\->fetch_assoc()) \[]=["id"=>\["id"],"file_path"=>\["file_path"],"sheet_id"=>\["sheet_id"],"max_score"=>floatval(\["ms"])];
            \[]=["assignment_id"=>\["aid"],"task_name"=>\["tn"],"question_number"=>\,"total_count"=>intval(\["total_count"]),"graded_count"=>intval(\["graded_count"]),"pending_images"=>\];
        } jsonExit(\);
    }
    if (preg_match("#^/grading/grade\$#",\) && \==="POST") {
        \=authUser(\);\=jsonInput();\=\->real_escape_string(\["id"]);
        \=\->real_escape_string(\["assignment_id"]??"");
        if(!\->query("SELECT id FROM grading_assignments WHERE id='\' AND teacher_id='\'")->num_rows) jsonExit(["detail"=>"无权限"],403);
        \=intval(\["question_number"]??0);\=floatval(\["score"]??0);
        \=\->real_escape_string(\["sheet_id"]??"");\=\->real_escape_string(\["subjective_image_id"]??"");
        \=uuid();\->query("INSERT INTO grades VALUES('\','\','\','\',\,\,'\',1,NULL,NOW())");
        if(\) \->query("UPDATE subjective_images SET score=\,graded=1 WHERE id='\'");
        \->query("UPDATE grading_assignments SET graded_count=graded_count+1 WHERE id='\'");
        \=\->query("SELECT graded_count,total_count FROM grading_assignments WHERE id='\'")->fetch_assoc();
        if(intval(\["graded_count"])>=intval(\["total_count"])) \->query("UPDATE grading_assignments SET status='completed' WHERE id='\'");
        jsonExit(["message"=>"评分提交成功"]);
    }
'''

# Insert before the Health section
new = old.replace('// ─── Health ────────────────────────────────────────', insert + '\n    // ─── Health ────────────────────────────────────────')

# Write back
with open(p, 'w', encoding='utf-8') as f:
    f.write(new)
print('PHP file updated successfully')
print(f'Size: {len(new)} bytes')
