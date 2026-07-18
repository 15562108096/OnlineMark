<?php
try {
    $DB_HOST = "sql306.infinityfree.com";
    $DB_USER = "if0_39743066";
    $DB_PASS = "DouglasJP2026";
    $DB_NAME = "if0_39743066_onlinemark";
    header("Content-Type: text/plain; charset=utf-8");
    echo "OnlineMark Database Seed\n=======================\n\n";
    if (!extension_loaded("mysqli")) die(" PHP缺少mysqli扩展\n");
    $conn = @new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME, 3306);
    if ($conn->connect_error) die(" DB连接失败: " . $conn->connect_error . "\n");
    $conn->set_charset("utf8mb4");
    echo " 数据库连接成功\n";

    // Tables
    $tables = [
        "CREATE TABLE IF NOT EXISTS users (id VARCHAR(36) PRIMARY KEY, username VARCHAR(100) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL, real_name VARCHAR(100), role VARCHAR(20) NOT NULL DEFAULT 'student', email VARCHAR(255), phone VARCHAR(20), is_active TINYINT(1) DEFAULT 1, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, created_by VARCHAR(36)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS templates (id VARCHAR(36) PRIMARY KEY, name VARCHAR(200) NOT NULL, description TEXT, subject VARCHAR(100), grade VARCHAR(50), exam_name VARCHAR(200), image_path VARCHAR(500), pdf_path VARCHAR(500), total_pages INT DEFAULT 1, image_width INT, image_height INT, total_score FLOAT DEFAULT 0, objective_score FLOAT DEFAULT 0, subjective_score FLOAT DEFAULT 0, info_method VARCHAR(20) DEFAULT 'omr', status VARCHAR(20) DEFAULT 'draft', created_by VARCHAR(36), created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS template_markers (id VARCHAR(36) PRIMARY KEY, template_id VARCHAR(36) NOT NULL, point_index INT NOT NULL, x FLOAT NOT NULL, y FLOAT NOT NULL, label VARCHAR(50), page_number INT DEFAULT 0, width FLOAT DEFAULT 0, height FLOAT DEFAULT 0, shape VARCHAR(20) DEFAULT 'circle') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS template_zones (id VARCHAR(36) PRIMARY KEY, template_id VARCHAR(36) NOT NULL, zone_type VARCHAR(20) NOT NULL, label VARCHAR(200), x FLOAT NOT NULL, y FLOAT NOT NULL, width FLOAT NOT NULL, height FLOAT NOT NULL, sort_order INT DEFAULT 0, page_number INT DEFAULT 0, config JSON, answer_positions JSON) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS objective_questions (id VARCHAR(36) PRIMARY KEY, template_id VARCHAR(36) NOT NULL, zone_id VARCHAR(36), question_number INT NOT NULL, question_type VARCHAR(20) DEFAULT 'single', options_count INT DEFAULT 4, options JSON, option_layout VARCHAR(20) DEFAULT 'vertical', score FLOAT DEFAULT 1, x FLOAT, y FLOAT, width FLOAT, height FLOAT, correct_answer VARCHAR(50), answer_positions JSON, sort_order INT DEFAULT 0) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS correct_answers (id VARCHAR(36) PRIMARY KEY, template_id VARCHAR(36) NOT NULL, question_id VARCHAR(36), question_number INT NOT NULL, answer VARCHAR(50) NOT NULL, score FLOAT DEFAULT 1, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS scan_batches (id VARCHAR(36) PRIMARY KEY, name VARCHAR(200) NOT NULL, template_id VARCHAR(36) NOT NULL, exam_name VARCHAR(200), total_sheets INT DEFAULT 0, upload_order VARCHAR(20) DEFAULT 'sequential', processed_sheets INT DEFAULT 0, status VARCHAR(20) DEFAULT 'pending', created_by VARCHAR(36), created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS scanned_sheets (id VARCHAR(36) PRIMARY KEY, batch_id VARCHAR(36) NOT NULL, filename VARCHAR(500) NOT NULL, file_path VARCHAR(500) NOT NULL, student_id VARCHAR(100), student_name VARCHAR(100), status VARCHAR(20) DEFAULT 'pending', error_message TEXT, page_number INT DEFAULT 1, side VARCHAR(20) DEFAULT 'front', processed_at DATETIME, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS recognition_results (id VARCHAR(36) PRIMARY KEY, sheet_id VARCHAR(36) NOT NULL, question_id VARCHAR(36), question_number INT NOT NULL, question_type VARCHAR(20) NOT NULL, detected_answer VARCHAR(50), correct_answer VARCHAR(50), is_correct TINYINT(1), score FLOAT DEFAULT 0, max_score FLOAT DEFAULT 0, confidence FLOAT, details JSON, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS subjective_images (id VARCHAR(36) PRIMARY KEY, sheet_id VARCHAR(36) NOT NULL, question_number INT NOT NULL, file_path VARCHAR(500) NOT NULL, score FLOAT, max_score FLOAT, graded TINYINT(1) DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS grading_tasks (id VARCHAR(36) PRIMARY KEY, name VARCHAR(200) NOT NULL, batch_id VARCHAR(36) NOT NULL, template_id VARCHAR(36) NOT NULL, status VARCHAR(20) DEFAULT 'pending', total_subjective INT DEFAULT 0, graded_count INT DEFAULT 0, threshold FLOAT DEFAULT 5, created_by VARCHAR(36), created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS grading_assignments (id VARCHAR(36) PRIMARY KEY, task_id VARCHAR(36) NOT NULL, teacher_id VARCHAR(36) NOT NULL, question_number INT NOT NULL, question_type VARCHAR(20) DEFAULT 'subjective', total_count INT DEFAULT 0, graded_count INT DEFAULT 0, status VARCHAR(20) DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS grades (id VARCHAR(36) PRIMARY KEY, assignment_id VARCHAR(36) NOT NULL, sheet_id VARCHAR(36) NOT NULL, subjective_image_id VARCHAR(36), question_number INT NOT NULL, score FLOAT NOT NULL, teacher_id VARCHAR(36) NOT NULL, grading_round INT DEFAULT 1, comment TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        "CREATE TABLE IF NOT EXISTS exam_scores (id VARCHAR(36) PRIMARY KEY, batch_id VARCHAR(36) NOT NULL, sheet_id VARCHAR(36) NOT NULL, student_id VARCHAR(100), student_name VARCHAR(100), objective_score FLOAT DEFAULT 0, subjective_score FLOAT DEFAULT 0, total_score FLOAT DEFAULT 0, full_score FLOAT DEFAULT 0, `rank` VARCHAR(20), details TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    ];
    foreach ($tables as $sql) { $conn->query($sql); }
    echo " 数据表创建完成\n";
foreach ($tables as $i => $sql) {
    $r = $conn->query($sql);
    if (!$r) echo "  表 #$i 失败: " . $conn->error . "\n" . substr($sql, 0, 80) . "...\n";
}
echo " 数据表创建完成\n";

    // Admin user
    $username = "37108220071109031X"; $password = "Zyw20071109"; $realName = "超级管理员";
    $u = $conn->real_escape_string($username);
    $r = $conn->query("SELECT id FROM users WHERE username = '$u'");
    if ($r && $r->num_rows > 0) {
        echo " 管理员已存在\n";
    } else {
        $id = sprintf("%04x%04x-%04x-%04x-%04x-%04x%04x%04x", mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0x0fff)|0x4000, mt_rand(0,0x3fff)|0x8000, mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff));
        $hash = password_hash($password, PASSWORD_BCRYPT);
        $rn = $conn->real_escape_string($realName);
        $conn->query("INSERT INTO users (id, username, password_hash, real_name, role, is_active, created_at) VALUES ('$id', '$u', '$hash', '$rn', 'super_admin', 1, NOW())");
        echo " 管理员创建成功!\n";
    }
    echo "\n 账号: $username\n 密码: $password\n";
} catch (Throwable $e) {
    echo " 错误: " . $e->getMessage() . "\n";
}
