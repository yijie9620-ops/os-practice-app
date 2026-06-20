import http.server
import os
import socketserver
import subprocess
import sys
import webbrowser
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
START_PORT = 8765


def run_extractor() -> None:
    extractor = APP_DIR / "extract_questions.py"
    output = APP_DIR / "questions.json"
    if output.exists():
        return

    print("正在生成题库 questions.json ...")
    result = subprocess.run([sys.executable, str(extractor)], cwd=str(APP_DIR))
    if result.returncode != 0:
        print("题库生成失败。网页仍会启动，但只会显示示例题或等待你手动导入 JSON。")


def main() -> int:
    run_extractor()
    os.chdir(APP_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True

    for port in range(START_PORT, START_PORT + 20):
        try:
            server = socketserver.TCPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            server = None

    if server is None:
        print("没有找到可用端口，请稍后再试。")
        return 1

    with server:
        url = f"http://127.0.0.1:{server.server_address[1]}/index.html"
        print(f"练习程序已启动：{url}")
        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n已退出。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
