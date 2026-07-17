import os,json

base=r"D:\\Desktop\\Gaston Studio\\services\\OnlineMark"

# Dockerfile
with open(os.path.join(base,"Dockerfile"),"w") as f:
    f.write("FROM python:3.11-slim\nWORKDIR /app\nCOPY backend/requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY backend/ .\nENV DB_TYPE=sqlite\nEXPOSE 8000\nCMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]\n")

# .dockerignore
with open(os.path.join(base,".dockerignore"),"w") as f:
    f.write("node_modules\nfrontend/node_modules\nfrontend/dist\n__pycache__\n*.pyc\n.env\n*.db\nuploads\n.git\n")

# vercel.json
with open(os.path.join(base,"frontend","vercel.json"),"w") as f:
    json.dump({"rewrites":[{"source":"/api/(.*)","destination":"https://online-mark-backend.onrender.com/api/$1"},{"source":"/uploads/(.*)","destination":"https://online-mark-backend.onrender.com/uploads/$1"},{"source":"/(.*)","destination":"/index.html"}]},f,indent=2)

print("Files created!")