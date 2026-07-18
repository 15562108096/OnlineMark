<?php
// InfinityFree PHP Diagnostics
header("Content-Type: text/plain; charset=utf-8");
echo "=== PHP Info ===\n";
echo "PHP Version: " . phpversion() . "\n";
echo "mysqli: " . (extension_loaded("mysqli") ? "✅ 已加载" : "❌ 未加载") . "\n";
echo "PDO: " . (extension_loaded("PDO") ? "✅" : "❌") . "\n";
echo "password_hash: " . (function_exists("password_hash") ? "✅" : "❌") . "\n";
echo "json_encode: " . (function_exists("json_encode") ? "✅" : "❌") . "\n\n";

echo "=== DB Test ===\n";
$host = "localhost";
$user = "if0_39743066";
$pass = "DouglasJP2026";
$name = "if0_39743066_onlinemark";

$conn = @new mysqli($host, $user, $pass, $name);
if ($conn->connect_error) {
    echo "❌ 连接失败: " . $conn->connect_error . "\n";
    echo "   Host: $host\n";
    echo "   User: $user\n";
    echo "   DB:   $name\n";
} else {
    echo "✅ 数据库连接成功\n";
    echo "   Host: $host\n";
    echo "   Server: " . $conn->server_info . "\n";
    $conn->close();
}
