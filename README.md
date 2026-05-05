# PDF阅读器

把PDF文件推送到 `pdfs/` 文件夹，GitHub Actions 自动将每页转为高清图片，部署到 GitHub Pages 供手机/浏览器查看。

## 使用方法

```bash
# 1. 把PDF复制到pdfs文件夹
cp 你的文件.pdf pdfs/

# 2. 提交推送
git add pdfs/
git commit -m "添加PDF"
git push

# 3. 等待自动处理完成后访问 GitHub Pages 查看
```

## 目录结构

```
pdfs/                ← 放PDF文件
scripts/             ← 处理脚本
docs/                ← 自动生成的网页（GitHub Pages）
.github/workflows/   ← 自动化工作流
```
