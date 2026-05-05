#!/usr/bin/env python3
"""
小红书封面生成器 — 按风格自动选择模板并输出完整 JSON prompt

Usage:
    python xiaohongshu_cover_gen.py \
        --style magazine \
        --topic "夏日睡衣推荐" \
        --product "男士云朵棉睡衣" \
        --color "浅蓝色" \
        --ref "C:/path/to/reference.jpg" \
        --ratio 3:4 \
        --output cover_prompt.json

    # 批量生成全部风格
    python xiaohongshu_cover_gen.py \
        --style all \
        --topic "夏日睡衣推荐" \
        --product "男士云朵棉睡衣" \
        --ref "C:/path/to/reference.jpg"

风格选项:
    magazine   - 杂志留白风
    bold       - 大色块冲击风
    collage    - 拼贴风
    cozy       - 质感氛围风
"""

import argparse
import json
import sys
from pathlib import Path


TEMPLATES = {
    "magazine": {
        "style_name": "杂志留白风",
        "style_desc": "高级感杂志封面，大量留白，精致排版，奶咖/米白基调",
        "layout": {
            "subject_ratio": "65%",
            "text_area": "底部或左侧三分之一留白",
            "text_lines": "2-3行",
            "grid": None
        },
        "scene": {
            "setting": "温馨卧室或生活场景，浅米色/奶油白背景，柔和自然光",
            "lighting": "自然窗光，柔和侧光，暖调",
            "mood": "慵懒、舒适、治愈、高级感"
        },
        "subject_pose": "产品自然摆放于床铺或沙发上，搭配同色系抱枕和毯子，呈现真实居家场景，氛围慵懒舒适",
        "color_palette": ["奶咖", "米白", "浅灰", "淡粉"],
        "typography": {
            "title_font": "粗体无衬线或 elegant serif",
            "color": "深棕或奶白色，与背景高对比",
            "position": "底部居中或左下角",
            "decoration": "细线条分隔符，极简"
        },
        "rendering": {
            "vibe": "真实生活感+杂志设计感，拒绝过度精修",
            "quality": "高清",
            "forbidden": ["夸张滤镜", "冷白皮", "3D渲染感", "杂乱背景"]
        }
    },

    "bold": {
        "style_name": "大色块冲击风",
        "style_desc": "高饱和度色块背景，强对比文字区域，视觉冲击力极强",
        "layout": {
            "subject_ratio": "60%",
            "text_area": "上半部分或左侧大色块区域",
            "text_lines": "1-2行大字标题",
            "color_blocks": True
        },
        "subject_pose": "产品正面平铺或手持展示，背景为纯色色块，主体突出，画面干净无多余杂物",
        "scene": {
            "setting": "纯色高饱和背景或几何色块拼接",
            "lighting": "均匀明亮，无阴影",
            "mood": "活力、醒目、种草感强"
        },
        "color_palette": ["亮黄", "粉紫", "薄荷绿", "亮橙"],
        "typography": {
            "title_font": "超粗体无衬线，大字报风格",
            "color": "白色或黑色，与色块形成极端对比",
            "position": "色块区域内居中",
            "decoration": "无装饰，纯粹色块+文字"
        },
        "rendering": {
            "vibe": "设计感+冲击力，适合干货/清单类笔记",
            "quality": "高清",
            "forbidden": ["渐变色", "过多细节", "柔和色调"]
        }
    },

    "collage": {
        "style_name": "拼贴风",
        "style_desc": "多图拼贴，网格布局，手账感，贴纸和胶带元素",
        "layout": {
            "subject_ratio": "70%",
            "text_area": "穿插于拼贴之间",
            "text_lines": "2-3行",
            "grid": "2x2 或 3x3 不规则拼贴"
        },
        "scene": {
            "setting": "多种材质背景拼接（牛皮纸、格纹布、照片边）",
            "lighting": "自然光，温暖",
            "mood": "手作感、亲切、分享欲强"
        },
        "subject_pose": "多张小图拼贴：产品平铺图、面料特写、穿搭效果图，排列于手账风背景上，胶带和贴纸装饰点缀",
        "color_palette": ["牛皮纸黄", "淡粉", "薄荷绿", "灰蓝"],
        "typography": {
            "title_font": "手写体或圆体",
            "color": "深棕或黑色",
            "position": "拼贴空隙处",
            "decoration": "胶带贴纸、手绘箭头、小图标"
        },
        "rendering": {
            "vibe": "真实手账拼贴感，每张小图都有独立内容",
            "quality": "高清",
            "forbidden": ["完美对称", "机械感", "商业大片感"]
        }
    },

    "cozy": {
        "style_name": "质感氛围风",
        "style_desc": "暖调柔光，朦胧感，强调情绪和氛围，适合深夜/治愈内容",
        "layout": {
            "subject_ratio": "60%",
            "text_area": "底部小字",
            "text_lines": "1-2行",
            "grid": None
        },
        "subject_pose": "产品搭在沙发扶手或随意铺在床上，旁边有暖光台灯/香薰蜡烛，画面大面积暗部，情绪感强",
        "scene": {
            "setting": "温暖室内，烛光/台灯柔光，背景浅景深虚化",
            "lighting": "暖黄点光源，大面积暗部，高对比",
            "mood": "私密、温暖、治愈、深夜氛围"
        },
        "color_palette": ["暖黄", "深棕", "焦糖", "暗红"],
        "typography": {
            "title_font": "细衬线或手写体",
            "color": "奶白或浅金",
            "position": "底部小字，不打扰画面",
            "decoration": "无"
        },
        "rendering": {
            "vibe": "电影感+情绪片，模糊背景突出主体情绪",
            "quality": "高清",
            "forbidden": ["明亮日光", "冷色调", "清晰背景"]
        }
    }
}


