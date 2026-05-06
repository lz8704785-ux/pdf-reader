import fitz
import os
import glob
import json

PDFS_DIR = "pdfs"
IMAGES_DIR = "docs/images"
OUTPUT_DIR = "docs"

os.makedirs(IMAGES_DIR, exist_ok=True)

pdf_files = sorted(glob.glob(os.path.join(PDFS_DIR, "*.pdf")))
if not pdf_files:
    print("pdfs/ 文件夹中没有找到PDF文件")
    # 生成空的index.html
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PDF阅读器</title></head><body><p>请将PDF文件放入 pdfs/ 文件夹后推送</p></body></html>""")
    exit(0)

catalog = []

for pdf_path in pdf_files:
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    safe_name = pdf_name.replace(" ", "_").replace("(", "").replace(")", "")
    page_images = []

    print(f"正在处理: {pdf_name}")
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img_filename = f"{safe_name}_p{page_num + 1}.jpg"
        img_path = os.path.join(IMAGES_DIR, img_filename)
        pix.save(img_filename, output="jpg", jpg_quality=85)

        # PyMuPDF save to file path
        img_bytes = pix.tobytes(output="jpg", jpg_quality=85)
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        page_images.append(f"images/{img_filename}")

        print(f"  第 {page_num + 1}/{len(doc)} 页")

    doc.close()
    catalog.append({
        "name": pdf_name,
        "pages": page_images
    })

# 生成index.html
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PDF阅读器</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f5f5f5; color: #333; }
.header { background: #fff; padding: 16px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #e0e0e0; }
.header h1 { font-size: 18px; }
.tabs { display: flex; gap: 8px; margin-top: 10px; overflow-x: auto; padding-bottom: 4px; }
.tab { padding: 8px 16px; background: #e8e8e8; border-radius: 20px; cursor: pointer; white-space: nowrap; font-size: 14px; border: none; }
.tab.active { background: #1a73e8; color: #fff; }
.viewer { max-width: 800px; margin: 0 auto; padding: 12px; }
.viewer img { width: 100%; display: block; margin-bottom: 4px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.nav { position: fixed; bottom: 20px; right: 20px; display: flex; gap: 8px; }
.nav button { width: 44px; height: 44px; border-radius: 50%; border: none; background: #1a73e8; color: #fff; font-size: 20px; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.3); }
.empty { text-align: center; padding: 40px; color: #999; }
.page-num { text-align: center; padding: 8px; color: #999; font-size: 13px; }
</style>
</head>
<body>
<div class="header">
<h1>PDF阅读器</h1>
<div class="tabs" id="tabs"></div>
</div>
<div class="viewer" id="viewer"></div>
<div class="nav">
<button onclick="scrollUp()">&#8593;</button>
<button onclick="scrollDown()">&#8595;</button>
</div>
<script>
const data = """ + json.dumps(catalog, ensure_ascii=False) + """;
let current = 0;

function renderTabs() {
  const tabs = document.getElementById('tabs');
  tabs.innerHTML = data.map((item, i) =>
    '<button class="tab' + (i === current ? ' active' : '') + '" onclick="switchPdf(' + i + ')">' + item.name + '</button>'
  ).join('');
}

function renderViewer() {
  const viewer = document.getElementById('viewer');
  const pages = data[current].pages;
  viewer.innerHTML = pages.map((src, i) =>
    '<p class="page-num">' + (i+1) + ' / ' + pages.length + '</p><img src="' + src + '" loading="lazy">'
  ).join('');
  window.scrollTo(0, 0);
}

function switchPdf(i) {
  current = i;
  renderTabs();
  renderViewer();
}

function scrollUp() { window.scrollBy(0, -window.innerHeight * 0.8); }
function scrollDown() { window.scrollBy(0, window.innerHeight * 0.8); }

if (data.length > 0) { renderTabs(); renderViewer(); }
else { document.getElementById('viewer').innerHTML = '<p class="empty">没有PDF文件</p>'; }
</script>
</body>
</html>"""

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n处理完成! 共 {len(catalog)} 个PDF, 生成 {sum(len(c['pages']) for c in catalog)} 张图片")
