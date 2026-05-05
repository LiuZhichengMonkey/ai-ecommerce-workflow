#!/usr/bin/env python3
"""
文案迭代脚本 — 自动 gen → review → 修改 → review 循环直到 ≥80分

Usage:
    python copywriting_iterate.py \
        --product "男士云朵棉睡衣套装" \
        --fabric "云朵棉泡泡纱" \
        --color "浅蓝色" \
        --features "短袖翻领,白色滚边,胸前双口袋" \
        --platform xiaohongshu \
        --type long \
        --max-rounds 5 \
        --output final_copy.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


CODEX_PATH = "C:/Users/zhicheng.liu/AppData/Roaming/npm/codex.cmd"


def run_command(cmd: list, input_text: str) -> str:
    """运行 codex exec 命令并返回输出"""
    result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def generate_round_1(product: str, fabric: str, color: str, features: str,
                     platform: str, copy_type: str) -> tuple:
    """第一轮：生成初版文案"""
    from copywriting_gen import load_template, load_anti_ai_constraints, build_gen_prompt

    template = load_template(platform)
    constraints = load_anti_ai_constraints()
    prompt = build_gen_prompt(product, fabric, color, features, platform, copy_type, template, constraints)

    print(f"\n{'='*60}")
    print(f"Round 1: 生成初版 {platform} {copy_type} 文案")
    print(f"{'='*60}")

    output = run_command([CODEX_PATH, "exec", "--skip-git-repo-check"], prompt)
    copy_text = extract_copy_from_output(output)

    print(f"文案长度: {len(copy_text)} 字")
    return copy_text


def generate_round_n(product: str, fabric: str, color: str, features: str,
                     platform: str, copy_type: str, prev_copy: str,
                     ai_sentences: list, suggestions: list, round_num: int) -> str:
    """第N轮：基于review反馈修改文案"""

    platform_name = "小红书" if platform == "xiaohongshu" else "淘宝"

    # 构建AI感句子列表
    ai_sentences_text = "\n".join([f'- "{item["sentence"]}"' for item in ai_sentences]) if ai_sentences else "无"

    # 构建修改建议列表
    suggestions_text = "\n".join([
        f'{i+1}. 原文: "{item["original"]}" → 建议改为: "{item["suggestion"]}"'
        for i, item in enumerate(suggestions)
    ]) if suggestions else "无"

    prompt = f"""你是一个真实的小红书/淘宝文案写手。上一版文案被审核人指出有AI感，需要重写。

## 商品信息
- 商品名称：{product}
- 面料：{fabric}
- 颜色：{color}
- 核心卖点：{features}

## 上一版文案（有AI感，需要重写）
---
{prev_copy}
---

## 被指出的AI感句子（必须避免）
{ai_sentences_text}

## 修改建议（必须参考）
{suggestions_text}

## 重写要求
1. 彻底重写，不要保留任何AI感句子
2. 保持{platform_name}平台的调性和结构
3. 更加口语化，像真实用户在分享
4. 加入更多个人化细节（具体时间/地点/人物）
5. 句子长短不一，有错别字或不完整短句也没关系
6. 直接输出新文案，不要解释

