#!/usr/bin/env python3
"""
电商文案生成器 — 小红书/淘宝文案自动生成
基于框架模板 + 去AI感约束，通过 Codex CLI 生成

Usage:
    python copywriting_gen.py \
        --product "男士云朵棉睡衣套装" \
        --fabric "云朵棉泡泡纱" \
        --color "浅蓝色" \
        --features "短袖翻领,白色滚边,胸前双口袋" \
        --platform xiaohongshu \
        --type long \
        --output copy.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_template(platform: str) -> str:
    """加载平台文案框架模板"""
    template_dir = Path.home() / "templates"
    if platform == "xiaohongshu":
        path = template_dir / "xiaohongshu_copy.md"
    else:
        path = template_dir / "taobao_copy.md"
    return path.read_text(encoding="utf-8")


def load_anti_ai_constraints() -> str:
    """加载去AI感约束词库"""
    path = Path.home() / "templates" / "anti_ai_constraints.md"
    return path.read_text(encoding="utf-8")


def build_gen_prompt(product: str, fabric: str, color: str, features: str,
                     platform: str, copy_type: str, template: str, constraints: str) -> str:
    """构建文案生成 prompt"""

    platform_name = "小红书" if platform == "xiaohongshu" else "淘宝"
    type_name = "长文案" if copy_type == "long" else "短文案（1-2句slogan）"

    prompt = f"""你是一个真实的小红书/淘宝文案写手，不是AI助手。你的文风口语化、有个人色彩、不完美但真实。

## 任务
为以下商品写一份{platform_name} {type_name}。

## 商品信息
- 商品名称：{product}
- 面料：{fabric}
- 颜色：{color}
- 核心卖点/特征：{features}

## 文案框架
{template}

## 去AI感约束（严格遵守）
{constraints}

## 输出要求
- 输出必须是纯文案，不要解释、不要分析、不要JSON格式
- 用自然的中文口语写作
- 句子长短不一，有错别字或不完整短句更真实
- 有具体时间/地点/人物
- 直接输出文案内容

## 开始写作
"""
    return prompt


def generate_copy(product: str, fabric: str, color: str, features: str,
                  platform: str, copy_type: str) -> str:
    """调用 Codex CLI 生成文案"""
    template = load_template(platform)
    constraints = load_anti_ai_constraints()
    prompt = build_gen_prompt(product, fabric, color, features, platform, copy_type, template, constraints)

    codex_path = "C:/Users/zhicheng.liu/AppData/Roaming/npm/codex.cmd"
    cmd = [codex_path, "exec", "--skip-git-repo-check"]

    print(f"正在生成 {platform} {copy_type} 文案...")
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    output = result.stdout
    if result.stderr and "Reading prompt from stdin" not in result.stderr:
        print(f"STDERR: {result.stderr}", file=sys.stderr)

    # 从 codex 输出中提取文案内容
    # codex exec 的输出格式包含对话内容，我们需要提取最后的 assistant 回复
    lines = output.split("\n")
    copy_lines = []
    in_copy = False
    for line in lines:
        if line.startswith("user") or line.startswith("codex") or line.startswith("exec"):
            in_copy = False
            continue
        if line.startswith("--------") or line.startswith("session id"):
            in_copy = False
            continue
        if "tokens used" in line or "Exit code" in line:
            in_copy = False
            continue
        if in_copy:
            copy_lines.append(line)
        elif line.strip() and not line.startswith("{") and not line.startswith("STDERR"):
            # 尝试找到文案开始的位置
            in_copy = True
            copy_lines.append(line)

    copy_text = "\n".join(copy_lines).strip()

    # 如果提取为空，返回原始输出的一部分
    if not copy_text:
        # 简单启发式：找最后一个非空大段落
        paragraphs = output.split("\n\n")
        for p in reversed(paragraphs):
            p = p.strip()
            if p and len(p) > 50 and not p.startswith("{") and not p.startswith("codex"):
                copy_text = p
                break

    return copy_text


def main():
    parser = argparse.ArgumentParser(description="电商文案生成器")
    parser.add_argument("--product", required=True, help="商品名称")
    parser.add_argument("--fabric", required=True, help="面料")
    parser.add_argument("--color", required=True, help="颜色")
    parser.add_argument("--features", required=True, help="核心卖点，逗号分隔")
    parser.add_argument("--platform", required=True, choices=["xiaohongshu", "taobao"], help="平台")
    parser.add_argument("--type", required=True, choices=["long", "short"], help="文案类型")
    parser.add_argument("--output", default="copy.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    copy_text = generate_copy(
        product=args.product,
        fabric=args.fabric,
        color=args.color,
        features=args.features,
        platform=args.platform,
        copy_type=args.type,
    )

    output = {
        "meta": {
            "product": args.product,
            "fabric": args.fabric,
            "color": args.color,
            "features": args.features,
            "platform": args.platform,
            "type": args.type,
        },
        "copy": copy_text,
        "round": 1,
        "score": None,
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"文案已保存至: {out_path.resolve()}")
    print(f"\n--- 文案预览 ---\n{copy_text[:500]}...")


if __name__ == "__main__":
    main()
