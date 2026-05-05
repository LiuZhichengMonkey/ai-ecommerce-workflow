#!/usr/bin/env python3
"""
淘宝详情页长图生成器 — 输出详情页各板块的完整 JSON prompt

Usage:
    python taobao_detail_kit.py \
        --name "男士云朵棉睡衣套装" \
        --desc "短袖翻领，浅蓝色，白色滚边，胸前双口袋" \
        --fabric "云朵棉泡泡纱" \
        --color "浅蓝色" \
        --ref "C:/path/to/reference.jpg" \
        --sections poster,fabric,model,detail,care,trust \
        --output detail_prompts.json

    # 覆盖面料技术指标（可选）
    python taobao_detail_kit.py ... \
        --softness-value "46" --comparison-value "99" \
        --softness-level "5级一等面料" --antibacterial-level "7A级抑菌"

详情页板块 (sections):
    poster   - 海报首屏（高颜值场景图+氛围文案）
    emotion  - 情感文案板块（氛围感文字，如"像把云穿上身"）
    size     - 尺码快选（体重+身高对照，降低退货率）
    data_viz - 面料数据可视化（柔软度/透气性对比图表）
    fabric   - 面料成分与工艺特写（含可视化指标）
    model    - 模特场景多角度展示（3-4组不同姿势）
    detail   - 细节卖点（圆领/刺绣/面料/腰头/裤脚/锁边）
    scene    - 多场景穿搭（卧室、客厅、轻度外出）
    care     - 洗护说明标签（5个国标图标）
    trust    - 信任背书（质检报告+售后保障）
"""

import argparse
import json
import sys
from pathlib import Path