def build_prompt(style_key: str, topic: str, product: str, color: str, ref_note: str, ratio: str = "3:4") -> dict:
    """根据风格模板构建完整小红书封面 JSON"""
    template = TEMPLATES[style_key]

    return {
        "type": "小红书种草封面",
        "aspect_ratio": ratio,
        "platform": "xiaohongshu",
        "style": f"{template['style_name']}，{template['style_desc']}",
        "reference_image_note": ref_note,
        "layout": template["layout"],
        "scene": template["scene"],
        "subject": {
            "type": "生活方式展示",
            "product": product,
            "pose": template.get("subject_pose", "自然摆放或平铺，呈现真实使用场景"),
            "outfit": {
                "item": f"{product}，{color}"
            }
        },
        "typography": {
            **template["typography"],
            "title": topic
        },
        "color_palette": template["color_palette"],
        "rendering": template["rendering"]
    }


def generate_single(style_key: str, topic: str, product: str, color: str,
                    ref_path: Path, ref_note: str, ratio: str, output_base: Path) -> dict:
    """生成单个风格的 prompt"""
    prompt = build_prompt(style_key, topic, product, color, ref_note, ratio)

    out_name = output_base.stem + f"_{style_key}" + output_base.suffix
    out_path = output_base.parent / out_name

    output = {
        "meta": {
            "style": TEMPLATES[style_key]["style_name"],
            "topic": topic,
            "product": product,
            "reference_image": str(ref_path.resolve()),
            "aspect_ratio": ratio,
            "note": "GPT Image 2 文字渲染能力有限，建议生成后使用 Canva/PS 后期加字"
        },
        "prompt": prompt
    }

    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "style": style_key,
        "style_name": TEMPLATES[style_key]["style_name"],
        "path": out_path,
        "color_palette": TEMPLATES[style_key]["color_palette"],
        "position": TEMPLATES[style_key]["typography"]["position"],
        "font": TEMPLATES[style_key]["typography"]["title_font"]
    }


def main():
    parser = argparse.ArgumentParser(description="小红书封面生成器")
    parser.add_argument("--style", required=True,
                        help="封面风格: magazine/bold/collage/cozy，或用 all 生成全部")
    parser.add_argument("--topic", required=True, help="封面标题/主题，如：夏日睡衣推荐")
    parser.add_argument("--product", required=True, help="产品名称，如：男士云朵棉睡衣")
    parser.add_argument("--color", default="浅蓝色", help="产品颜色")
    parser.add_argument("--ref", required=True, help="参考图路径")
    parser.add_argument("--ratio", default="3:4", choices=["1:1", "3:4", "4:3"],
                        help="封面比例，默认 3:4")
    parser.add_argument("--output", default="xiaohongshu_cover.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    ref_path = Path(args.ref)
    if not ref_path.exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)

    if args.style != "all" and args.style not in TEMPLATES:
        print(f"错误: 未知风格 '{args.style}'，可用: {', '.join(TEMPLATES.keys())} 或 all", file=sys.stderr)
        sys.exit(1)

    ref_note = f"参考图中为{args.product}。生成时必须保持同款版型、面料质感和{args.color}颜色准确还原"
    output_base = Path(args.output)

    if args.style == "all":
        results = []
        for style_key in TEMPLATES:
            result = generate_single(style_key, args.topic, args.product, args.color,
                                     ref_path, ref_note, args.ratio, output_base)
            results.append(result)
        print(f"已生成全部 {len(results)} 种风格封面 prompt")
        for r in results:
            print(f"  [{r['style']}] {r['style_name']} -> {r['path'].resolve()}")
            print(f"       配色: {', '.join(r['color_palette'])} | 排版: {r['position']}")
    else:
        result = generate_single(args.style, args.topic, args.product, args.color,
                                 ref_path, ref_note, args.ratio, output_base)
        print(f"已生成「{result['style_name']}」封面 prompt")
        print(f"主题: {args.topic}")
        print(f"保存至: {result['path'].resolve()}")
        print(f"\n配色建议: {', '.join(result['color_palette'])}")
        print(f"排版提示: {result['position']} — {result['font']}")


if __name__ == "__main__":
    main()
