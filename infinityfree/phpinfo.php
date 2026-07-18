<?php
header("Content-Type: text/plain; charset=utf-8");
echo "=== 数据库连接诊断 ===\n\n";

$user = "if0_39743066";
$pass = "DouglasJP2026";
$name = "if0_39743066_onlinemark";
$hosts = ["localhost", "127.0.0.1", "sql306.infinityfree.com"];

echo "DNS解析:\n";
foreach ($hosts as $h) {
    $ip = gethostbyname($h);
    echo "  $h → $ip\n";
}

echo "\n连接测试:\n";
foreach ($hosts as $h) {
    echo "  尝试 $h ... ";
    $start = microtime(true);
    $conn = @new mysqli($h, $user, $pass, $name, 3306);
    $elapsed = round((microtime(true) - $start) * 1000);
    if ($conn->connect_error) {
        echo "❌ ({$elapsed}ms) " . $conn->connect_error . "\n";
    } else {
        echo "✅ ({$elapsed}ms) 成功! 服务器: " . $conn->server_info . "\n";
        $conn->close();
        break;
    }
}

echo "\n=== PHP配置 ===\n";
echo "禁用函数: " . (ini_get("disable_functions") ?: "无") . "\n";
echo "内存限制: " . ini_get("memory_limit") . "\n";
echo "最大执行时间: " . ini_get("max_execution_time") . "s\n";
echo "扩展路径: " . ini_get("extension_dir") . "\n";
