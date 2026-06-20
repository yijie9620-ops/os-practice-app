import json
import re
import sys
from pathlib import Path


DEFAULT_PDF = Path(
    r"D:\11.个人文件\12.电子书\《操作系统原理》线上各类练习题集\《操作系统原理》线上各类练习题集\《操作系统原理-线上选择题库.pdf"
)
OUTPUT_JSON = Path(__file__).with_name("questions.json")


def read_pdf_text(pdf_path: Path) -> str:
    errors = []

    try:
        import fitz  # type: ignore

        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception as exc:
        errors.append(f"pymupdf: {exc}")

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        errors.append(f"pypdf: {exc}")

    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(pdf_path)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:
        errors.append(f"pdfplumber: {exc}")

    joined = "\n".join(errors)
    raise RuntimeError(
        "没有可用的 PDF 读取库。请先安装其中一个：python -m pip install pymupdf pypdf pdfplumber\n"
        + joined
    )


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\u3000]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def find_answer_map(text: str) -> dict[int, str]:
    answers: dict[int, str] = {}
    patterns = [
        r"(?P<num>\d+)\s*[\.、]?\s*(?:答案|参考答案|正确答案)\s*[:：]?\s*(?P<ans>[ABCD])",
        r"(?:答案|参考答案|正确答案)\s*[:：]?\s*(?P<ans>[ABCD])\s*(?:\(|（)?\s*(?P<num>\d+)?",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.I):
            num = match.groupdict().get("num")
            ans = match.groupdict().get("ans")
            if num and ans:
                answers[int(num)] = ans.upper()

    for line in text.splitlines():
        for num, ans in re.findall(r"(\d+)\s*[\.、:：]\s*([ABCD])\b", line, flags=re.I):
            answers.setdefault(int(num), ans.upper())
    return answers


def split_question_blocks(text: str) -> list[tuple[int, str]]:
    marker = re.compile(r"(?m)^\s*(\d+)\s*[\.、]\s*")
    matches = list(marker.finditer(text))
    blocks: list[tuple[int, str]] = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        number = int(match.group(1))
        block = text[start:end].strip()
        if re.search(r"\bA\s*[\.、．]", block) and re.search(r"\bB\s*[\.、．]", block):
            blocks.append((number, block))

    return blocks


def parse_options(block: str) -> tuple[str, dict[str, str], str | None]:
    inline_answer = None
    answer_match = re.search(r"(?:答案|参考答案|正确答案)\s*[:：]?\s*([ABCD])", block, flags=re.I)
    if answer_match:
        inline_answer = answer_match.group(1).upper()
        block = block[: answer_match.start()] + block[answer_match.end() :]

    option_marker = re.compile(r"(?s)([ABCD])\s*[\.、．]\s*")
    matches = list(option_marker.finditer(block))
    if len(matches) < 2:
        return block.strip(), {}, inline_answer

    stem = block[: matches[0].start()].strip()
    stem = re.sub(r"^\d+\s*[\.、]\s*", "", stem).strip()
    options: dict[str, str] = {}

    for index, match in enumerate(matches):
        key = match.group(1).upper()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        value = block[start:end].strip()
        value = re.sub(r"\s+", " ", value)
        value = re.sub(r"(?:答案|参考答案|正确答案)\s*[:：]?\s*[ABCD].*$", "", value, flags=re.I).strip()
        options[key] = value

    return re.sub(r"\s+", " ", stem), options, inline_answer


def parse_questions(text: str) -> list[dict[str, object]]:
    text = normalize_text(text)
    answer_map = find_answer_map(text)
    questions = []

    for number, block in split_question_blocks(text):
        stem, options, inline_answer = parse_options(block)
        if not stem or len(options) < 2:
            continue

        question = {
            "id": number,
            "stem": stem,
            "options": {key: options[key] for key in "ABCD" if key in options},
            "answer": inline_answer or answer_map.get(number),
        }
        questions.append(question)

    seen = set()
    deduped = []
    for question in questions:
        qid = question["id"]
        if qid in seen:
            continue
        seen.add(qid)
        deduped.append(question)
    return deduped


def main() -> int:
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf_path.exists():
        print(f"找不到 PDF：{pdf_path}", file=sys.stderr)
        return 1

    text = read_pdf_text(pdf_path)
    questions = parse_questions(text)
    if not questions:
        print("没有解析到选择题。可能需要根据 PDF 文本排版调整解析规则。", file=sys.stderr)
        return 2

    OUTPUT_JSON.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    with_answer = sum(1 for item in questions if item.get("answer"))
    print(f"已生成：{OUTPUT_JSON}")
    print(f"题目数量：{len(questions)}，含答案：{with_answer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
