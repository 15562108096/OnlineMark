<?php
/**
 * OnlineMark - Database Seed Script
 * Visit this URL in your browser ONCE after uploading to InfinityFree.
 * It creates the admin user in the database.
 */
$DB_HOST = getenv("DB_HOST") ?: "sql306.infinityfree.com";
$DB_USER = getenv("DB_USER") ?: "if0_39743066";
$DB_PASS = getenv("DB_PASSWORD") ?: "DouglasJP2026";
$DB_NAME = getenv("DB_NAME") ?: "if0_39743066_onlinemark";

header("Content-Type: text/plain; charset=utf-8");
echo "OnlineMark Database Seed\n";
echo "=======================\n\n";

$conn = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
if ($conn->connect_error) {
    die("❌ DB连接失败: " . $conn->connect_error . "\n");
}
$conn->set_charset("utf8mb4");
echo "✅ 数据库连接成功\n";

$username = "37108220071109031X";
$password = "Zyw20071109";
$realName = "超级管理员";

$u = $conn->real_escape_string($username);
$r = $conn->query("SELECT id FROM users WHERE username = '$u'");
if ($r && $r->num_rows > 0) {
    echo "✅ 管理员已存在，跳过创建\n";
} else {
    $id = sprintf("%04x%04x-%04x-%04x-%04x-%04x%04x%04x",
        mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff),
        mt_rand(0,0x0fff)|0x4000, mt_rand(0,0x3fff)|0x8000,
        mt_rand(0,0xffff), mt_rand(0,0xffff), mt_rand(0,0xffff));
    $hash = password_hash($password, PASSWORD_BCRYPT);
    $rn = $conn->real_escape_string($realName);
    $conn->query("INSERT INTO users (id, username, password_hash, real_name, role, is_active, created_at) VALUES ('$id', '$u', '$hash', '$rn', 'super_admin', 1, NOW())");
    echo "✅ 管理员创建成功!\n";
}

echo "\n👤 账号: $username\n";
echo "🔑 密码: $password\n";
echo "\n然后设置 Render 环境变量:\n";
echo "  PHP_API_URL=https://你的infinityfree域名.com\n";
echo "  PHP_API_ENABLED=true\n";
