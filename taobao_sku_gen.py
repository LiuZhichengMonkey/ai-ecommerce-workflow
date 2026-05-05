#!/usr/bin/env python3
"""
淘宝 SKU 多色图生成器 — 批量输出不同颜色/款式的 SKU 平铺图 prompt

Usage:
    python taobao_sku_gen.py \
        --name "男士云朵棉睡衣套装" \
        --desc "短袖翻领，白色滚边，胸前双口袋" \
        --fabric "云朵棉泡泡纱" \
        --colors "浅蓝色,淡粉色,米白色,浅灰色" \
        --ref "C:/path/to/reference.jpg" \
        --output sku_prompts.json

输出每个颜色的独立平铺图 prompt，用于商品选择区域的 SKU 缩略图。
"""

import argparse
import json
import sys
from pathlib import Path


def build_sku_prompt(product_name: str, desc: str, fabric: str, color: str, ref_note: str) -> dict:
    """构建单个 SKU 颜色的 prompt"""
    # 根据 name 和 desc 推断是否有下装
    combined = product_name + desc
    has_bottom = any(k in combined for k in ("套装", "长裤", "短裤", "裤子", "下装", "两件套"))
    bottom_desc = ""
    if "短裤" in desc:
        bottom_desc = f"配套同色短裤，{fabric}面料，{color}"
    elif has_bottom:
        bottom_desc = f"配套同色长裤，{fabric}面料，{color}"

    # 从 desc 提取装饰特征用于 outfit 描述
    trim_detail = ""
    if "滚边" in desc:
        trim_detail = "滚边装饰细节"
    if "口袋" in desc:
        trim_detail += "，口袋对称工整" if trim_detail else "对称口袋设计"
    if "纽扣" in desc:
        trim_detail += "，纽扣有厚度" if trim_detail else "纽扣细节"

    pose = f"{product_name}平铺正面展示"
    if has_bottom:
        pose += "，下装平铺于下方，整体呈标准产品展示摆放"
    pose += f"，必须准确呈现{color}的真实色泽"

    outfit = {
        "item": f"{product_name}，{desc}，{fabric}面料，{color}",
        "detail": f"真实{fabric}面料纹理可见，{trim_detail}，颜色必须严格还原为{color}，不可有色差"
    }
    if bottom_desc:
        outfit["bottom"] = bottom_desc

    return {
        "type": "淘宝SKU颜色图",
        "aspect_ratio": "1:1",
        "platform": "taobao",
        "style": "高清电商SKU颜色展示，纯白背景，颜色准确无色差",
        "reference_image_note": ref_note,
        "layout": {
            "composition": "居中构图",
            "occupancy": "60%",
            "margin": "四周均匀留白"
        },
        "scene": {
            "setting": "纯白色背景 RGB(255,255,255)，无阴影，无道具",
            "lighting": "均匀产品摄影光，消除色差，确保颜色准确还原"
        },
        "subject": {
            "type": "SKU颜色展示",
            "product": product_name,
            "color_variant": color,
            "pose": pose,
            "outfit": outfit
        },
        "camera": {
            "angle": "正上方垂直俯拍",
            "framing": "完整产品入镜，四周留白",
            "quality": "超高清电商标准"
        },
        "rendering": {
            "quality": "超高清",
            "sharpness": "高",
            "color_accuracy": f"极高，必须准确还原{color}，不可有色差",
            "forbidden": ["文字", "牛皮癣", "拼接", "边框", "阴影", "道具", "模特", "滤镜", "色偏"]
        }
    }


def main():
    parser = argparse.ArgumentParser(description="淘宝 SKU 多色图生成器")
    parser.add_argument("--name", required=True, help="商品名称")
    parser.add_argument("--desc", required=True, help="商品款式描述（不含颜色）")
    parser.add_argument("--fabric", required=True, help="面料名称")
    parser.add_argument("--colors", required=True, help="颜色列表，逗号分隔，如：浅蓝色,淡粉色,米白色")
    parser.add_argument("--ref", required=True, help="参考图路径（建议用主色款）")
    parser.add_argument("--output", default="sku_prompts.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    ref_path = Path(args.ref)
    if not ref_path.exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)

    colors = [c.strip() for c in args.colors.split(",") if c.strip()]
    if not colors:
        print("错误: --colors 不能为空，至少提供一个颜色", file=sys.stderr)
        sys.exit(1)

    ref_note = f"参考图中为{args.name}：{args.desc}。生成时必须保持同款版型、面料质感。颜色需按指定色号准确还原"

    prompts = []
    for color in colors:
        prompt = build_sku_prompt(args.name, args.desc, args.fabric, color, ref_note)
        prompts.append({
            "sku_type": "color",
            "variant": color,
            "filename_hint": f"sku_color_{color}.png",
            "prompt": prompt
        })

    output = {
        "meta": {
            "product": args.name,
            "fabric": args.fabric,
            "reference_image": str(ref_path.resolve()),
            "color_count": len(colors),
            "colors": colors,
            "note": "每张SKU图必须保证颜色准确，避免客诉色差"
        },
        "prompts": prompts
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成 {len(colors)} 个 SKU 颜色图 prompt")
    for p in prompts:
        print(f"  [{p['variant']}] -> {p['filename_hint']}")
    print(f"\n保存至: {out_path.resolve()}")
    print("\n[提示] SKU图颜色准确度直接影响退货率，建议生成后与实际面料比对")


if __name__ == "__main__":
    main()
