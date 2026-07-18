import re
p = r"D:\Desktop\Gaston Studio\services\OnlineMark\infinityfree\api\index.php"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Add authHeader helper after getDB()
if "function authHeader" not in c:
    c = c.replace(
        "function getDB(): mysqli {",
        "function authHeader(): string {\n    return $_SERVER[\"HTTP_AUTHORIZATION\"] ?? $_SERVER[\"REDIRECT_HTTP_AUTHORIZATION\"] ?? \"\";\n}\n\nfunction getDB(): mysqli {",
        1
    )

# 2. Update authUser HTTP_AUTHORIZATION check
c = c.replace(
    "$auth = $_SERVER[\"HTTP_AUTHORIZATION\"] ?? \"\";",
    "$auth = authHeader();"
)

with open(p, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed")
