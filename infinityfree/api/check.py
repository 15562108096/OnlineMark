import re
with open(r'D:\Desktop\Gaston Studio\services\OnlineMark\infinityfree\api\index.php', 'r', encoding='utf-8') as f:
    c = f.read()
print("HTTP_AUTHORIZATION count:", c.count("HTTP_AUTHORIZATION"))
print("Has authHeader:", "authHeader" in c)
print("Has REDIRECT:", "REDIRECT" in c)
