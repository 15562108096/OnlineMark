import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "frontend", "src", "pages", "TemplateEditorPage.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove the previous wheel fix (onWheel on div)  
c = c.replace('        <div className="editor-canvas-wrap">',
    '        <div className="editor-canvas-wrap" onWheel={(e) => { const h = (ev: WheelEvent) => { ev.preventDefault(); const d = ev.deltaY > 0 ? 0.9 : 1.1; setScale((s) => Math.max(0.2, Math.min(3, s * d))); }; try { (e as any).preventDefault && (e as any).preventDefault(); } catch {} const d = (e as any).deltaY > 0 ? 0.9 : 1.1; setScale((s) => Math.max(0.2, Math.min(3, s * d))); }} onWheelCapture={(e) => { try { e.preventDefault(); } catch {} }}>')
# Actually this is getting complex. Let me just use a simple approach.
