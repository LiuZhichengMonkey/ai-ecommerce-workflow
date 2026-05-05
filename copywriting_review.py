#!/usr/bin/env python3
"""
文案 Review Agent — 5维度评分 + AI感句子标注 + 修改建议

Usage:
    python copywriting_review.py \
        --input copy.json \
        --platform xiaohongshu \
        --output review.json
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def build_review_prompt(copy_text: str, platform: str) -> str:
    """构建 Review Agent prompt"""

    platform_name = "小红书" if platform == "xiaohongshu" else "淘宝"

    prompt = f"""你是一个资深电商文案审核人，有10年小红书/淘宝文案撰写经验。你非常讨厌AI生成的模板化文案，能一眼认出AI感。

## 任务
对以下{platform_name}文案进行评分和审查。

## 文案内容
---
{copy_text}
---

## 评分标准（满分100分，目标≥95分，请严格打分）

### 1. 真实感（权重 2.0x，满分20分）
- 20分：像真实用户写的，有个人色彩，不完美，完全看不出AI痕迹
- 17分：很真实，但1-2处略有AI感
- 14分：比较真实，但部分段落像AI
- 10分：中等，AI感明显
- 5分：明显AI生成，模板化严重
- 0分：完全不像人写的

### 2. 框架匹配（权重 1.5x，满分15分）
- 15分：完全符合{platform_name}爆款结构
- 10分：基本符合，缺1个环节
- 5分：结构混乱，缺多个环节
- 0分：完全不符合平台调性

### 3. 卖点传达（权重 1.5x，满分15分）
- 15分：核心卖点清晰自然，不生硬植入
- 10分：卖点提到但不突出
- 5分：卖点模糊或强行植入
- 0分：完全没有卖点

### 4. 口语化（权重 1.0x，满分10分）
- 10分：读起来像聊天，完全口语化
- 7分：比较口语，但部分句子书面
- 4分：半书面半口语
- 0分：完全书面语/说明书口吻

### 5. 感染力（权重 1.0x，满分10分）
- 10分：让人有购买欲/收藏欲
- 7分：有一定吸引力
- 4分：平淡，读完无感
- 0分：完全无感染力

## AI感句子标注
标出3-5个最有AI感的句子，用引号括起来，说明为什么像AI。

## 修改建议
给出3-5条具体修改建议，每条建议对应一个具体的句子改写。

## 输出格式（必须严格按此格式）

```
真实感: XX/20
框架匹配: XX/15
卖点传达: XX/15
口语化: XX/10
感染力: XX/10
总分: XX/70（加权后总分: XX/100）
等级: X级

AI感句子:
1. "..." — 原因
2. "..." — 原因
3. "..." — 原因

修改建议:
1. 原文: "..."
   建议: "..."
2. 原文: "..."
   建议: "..."
3. 原文: "..."
   建议: "..."

是否进入下一轮: 是/否
```

