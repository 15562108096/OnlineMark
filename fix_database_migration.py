import os
b = r"D:\Desktop\Gaston Studio\services\OnlineMark"

# 1. Update database.py
path = os.path.join(b, "backend", "app", "database.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

mig = '\nimport sqlalchemy as sa\nfrom sqlalchemy import text\n\ndef run_migrations(engine):\n'
mig += '    """Add new columns to existing tables"""\n'
mig += '    migs = [\n'
mig += '        ("templates", "total_pages", "ALTER TABLE templates ADD COLUMN total_pages INTEGER DEFAULT 1"),\n'
mig += '        ("templates", "pdf_path", "ALTER TABLE templates ADD COLUMN pdf_path VARCHAR(500)"),\n'
mig += '        ("template_markers", "page_number", "ALTER TABLE template_markers ADD COLUMN page_number INTEGER DEFAULT 0"),\n'
mig += '        ("template_zones", "page_number", "ALTER TABLE template_zones ADD COLUMN page_number INTEGER DEFAULT 0"),\n'
mig += '        ("objective_questions", "page_number", "ALTER TABLE objective_questions ADD COLUMN page_number INTEGER DEFAULT 0"),\n'
mig += '        ("scan_batches", "upload_order", "ALTER TABLE scan_batches ADD COLUMN upload_order VARCHAR(20) DEFAULT \'sequential\'"),\n'
mig += '        ("scanned_sheets", "page_number", "ALTER TABLE scanned_sheets ADD COLUMN page_number INTEGER DEFAULT 1"),\n'
mig += '        ("scanned_sheets", "side", "ALTER TABLE scanned_sheets ADD COLUMN side VARCHAR(20) DEFAULT \'front\'"),\n'
mig += '    ]\n'
mig += '    for table, column, sql in migs:\n'
mig += '        try:\n'
mig += '            with engine.connect() as conn:\n'
mig += '                conn.execute(text(sql))\n'
mig += '                conn.commit()\n'
mig += '        except Exception:\n'
mig += '            pass  # Column likely already exists\n'

old = 'def get_db():'
c = c.replace(old, mig + old)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("1. database.py migration code added")

# 2. Update main.py to call migration
path = os.path.join(b, "backend", "app", "main.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old = "from app.database import init_db, engine, Base"
new = "from app.database import init_db, engine, Base, run_migrations"
c = c.replace(old, new)

old = "Base.metadata.create_all(bind=engine)"
new = "Base.metadata.create_all(bind=engine)\nrun_migrations(engine)"
c = c.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("2. main.py updated to run migrations on startup")

# Verify syntax
import compileall
path_db = os.path.join(b, "backend", "app", "database.py")
path_main = os.path.join(b, "backend", "app", "main.py")
for p in [path_db, path_main]:
    with open(p, "r", encoding="utf-8") as f:
        try:
            compile(f.read(), p, "exec")
            print(f"  OK: {os.path.basename(p)}")
        except SyntaxError as e:
            print(f"  ERROR: {os.path.basename(p)}: {e}")