SECTIONS = {
    "poster": {
        "name": "海报首屏",
        "type": "淘宝详情页海报",
        "aspect_ratio": "3:4",
        "style": "高级感生活方式海报，温馨卧室场景，大面积留白，杂志风排版",
        "layout": {"subject_ratio": "50%", "text_area": "底部", "text_lines": "1-2行"},
        "scene": {
            "setting": "温馨现代卧室，浅米色亚麻床品，木质床头柜，暖光台灯，窗外柔和晨光",
            "lighting": "自然窗光+暖色台灯光，明暗层次丰富",
            "mood": "慵懒、治愈、高级感"
        },
        "subject": {
            "type": "生活方式场景",
            "pose": "模特自然半躺于床上或坐在沙发边，姿态放松，一手搭在床头或抱枕上，呈现真实居家状态",
            "outfit": {"item": "{product}，{color}"}
        },
        "atmosphere_copy": "云感睡衣，像把云穿上身 | 舒服的家居服，能提升居家生活的幸福感",
        "typography": {
            "title": "{product}",
            "subtitle": "舒适居家 | 从一件好睡衣开始",
            "atmosphere": "云感睡衣，像把云穿上身",
            "font": "优雅衬线体",
            "color": "深棕或奶白色"
        },
        "rendering": {"vibe": "生活方式杂志感", "quality": "超高清", "forbidden": ["牛皮癣", "促销文字", "夸张滤镜"]}
    },

    "emotion": {
        "name": "情感文案",
        "type": "淘宝详情页情感板块",
        "aspect_ratio": "3:4",
        "style": "极简氛围感图文，大字情感文案配模特场景，治愈系视觉",
        "layout": {"composition": "文案为主，模特场景为辅", "text_ratio": "40%", "image_ratio": "60%"},
        "scene": {
            "setting": "浅色干净背景或柔和家居场景，无杂乱道具",
            "lighting": "柔和均匀光，温馨氛围",
            "mood": "治愈、放松、幸福感"
        },
        "subject": {
            "type": "情感氛围展示",
            "pose": "模特自然放松姿态，背对镜头或侧脸，不强调面容",
            "outfit": {"item": "{product}，{color}"}
        },
        "copywriting": [
            "舒服的{product}，能提升居家生活的幸福感。",
            "把{fabric}穿上身，每一次触碰都是柔软。",
            "身体舒服了，怎么动都超放松。"
        ],
        "typography": {
            "font": "简洁无衬线，字重中等",
            "color": "深灰或暖棕色",
            "layout": "左文右图或上文下图"
        },
        "rendering": {"quality": "超高清", "vibe": "真实生活感+情绪共鸣", "forbidden": ["促销文字", "极限词", "牛皮癣"]}
    },

    "size": {
        "name": "尺码快选",
        "type": "淘宝详情页尺码图",
        "aspect_ratio": "3:4",
        "style": "极简电商信息图，体重+身高快选，降低决策门槛",
        "layout": {"composition": "上下分区", "top": "尺码快选卡片", "bottom": "详细参数表", "occupancy": "85%"},
        "scene": {"setting": "纯白色背景 RGB(255,255,255)，无装饰", "lighting": "均匀"},
        "subject": {
            "type": "尺码快选信息图",
            "size_quick_select": {
                "title": "男生尺码快选",
                "format": "圆形/圆角矩形卡片式",
                "sizes": [
                    {"size": "L", "weight": "100-130斤", "height": "165-172cm"},
                    {"size": "XL", "weight": "130-150斤", "height": "172-177cm"},
                    {"size": "2XL", "weight": "150-180斤", "height": "175-183cm"},
                    {"size": "3XL", "weight": "180-200斤", "height": "175-188cm"}
                ]
            },
            "size_chart": {
                "title": "详细尺码表",
                "columns": ["尺码", "身高(cm)", "体重(kg)", "衣长(cm)", "胸围(cm)", "袖长(cm)", "裤长(cm)"],
                "data": [
                    "M | 160-165 | 50-60 | 68 | 104 | 22 | 98",
                    "L | 165-170 | 60-70 | 70 | 108 | 23 | 100",
                    "XL | 170-175 | 70-80 | 72 | 112 | 24 | 102",
                    "XXL | 175-180 | 80-90 | 74 | 116 | 25 | 104"
                ],
                "note": "手工测量，误差1-3cm"
            },
            "model_info": "模特身高175cm，体重70kg，试穿L码",
            "fabric_composition": "面料：{fabric} | 成分：棉100% | 里料：棉100%",
            "standards": "执行标准：GB/T 22844-2009 | 安全类别：GB 18401 B类（直接接触皮肤）"
        },
        "typography": {
            "title_font": "粗体无衬线",
            "body_font": "简洁无衬线",
            "table_style": "细灰色边框，行列清晰分隔",
            "color": "深灰 #333333"
        },
        "rendering": {"quality": "超高清", "forbidden": ["花哨装饰", "多余配色", "模糊文字"]}
    },

    "data_viz": {
        "name": "面料数据可视化",
        "type": "淘宝详情页数据图",
        "aspect_ratio": "3:4",
        "style": "极简数据可视化图表，对比式排版，科技感+高级感",
        "layout": {"composition": "上下分区", "top": "对比图表", "bottom": "指标说明", "occupancy": "75%"},
        "scene": {"setting": "纯白色或极浅灰背景，突出数据", "lighting": "均匀"},
        "subject": {
            "type": "面料数据对比",
            "charts": [
                {
                    "title": "柔软度对比",
                    "type": "横向对比条",
                    "metric": "单位：mN（数值越小越柔软）",
                    "data": [
                        {"label": "本品", "value": "{softness_value}", "level": "{softness_level}", "highlight": True},
                        {"label": "普通面料", "value": "{comparison_value}", "level": "普通面料", "highlight": False}
                    ],
                    "visual": "渐变色条形图，本品用品牌色突出"
                },
                {
                    "title": "核心指标",
                    "type": "标签阵列",
                    "tags": [
                        {"label": "版型", "value": "宽松", "color": "薄荷绿"},
                        {"label": "手感", "value": "柔软", "color": "薄荷绿"},
                        {"label": "弹性", "value": "微弹", "color": "淡黄"},
                        {"label": "厚度", "value": "适中", "color": "淡蓝"}
                    ]
                }
            ],
            "certification": "{antibacterial_level} | {wash_resistance}"
        },
        "typography": {
            "title_font": "粗体无衬线",
            "data_font": "等宽或简洁无衬线",
            "color": "深灰 #333333",
            "highlight_color": "品牌主色（如薄荷绿/浅蓝）"
        },
        "rendering": {"quality": "超高清", "forbidden": ["花哨装饰", "多余配色", "模糊数据", "3D渲染感"]}
    },

    "fabric": {
        "name": "面料成分与工艺",
        "type": "淘宝详情页面料图",
        "aspect_ratio": "3:4",
        "style": "面料质感特写，微距摄影，突出纹理和触感，科技感信息叠加",
        "layout": {"composition": "上下分栏", "top": "面料特写", "bottom": "成分说明+可视化指标", "occupancy": "70%"},
        "scene": {"setting": "纯白色或浅灰背景，突出面料", "lighting": "柔和侧光，突出纹理立体感"},
        "subject": {
            "type": "面料展示",
            "pose": "{fabric}面料平铺特写，展示凸起泡泡颗粒纹理，手指轻按留下凹痕暗示柔软",
            "outfit": {"detail": "面料必须有极其明显的凹凸泡泡纹理，像绉布/豆腐块表面，白色滚边细节，呈现'rua一下'的柔软视觉"},
            "features": ["100%纯棉", "亲肤透气", "不易起球", "水洗不变形"],
            "tech_specs": {
                "softness": "{softness_spec}",
                "breathability": "{breathability}",
                "antibacterial": "{antibacterial_level}",
                "wash_resistance": "{wash_resistance}"
            }
        },
        "typography": {
            "title": "{fabric}面料",
            "body": "100%纯棉 | 亲肤透气 | 柔软舒适",
            "tech_labels": ["防螨抑菌", "50次水洗有效", "远离粉尘螨"],
            "font": "简洁无衬线",
            "color": "深灰"
        },
        "rendering": {"quality": "超高清微距", "forbidden": ["模糊", "滤镜", "3D渲染感"]}
    },

    "model": {
        "name": "模特场景多角度",
        "type": "淘宝详情页模特展示",
        "aspect_ratio": "3:4",
        "style": "真实模特场景摄影，浅色家居背景，3-4组不同姿势展示版型和穿着效果",
        "layout": {"composition": "竖排多张", "occupancy": "70%", "shots": ["坐姿放松", "站立全身", "侧身展示", "局部特写"]},
        "scene": {
            "setting": "浅米色/浅灰色简约家居场景，沙发或床铺，背景干净无杂乱",
            "lighting": "柔和自然光，主光从侧前方照射，阴影自然虚化",
            "mood": "放松、慵懒、自然居家"
        },
        "subject": {
            "type": "模特多角度场景展示",
            "model": "亚洲男性模特，身形匀称，面部模糊或侧脸/低头，不可识别具体人物",
            "poses": [
                {
                    "name": "坐姿放松",
                    "pose": "模特自然坐在沙发上，一手搭扶手，双腿自然分开，展示上衣版型和垂坠感",
                    "copy": "微微自然垂感，不易皱，干净利落。"
                },
                {
                    "name": "站立全身",
                    "pose": "模特自然站立，身体微侧，一手插兜，展示全身版型和H型宽松剪裁",
                    "copy": "宽松H版型，简约翻领，有点小不同。"
                },
                {
                    "name": "侧身展示",
                    "pose": "模特侧身站立，展示裤型轮廓和侧面线条，突出宽松休闲感",
                    "copy": "宽松休闲裤，看起来显腿细。"
                },
                {
                    "name": "局部特写",
                    "pose": "模特坐在沙发边缘，展示脚口锁边和裤脚细节，手轻触面料",
                    "copy": "脚口双线锁边，宽松休闲。"
                }
            ],
            "outfit": {
                "top": "短袖翻领睡衣上衣，{fabric}，{color}",
                "bottom": "配套长裤/短裤，{fabric}，{color}"
            }
        },
        "rendering": {"quality": "超高清", "forbidden": ["文字", "牛皮癣", "模特清晰人脸", "3D渲染感"]}
    },

    "detail": {
        "name": "细节卖点",
        "type": "淘宝详情页细节图",
        "aspect_ratio": "3:4",
        "style": "工艺细节特写，微距质感，工匠精神，五宫格或竖排",
        "layout": {"composition": "五宫格或竖排", "items": ["经典翻领", "精致滚边", "超柔软面料", "对称裤袋/腰头", "脚口锁边"]},
        "scene": {"setting": "纯白色背景，局部微距", "lighting": "柔和侧光"},
        "subject": {
            "type": "工艺细节",
            "pose": "五个细节分别特写：经典翻领、精致滚边工艺、超柔软弹力棉面料、对称裤袋/无痕腰头、脚口双线锁边",
            "outfit": {
                "detail": "每个细节必须清晰可见，滚边有轻微起毛感和纤维外露，纽扣有厚度和反光，口袋对称工整，腰头无痕工艺，脚口双线锁边平整"
            }
        },
        "typography": {
            "labels": ["经典翻领", "精致滚边", "超柔软面料", "舒适腰头", "双线锁边"],
            "font": "简洁无衬线",
            "color": "深灰"
        },
        "rendering": {"quality": "超高清微距", "forbidden": ["模糊", "过度磨皮"]}
    },

    "scene": {
        "name": "多场景穿搭",
        "type": "淘宝详情页场景图",
        "aspect_ratio": "3:4",
        "style": "生活方式场景，温馨居家，可外穿属性",
        "layout": {"composition": "场景氛围", "occupancy": "45%", "context": "居家仪式感"},
        "scene": {
            "setting": "温馨客厅，沙发上搭着同款睡衣，旁边有抱枕和地毯",
            "lighting": "自然窗光，暖调",
            "mood": "放松、惬意、可外穿的时尚感"
        },
        "subject": {
            "type": "场景展示",
            "pose": "睡衣搭在沙发扶手上，或平铺于茶几上，呈现自然使用状态",
            "outfit": {"item": "{product}，{color}"}
        },
        "rendering": {"quality": "高清", "vibe": "真实生活感", "forbidden": ["冷白皮", "过度精修"]}
    },

    "care": {
        "name": "洗护说明标签",
        "type": "淘宝详情页洗护图",
        "aspect_ratio": "1:1",
        "style": "电商信息图，5个国标洗护图标，清晰排版",
        "layout": {"composition": "图标阵列", "occupancy": "60%", "items": 5},
        "scene": {"setting": "纯白色背景", "lighting": "均匀"},
        "subject": {
            "type": "洗护标签",
            "care_labels": [
                {"icon": "水洗盆30度", "text": "最高洗涤温度30度"},
                {"icon": "不可漂白", "text": "不可漂白"},
                {"icon": "悬挂晾干", "text": "悬挂晾干"},
                {"icon": "低温熨烫", "text": "低温熨烫（110度）"},
                {"icon": "不可干洗", "text": "不可干洗"}
            ],
            "additional": "深浅色分开洗涤 | 不可长时间浸泡 | 避免阳光直射晾晒"
        },
        "typography": {
            "title": "洗涤说明",
            "font": "简洁无衬线",
            "icon_style": "国标GB/T 8685规范图标"
        },
        "rendering": {"quality": "高清", "forbidden": ["非标准图标", "模糊"]}
    },

    "trust": {
        "name": "信任背书",
        "type": "淘宝详情页背书图",
        "aspect_ratio": "3:4",
        "style": "极简电商信息图，质检报告+售后承诺",
        "layout": {"composition": "上下分区", "top": "质检报告示意", "bottom": "售后保障"},
        "scene": {"setting": "纯白色背景，专业感", "lighting": "均匀"},
        "subject": {
            "type": "信任背书",
            "certifications": ["GB/T 22844-2009 执行标准", "GB 18401 B类 安全标准", "通过质量检测"],
            "service": ["7天无理由退换", "运费险", "正品保证", "48小时发货"]
        },
        "typography": {
            "title": "品质保障",
            "font": "粗体无衬线",
            "color": "深灰"
        },
        "rendering": {"quality": "高清", "forbidden": ["虚假宣传", "极限词", "伪造证书"]}
    }
}