## 开始评分
"""
    return prompt


def parse_review_output(output: str) -> dict:
    """从 codex 输出中解析评分结果"""
    result = {
        "realism": 0,
        "framework": 0,
        "selling_point": 0,
        "colloquial": 0,
        "appeal": 0,
        "raw_total": 0,
        "weighted_total": 0,
        "grade": "D",
        "ai_sentences": [],
        "suggestions": [],
        "continue": False,
    }

    # 提取各项分数
    realism_match = re.search(r"真实感[:：]\s*(\d+)/20", output)
    if realism_match:
        result["realism"] = int(realism_match.group(1))

    framework_match = re.search(r"框架匹配[:：]\s*(\d+)/15", output)
    if framework_match:
        result["framework"] = int(framework_match.group(1))

    selling_match = re.search(r"卖点传达[:：]\s*(\d+)/15", output)
    if selling_match:
        result["selling_point"] = int(selling_match.group(1))

    colloquial_match = re.search(r"口语化[:：]\s*(\d+)/10", output)
    if colloquial_match:
        result["colloquial"] = int(colloquial_match.group(1))

    appeal_match = re.search(r"感染力[:：]\s*(\d+)/10", output)
    if appeal_match:
        result["appeal"] = int(appeal_match.group(1))

    raw_match = re.search(r"总分[:：]\s*(\d+)/70", output)
    if raw_match:
        result["raw_total"] = int(raw_match.group(1))

    weighted_match = re.search(r"加权后总分[:：]\s*(\d+)/100", output)
    if weighted_match:
        result["weighted_total"] = int(weighted_match.group(1))
    else:
        # 手动计算加权总分
        result["weighted_total"] = round(
            result["realism"] * 2.0 +
            result["framework"] * 1.5 +
            result["selling_point"] * 1.5 +
            result["colloquial"] * 1.0 +
            result["appeal"] * 1.0
        )

    grade_match = re.search(r"等级[:：]\s*([ABCD])级", output)
    if grade_match:
        result["grade"] = grade_match.group(1)
    else:
        # 根据加权总分定等级
        w = result["weighted_total"]
        if w >= 80:
            result["grade"] = "A"
        elif w >= 60:
            result["grade"] = "B"
        elif w >= 40:
            result["grade"] = "C"
        else:
            result["grade"] = "D"

    # 提取AI感句子
    ai_section = re.search(r"AI感句子[:：]?(.*?)(?=修改建议|是否进入下一轮|$)", output, re.DOTALL)
    if ai_section:
        ai_text = ai_section.group(1)
        ai_lines = re.findall(r'\d+\.\s*"([^"]+)"\s*[-—]\s*(.+)', ai_text)
        for sentence, reason in ai_lines:
            result["ai_sentences"].append({"sentence": sentence, "reason": reason.strip()})

    # 提取修改建议
    suggest_section = re.search(r"修改建议[:：]?(.*?)(?=是否进入下一轮|$)", output, re.DOTALL)
    if suggest_section:
        suggest_text = suggest_section.group(1)
        # 匹配 "原文: ... 建议: ..." 格式
        pairs = re.findall(r'原文[:：]\s*"([^"]+)".*?建议[:：]\s*"([^"]+)"', suggest_text, re.DOTALL)
        for original, suggestion in pairs:
            result["suggestions"].append({"original": original, "suggestion": suggestion})

    # 是否继续
    continue_match = re.search(r"是否进入下一轮[:：]\s*(是|否)", output)
    if continue_match:
        result["continue"] = continue_match.group(1) == "是"
    else:
        result["continue"] = result["weighted_total"] < 80

    return result


def review_copy(copy_text: str, platform: str) -> dict:
    """调用 Codex CLI 进行文案评分"""
    prompt = build_review_prompt(copy_text, platform)

    codex_path = "C:/Users/zhicheng.liu/AppData/Roaming/npm/codex.cmd"
    cmd = [codex_path, "exec", "--skip-git-repo-check"]

    print(f"正在 Review {platform} 文案...")
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    output = result.stdout
    review = parse_review_output(output)
    review["raw_output"] = output

    return review


def main():
    parser = argparse.ArgumentParser(description="文案 Review Agent")
    parser.add_argument("--input", required=True, help="文案 JSON 文件路径")
    parser.add_argument("--platform", required=True, choices=["xiaohongshu", "taobao"], help="平台")
    parser.add_argument("--output", default="review.json", help="输出 Review JSON 文件路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    copy_text = data["copy"]

    review = review_copy(copy_text, args.platform)

    output = {
        "meta": data["meta"],
        "review": review,
        "copy": copy_text,
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Review 结果已保存至: {out_path.resolve()}")
    print(f"\n--- 评分结果 ---")
    print(f"真实感: {review['realism']}/20")
    print(f"框架匹配: {review['framework']}/15")
    print(f"卖点传达: {review['selling_point']}/15")
    print(f"口语化: {review['colloquial']}/10")
    print(f"感染力: {review['appeal']}/10")
    print(f"加权总分: {review['weighted_total']}/100")
    print(f"等级: {review['grade']}级")
    print(f"是否继续: {'是' if review['continue'] else '否'}")


if __name__ == "__main__":
    main()
