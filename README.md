# 操作系统原理选择题练习

这是一个本地运行的小练习程序，用来把 PDF 题库转换成网页可练习的选择题。

## 纯网页版本

如果不想安装 Python，也不想运行小程序，直接双击打开：

```text
D:\os-practice-app\刷题网页.html
```

打开后，把 PDF 里的选择题文本复制进去，点击“解析并开始刷题”即可。这个版本会把题库和答题记录保存在浏览器本地。

## 文件

- `刷题网页.html`：纯离线网页，双击就能用
- `extract_questions.py`：从 PDF 中提取选择题，生成 `questions.json`
- `index.html`：练习页面，打开即可使用
- `questions.sample.json`：示例题库格式

## 推荐使用方法

直接运行：

```powershell
cd D:\os-practice-app
python .\start_app.py
```

它会自动尝试生成 `questions.json`，然后打开练习页面。

## 手动使用方法

也可以先生成题库：

```powershell
cd D:\os-practice-app
python .\extract_questions.py
```

再启动网页：

```powershell
python -m http.server 8765
```

浏览器打开：

```text
http://127.0.0.1:8765/index.html
```

如果浏览器没有自动加载 `questions.json`，可以点击页面右上角的导入按钮，选择生成的 `questions.json`。

## 说明

脚本会默认读取：

```text
D:\11.个人文件\12.电子书\《操作系统原理》线上各类练习题集\《操作系统原理》线上各类练习题集\《操作系统原理-线上选择题库.pdf》
```

如果 PDF 里的排版和常见题库格式差异较大，脚本可能需要根据实际文本微调。脚本会优先尝试 `pymupdf`、`pypdf`、`pdfplumber` 这几种常见 PDF 读取库。