## 开始重写
"""

    print(f"\n{'='*60}")
    print(f"Round {round_num}: 基于反馈重写 {platform} {copy_type} 文案")
    print(f"{'='*60}")

    output = run_command([CODEX_PATH, "exec", "--skip-git-repo-check"], prompt)
    copy_text = extract_copy_from_output(output)

    print(f"文案长度: {len(copy_text)} 字")
    return copy_text


def review_copy(copy_text: str, platform: str) -> dict:
    """Review文案"""
    from copywriting_review import build_review_prompt, parse_review_output

    prompt = build_review_prompt(copy_text, platform)
    output = run_command([CODEX_PATH, "exec", "--skip-git-repo-check"], prompt)
    review = parse_review_output(output)
    review["raw_output"] = output
    return review


def extract_copy_from_output(output: str) -> str:
    """从 codex 输出中提取文案内容"""
    lines = output.split("\n")
    copy_lines = []
    in_copy = False

    for line in lines:
        # 跳过元数据行
        if line.startswith("user") or line.startswith("codex") or line.startswith("exec"):
            in_copy = False
            continue
        if line.startswith("--------") or line.startswith("session id"):
            in_copy = False
            continue
        if "tokens used" in line or "Exit code" in line:
            in_copy = False
            continue
        if line.startswith("{") or line.startswith("STDERR"):
            continue

        # 启发式：找到第一个非空且不是特殊标记的行开始
        if not in_copy and line.strip() and len(line.strip()) > 10:
            # 检查是否是评分格式，如果是则跳过
            if not any(kw in line for kw in ["真实感", "框架匹配", "卖点传达", "口语化", "感染力", "总分", "等级", "AI感", "修改建议"]):
                in_copy = True
                copy_lines.append(line)
        elif in_copy:
            # 检查是否进入评分部分
            if any(kw in line for kw in ["真实感", "框架匹配", "卖点传达", "总分", "等级", "AI感句子", "修改建议", "是否进入下一轮"]):
                in_copy = False
                continue
            copy_lines.append(line)

    copy_text = "\n".join(copy_lines).strip()

    # 如果提取为空，尝试更简单的方法
    if not copy_text or len(copy_text) < 50:
        paragraphs = output.split("\n\n")
        for p in reversed(paragraphs):
            p = p.strip()
            if p and len(p) > 100:
                # 排除评分相关的段落
                if not any(kw in p for kw in ["真实感:", "总分:", "等级:", "AI感句子", "修改建议"]):
                    copy_text = p
                    break

    return copy_text


def iterate(product: str, fabric: str, color: str, features: str,
            platform: str, copy_type: str, max_rounds: int) -> dict:
    """主迭代流程"""

    rounds = []
    current_copy = ""

    for round_num in range(1, max_rounds + 1):
        if round_num == 1:
            current_copy = generate_round_1(product, fabric, color, features, platform, copy_type)
        else:
            prev_review = rounds[-1]["review"]
            current_copy = generate_round_n(
                product, fabric, color, features, platform, copy_type,
                rounds[-1]["copy"],
                prev_review.get("ai_sentences", []),
                prev_review.get("suggestions", []),
                round_num,
            )

        # Review
        review = review_copy(current_copy, platform)

        round_data = {
            "round": round_num,
            "copy": current_copy,
            "review": review,
        }
        rounds.append(round_data)

        print(f"\n--- Round {round_num} 评分 ---")
        print(f"真实感: {review['realism']}/20")
        print(f"框架匹配: {review['framework']}/15")
        print(f"卖点传达: {review['selling_point']}/15")
        print(f"口语化: {review['colloquial']}/10")
        print(f"感染力: {review['appeal']}/10")
        print(f"加权总分: {review['weighted_total']}/100")
        print(f"等级: {review['grade']}级")

        if review["weighted_total"] >= 95:
            print(f"\n✅ 达到目标分数（≥95），迭代结束！")
            break
        elif round_num >= max_rounds:
            print(f"\n⚠️ 达到最大轮数（{max_rounds}轮），当前分数 {review['weighted_total']}，未达到80分")
        else:
            print(f"\n🔄 分数未达标，进入 Round {round_num + 1}...")

    # 找出最高分的版本
    best_round = max(rounds, key=lambda r: r["review"]["weighted_total"])

    return {
        "meta": {
            "product": product,
            "fabric": fabric,
            "color": color,
            "features": features,
            "platform": platform,
            "type": copy_type,
        },
        "best_round": best_round["round"],
        "best_score": best_round["review"]["weighted_total"],
        "best_copy": best_round["copy"],
        "rounds": rounds,
    }


def main():
    parser = argparse.ArgumentParser(description="文案迭代优化脚本")
    parser.add_argument("--product", required=True, help="商品名称")
    parser.add_argument("--fabric", required=True, help="面料")
    parser.add_argument("--color", required=True, help="颜色")
    parser.add_argument("--features", required=True, help="核心卖点，逗号分隔")
    parser.add_argument("--platform", required=True, choices=["xiaohongshu", "taobao"], help="平台")
    parser.add_argument("--type", required=True, choices=["long", "short"], help="文案类型")
    parser.add_argument("--max-rounds", type=int, default=5, help="最大迭代轮数")
    parser.add_argument("--output", default="final_copy.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    result = iterate(
        product=args.product,
        fabric=args.fabric,
        color=args.color,
        features=args.features,
        platform=args.platform,
        copy_type=args.type,
        max_rounds=args.max_rounds,
    )

    out_path = Path(args.output)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"迭代完成！")
    print(f"{'='*60}")
    print(f"最佳版本: Round {result['best_round']}")
    print(f"最佳分数: {result['best_score']}/100")
    print(f"总轮数: {len(result['rounds'])}")
    print(f"输出文件: {out_path.resolve()}")
    print(f"\n--- 最终文案 ---\n{result['best_copy'][:800]}...")


if __name__ == "__main__":
    main()
