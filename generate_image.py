#!/usr/bin/env python3
"""
Codex Image Generation Wrapper — 绕过 PowerShell 中文编码问题
正确传递 UTF-8 提示词给 Codex CLI

Usage:
    python generate_image.py prompt_v3.txt "C:/path/to/reference.jpg"
"""

import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_image.py <prompt_file> <reference_image_path>")
        sys.exit(1)

    prompt_file = Path(sys.argv[1])
    ref_image = Path(sys.argv[2])

    if not prompt_file.exists():
        print(f"错误: 提示词文件不存在: {prompt_file}")
        sys.exit(1)
    if not ref_image.exists():
        print(f"错误: 参考图不存在: {ref_image}")
        sys.exit(1)

    # 用 UTF-8 读取中文提示词
    prompt = prompt_file.read_text(encoding="utf-8")

    # 调用 codex exec，通过 stdin 传入提示词
    # Windows 下需要完整路径，否则 subprocess 找不到 npm 全局安装的命令
    codex_path = "C:/Users/zhicheng.liu/AppData/Roaming/npm/codex.cmd"
    cmd = [
        codex_path, "exec",
        "--skip-git-repo-check",
        "-i", str(ref_image),
    ]

    print(f"正在生成图片...")
    print(f"  提示词: {prompt_file}")
    print(f"  参考图: {ref_image}")
    print()

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)

    print(f"\nExit code: {result.returncode}")


if __name__ == "__main__":
    main()