def build_section(section_key: str, product_name: str, fabric: str, color: str, ref_note: str,
                  softness_value: str = "46", comparison_value: str = "99",
                  softness_level: str = "5级一等面料", softness_spec: str = "46mN（5级一等面料）",
                  breathability: str = "高透气", antibacterial_level: str = "7A级抑菌 / AAAAAAA级",
                  wash_resistance: str = "50次水洗依然有效") -> dict:
    """构建单个详情页板块的 prompt"""
    template = SECTIONS[section_key].copy()

    # 递归替换占位符
    def replace_placeholders(obj):
        if isinstance(obj, str):
            return (obj
                    .replace("{product}", product_name)
                    .replace("{fabric}", fabric)
                    .replace("{color}", color)
                    .replace("{softness_value}", softness_value)
                    .replace("{comparison_value}", comparison_value)
                    .replace("{softness_level}", softness_level)
                    .replace("{softness_spec}", softness_spec)
                    .replace("{breathability}", breathability)
                    .replace("{antibacterial_level}", antibacterial_level)
                    .replace("{wash_resistance}", wash_resistance))
        elif isinstance(obj, dict):
            return {k: replace_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_placeholders(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(replace_placeholders(item) for item in obj)
        elif isinstance(obj, set):
            return {replace_placeholders(item) for item in obj}
        return obj

    template = replace_placeholders(template)
    template["reference_image_note"] = ref_note
    return template


def main():
    parser = argparse.ArgumentParser(description="淘宝详情页长图生成器")
    parser.add_argument("--name", required=True, help="商品名称")
    parser.add_argument("--desc", required=True, help="商品描述")
    parser.add_argument("--fabric", required=True, help="面料名称")
    parser.add_argument("--color", required=True, help="颜色")
    parser.add_argument("--ref", required=True, help="参考图路径")
    parser.add_argument("--sections", default="poster,emotion,size,data_viz,fabric,model,detail,scene,care,trust",
                        help="详情页板块，逗号分隔")
    parser.add_argument("--output", default="detail_prompts.json", help="输出 JSON 文件路径")
    # 面料技术指标（覆盖模板默认值）
    parser.add_argument("--softness-value", default="46", help="柔软度数值（本品）")
    parser.add_argument("--comparison-value", default="99", help="柔软度对比数值（普通面料）")
    parser.add_argument("--softness-level", default="5级一等面料", help="柔软度等级描述")
    parser.add_argument("--softness-spec", default="46mN（5级一等面料）", help="柔软度完整规格")
    parser.add_argument("--breathability", default="高透气", help="透气性描述")
    parser.add_argument("--antibacterial-level", default="7A级抑菌 / AAAAAAA级", help="抑菌等级")
    parser.add_argument("--wash-resistance", default="50次水洗依然有效", help="耐水洗性能")
    args = parser.parse_args()

    ref_path = Path(args.ref)
    if not ref_path.exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)

    ref_note = f"参考图中为{args.name}：{args.desc}。生成时必须保持同款版型、面料质感和滚边细节"

    if args.sections.lower() == "all":
        section_keys = list(SECTIONS.keys())
    else:
        section_keys = [s.strip() for s in args.sections.split(",")]
    invalid = [s for s in section_keys if s not in SECTIONS]
    if invalid:
        print(f"错误: 未知板块: {', '.join(invalid)}", file=sys.stderr)
        print(f"可用板块: {', '.join(SECTIONS.keys())}", file=sys.stderr)
        sys.exit(1)

    prompts = []
    for key in section_keys:
        prompt = build_section(
            key, args.name, args.fabric, args.color, ref_note,
            softness_value=args.softness_value,
            comparison_value=args.comparison_value,
            softness_level=args.softness_level,
            softness_spec=args.softness_spec,
            breathability=args.breathability,
            antibacterial_level=args.antibacterial_level,
            wash_resistance=args.wash_resistance
        )
        prompts.append({
            "section": key,
            "name": SECTIONS[key]["name"],
            "filename_hint": f"detail_{key}.png",
            "prompt": prompt
        })

    output = {
        "meta": {
            "product": args.name,
            "reference_image": str(ref_path.resolve()),
            "sections": section_keys,
            "total": len(prompts)
        },
        "prompts": prompts
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成 {len(prompts)} 个详情页板块 prompt")
    for p in prompts:
        print(f"  [{p['section']}] {p['name']} -> {p['filename_hint']}")
    print(f"\n保存至: {out_path.resolve()}")


if __name__ == "__main__":
    main()
