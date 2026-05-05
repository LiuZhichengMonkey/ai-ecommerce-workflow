#!/usr/bin/env python3
"""
淘宝主图套餐生成器 — 基于真实爆款结构重构 (v2.0)

Usage:
    python taobao_image_kit.py \
        --name "男士云朵棉睡衣套装" \
        --desc "短袖翻领，浅蓝色，白色滚边，胸前双口袋，小印花" \
        --fabric "云朵棉泡泡纱" \
        --color "浅蓝色" \
        --ref "C:/path/to/reference.jpg" \
        --ratio 1:1 \
        --slots 0-8 \
        --output taobao_prompts.json

支持 slot (基于猫人2万+销量爆款真实结构):
    0: 模特场景首图    1: 卖点模特底图    2: 主图视频脚本
    3: 面料质感特写    4: 做工细节        5: 白底图
    6: 背面/侧面       7: 透明底图(绿幕)   8: 参数图/尺码表
"""

import argparse
import json
import sys
from pathlib import Path


def build_prompt(slot: int, ratio: str, product_name: str, desc: str, fabric: str, color: str, ref_note: str) -> dict:
    """为指定 slot 构建淘宝主图 JSON prompt — 基于真实爆款结构 v2.0"""

    # 共享的"真实摄影"渲染约束
    real_photo_forbidden = [
        "文字", "牛皮癣", "拼接", "边框", "极限词",
        "3D渲染感", "插画感", "卡通感", "过于平整", "完美对称",
        "塑料质感", "蜡像感", "AI平滑感", "计算机生成感"
    ]

    base = {
        "type": "淘宝商品主图",
        "aspect_ratio": ratio,
        "platform": "taobao",
        "image_slot": slot,
        "reference_image_note": ref_note,
        "rendering": {
            "quality": "超高清真实产品摄影，未过度修图",
            "sharpness": "高",
            "color_grade": "真实色彩还原，略带自然色偏",
            "forbidden": real_photo_forbidden,
            "note": "必须呈现真实布料摄影的质感，而非数字插画"
        }
    }

    # 共享的真实面料描述
    fabric_real = (
        f"{fabric}面料，真实棉质纤维可见细微绒毛，"
        f"泡泡颗粒纹理随机分布且每个颗粒受光不同呈现自然立体感，"
        f"面料表面有细微褶皱和不平整，经纬线隐约可见，"
        f"触感暗示柔软蓬松而非僵硬平滑"
    )

    # 共享的有脸模特约束 — 宣传图要求精神饱满、亲和自然
    model_constraint = (
        "模特为亚洲男性，身形匀称，面容真实自然有亲和力，"
        "面部必须有真实皮肤质感：可见细小毛孔、轻微胡茬或青色暗影、唇纹，"
        "气色健康精神饱满，表情温和放松或略带自然微笑，"
        "像刚刚睡醒或周末居家休息的舒适状态，不可有黑眼圈、眼袋或疲惫憔悴感，"
        "必须是虚构合成人脸，不可与任何真实明星或公众人物高度相似"
    )

    if slot == 0:
        base["type"] = "淘宝主图首图"
        base["style"] = "真实电商模特场景摄影，浅灰/米色家居背景，自然松弛感，拒绝数字插画感"
        base["layout"] = {"composition": "模特居中偏左/偏右", "occupancy": "45-55%", "margin": "四周留白，上方留足空间"}
        base["scene"] = {
            "setting": "浅色简约家居场景，浅米色/浅灰色布艺沙发或床铺，背景干净无杂乱，无文字道具",
            "lighting": "柔和自然光，主光从侧前方45度角照射，形成柔和明暗过渡，阴影自然虚化",
            "mood": "放松、慵懒、自然居家状态",
            "note": "光影必须自然不均匀，不可像3D渲染般完美均匀"
        }
        base["subject"] = {
            "type": "真实模特场景展示",
            "product": product_name,
            "model": model_constraint,
            "pose": "模特自然坐在沙发上或半躺，身体放松，一手搭在沙发扶手上，姿态慵懒不做作，像在家中休息的真实状态",
            "outfit": {
                "top": f"短袖翻领睡衣上衣，{fabric_real}，{color}，白色滚边装饰领口、门襟、袖口和双口袋边缘，滚边有轻微起毛感",
                "bottom": f"配套同色长裤/短裤，{fabric_real}，裤脚白色滚边",
                "note": "服装必须自然贴合身体，有因重力产生的自然褶皱和垂坠感，不可僵硬平直"
            }
        }
        base["camera"] = {
            "angle": "平视或略低于模特视线的15度仰拍",
            "framing": "中景，模特膝盖以上入镜，展示上身穿着效果",
            "device": "Canon EOS R5 + RF 50mm f/1.2L，f/2.8，ISO 400",
            "depth_of_field": "浅景深，模特清晰，背景适度虚化",
            "quality": "DSLR 真实人像摄影，RAW 输出"
        }

    elif slot == 1:
        base["type"] = "淘宝主图卖点底图"
        base["style"] = "真实电商模特站立展示，浅色干净背景，主体突出，预留文案叠加区域"
        base["layout"] = {
            "composition": "模特全身居中",
            "occupancy": "50-60%",
            "text_overlay_area": "模特胸前至腹部区域留白，或画面左侧/右侧留白，供后期叠加卖点文字",
            "margin": "四周均匀留白，不可贴边"
        }
        base["scene"] = {
            "setting": "极浅灰色或米白色纯色背景，无道具，无纹理干扰",
            "lighting": "柔和均匀的产品摄影光，无硬阴影，模特脚下有极淡的接触阴影",
            "note": "背景必须干净，方便后期叠加文字和icon"
        }
        base["subject"] = {
            "type": "真实模特全身展示",
            "product": product_name,
            "model": model_constraint,
            "pose": "模特自然站立，身体微侧15-30度，一手自然下垂，另一手可轻触衣摆或插兜，展示全身版型和垂坠感",
            "outfit": {
                "top": f"短袖翻领睡衣上衣，{fabric_real}，{color}，白色滚边装饰，胸前口袋可见",
                "bottom": f"配套同色长裤/短裤，{fabric_real}，裤脚白色滚边，展示裤型轮廓",
                "note": "服装必须呈现真实穿着状态，有自然褶皱，不可像塑料模特般僵硬"
            }
        }
        base["camera"] = {
            "angle": "平视正前方",
            "framing": "全身入镜，头顶和脚底各留适当空间",
            "device": "Canon EOS R5 + RF 35mm f/1.4L，f/5.6，ISO 200",
            "quality": "DSLR 真实电商标准摄影"
        }
        base["post_process"] = "此为底图，生成后需用 Canva/PS 在 text_overlay_area 叠加卖点文字（如'100%纯棉 7A级抑菌'）"

    elif slot == 2:
        base["type"] = "淘宝主图视频脚本"
        base["format"] = "video_storyboard"
        base["duration"] = "15-30秒"
        base["aspect_ratio"] = ratio
        base["reference_image_note"] = ref_note
        base["storyboard"] = [
            {
                "time": "0-5秒",
                "shot_type": "中景",
                "scene": "模特全身展示",
                "action": f"模特自然站立，轻微转身15度，展示{product_name}的整体版型和垂坠感",
                "lighting": "柔和侧光，突出服装轮廓",
                "camera_move": "固定机位或极缓慢推进"
            },
            {
                "time": "5-10秒",
                "shot_type": "微距特写",
                "scene": "面料质感特写",
                "action": f"手指轻抚面料表面，展示{fabric}的真实纹理和柔软触感，泡泡颗粒清晰可见",
                "lighting": "侧光45度，突出纤维立体感和绒毛",
                "camera_move": "固定机位"
            },
            {
                "time": "10-15秒",
                "shot_type": "中景",
                "scene": "家居场景展示",
                "action": f"模特坐在沙发上放松，一手搭扶手，展示{product_name}的居家穿着状态",
                "lighting": "自然窗光，温馨氛围",
                "camera_move": "固定机位"
            },
            {
                "time": "15-20秒（可选）",
                "shot_type": "特写",
                "scene": "工艺细节展示",
                "action": "展示领口滚边、口袋边缘、纽扣细节的特写镜头",
                "lighting": "柔和顶光",
                "camera_move": "固定机位"
            }
        ]
        base["rendering"] = {
            "quality": "1080P或更高，帧率30fps",
            "color_grade": "真实自然，略偏暖色调",
            "forbidden": real_photo_forbidden,
            "note": "视频需呈现真实面料的动态质感，如垂坠、褶皱、透光效果"
        }
        base["post_process"] = "视频封面需从0-5秒关键帧截取，并叠加商品标题和卖点文字"

    elif slot == 3:
        base["type"] = "淘宝主图面料质感"
        base["style"] = "真实面料微距特写，突出柔软手感和纹理，治愈系视觉"
        base["layout"] = {"composition": "面料特写为主", "occupancy": "65%", "focus": "纤维纹理、柔软触感、泡泡颗粒"}
        base["scene"] = {
            "setting": "浅米色或浅灰色柔和背景，局部微距展示",
            "lighting": "柔和侧光45度角，突出面料纹理立体感和纤维绒毛，阴影自然过渡",
            "note": "必须能看到单根纤维和布料经纬结构，呈现'rua一下'的柔软视觉暗示"
        }
        base["subject"] = {
            "type": "真实面料微距特写",
            "product": product_name,
            "pose": f"{fabric}面料自然平铺或轻微褶皱，展示凸起泡泡颗粒纹理，手指轻按留下自然凹痕暗示柔软",
            "outfit": {
                "detail": f"{fabric_real}，泡泡颗粒必须有高低起伏的立体感而非平面压花，面料边缘有自然毛边和纤维外露，呈现'100%长绒棉'的 premium 质感"
            }
        }
        base["camera"] = {
            "angle": "45度斜俯拍，微距",
            "framing": "面料纹理局部特写",
            "device": "Canon EOS R5 + RF 100mm f/2.8L Macro",
            "depth_of_field": "浅景深，面料纹理清晰但边缘柔和过渡，背景自然虚化",
            "quality": "微距真实摄影"
        }

    elif slot == 4:
        base["type"] = "淘宝主图做工细节"
        base["style"] = "真实产品微距摄影，纯白背景，展示真实做工细节和面料质感"
        base["layout"] = {"composition": "多细节平铺", "occupancy": "50%", "items": ["经典翻领", "精致滚边", "超柔软面料", "对称裤袋/腰头", "脚口锁边"]}
        base["scene"] = {
            "setting": "纯白色背景纸，多个细节部件自然摆放",
            "lighting": "均匀顶光但保留微弱阴影，不可完全无影"
        }
        base["subject"] = {
            "type": "真实细节部件展示",
            "product": product_name,
            "pose": "领口、袖口、裤脚、腰头、口袋五个部件分别自然平铺或搭落，每个部件都有因布料重量产生的自然弯曲和褶皱",
            "outfit": {
                "detail": f"经典翻领休闲大方，精致滚边工艺简约时尚，超柔软弹力棉面料，对称裤袋工整，无痕腰头工艺，脚口双线锁边。所有细节必须呈现真实{fabric}的纤维质感而非平滑贴图"
            }
        }
        base["camera"] = {
            "angle": "正上方垂直俯拍",
            "framing": "五个细节部件均匀分布入镜",
            "device": "Canon EOS R5 + RF 100mm f/2.8L Macro",
            "quality": "超高清微距真实摄影"
        }

    elif slot == 5:
        base["type"] = "淘宝主图白底图"
        base["style"] = "真实白底产品摄影，标准电商白底，有自然接触阴影"
        base["layout"] = {"composition": "居中构图", "occupancy": "55%", "margin": "四边等距留白"}
        base["scene"] = {
            "setting": "纯白色背景纸 RGB(255,255,255)，纸张有极轻微的纹理",
            "lighting": "左右两侧柔光箱，主光略强，衣物下方有极淡的自然接触阴影，阴影边缘柔和虚化",
            "note": "必须有接触阴影让产品有落地感，不可像漂浮在空中"
        }
        base["subject"] = {
            "type": "真实产品白底图",
            "product": product_name,
            "pose": "上衣自然平铺正面，因重力产生轻微褶皱和塌陷，下摆边缘不完全平直；长裤平铺于下方，裤腿有自然弯曲，整体呈标准T字形但有真实布料的柔软感",
            "outfit": {
                "top": f"短袖翻领睡衣上衣，{fabric_real}，{color}，白色滚边有轻微毛边",
                "bottom": f"配套同色长裤，{fabric_real}，裤脚白色滚边"
            }
        }
        base["camera"] = {
            "angle": "正上方垂直俯拍",
            "framing": "完整产品居中，四边留白均匀",
            "device": "Canon EOS R5 + RF 50mm f/1.2L，f/8",
            "quality": "DSLR 真实电商标准摄影"
        }
        base["rendering"]["forbidden"] = real_photo_forbidden + ["倒影", "道具", "背景渐变"]

    elif slot == 6:
        base["type"] = "淘宝主图背面侧面"
        base["style"] = "真实电商产品摄影，纯白背景，展示背面版型和侧面轮廓"
        base["layout"] = {"composition": "左右分开展示", "occupancy": "60%", "left": "上衣背面自然平铺", "right": "长裤侧面自然摆放"}
        base["scene"] = {
            "setting": "纯白色背景纸，无道具",
            "lighting": "左右两侧柔光箱，自然接触阴影"
        }
        base["subject"] = {
            "type": "真实背面与侧面展示",
            "product": product_name,
            "pose": "左侧：上衣翻至背面自然平铺，展示后领滚边和背片剪裁，布料有自然褶皱；右侧：长裤侧放，展示裤型轮廓和裤脚滚边",
            "outfit": {
                "top": f"短袖翻领睡衣上衣背面，{fabric_real}，{color}，后领白色滚边",
                "bottom": f"长裤侧面展示，{fabric_real}，{color}，裤脚白色滚边"
            }
        }
        base["camera"] = {
            "angle": "正上方垂直俯拍",
            "framing": "背面与侧面完整入镜",
            "device": "Canon EOS R5 + RF 50mm f/1.2L",
            "quality": "DSLR 真实电商标准摄影"
        }
        base["rendering"]["forbidden"] = real_photo_forbidden + ["倒影", "道具"]

    elif slot == 7:
        base["type"] = "淘宝主图透明底图"
        base["style"] = "真实产品透明底图源图，纯色绿幕背景"
        base["layout"] = {"composition": "居中构图", "occupancy": "55%", "margin": "四周 generous padding"}
        base["scene"] = {
            "setting": "纯绿色背景 #00ff00，无任何阴影、渐变、纹理",
            "lighting": "均匀产品摄影光，左右对称柔光",
            "note": "背景必须是单一均匀颜色，不可有光影变化"
        }
        base["subject"] = {
            "type": "真实产品抠图源图",
            "product": product_name,
            "pose": "上衣自然平铺正面，长裤平铺于下方，整体呈T字形，产品与背景之间有明显分离",
            "outfit": {
                "top": f"短袖翻领睡衣上衣，{fabric_real}，{color}，白色滚边",
                "bottom": f"配套同色长裤，{fabric_real}，裤脚白色滚边",
                "constraint": "产品中不可出现 #00ff00 绿色"
            }
        }
        base["camera"] = {
            "angle": "正上方垂直俯拍",
            "framing": "完整产品居中，四周留足绿边",
            "device": "Canon EOS R5 + RF 50mm f/1.2L",
            "quality": "DSLR 真实电商标准摄影"
        }
        base["rendering"] = {
            "quality": "超高清",
            "sharpness": "高",
            "color_grade": "真实色彩还原",
            "forbidden": real_photo_forbidden + ["文字", "牛皮癣", "拼接", "边框", "极限词", "阴影", "倒影", "道具", "模特", "背景渐变", "地板", "环境光变化"],
            "post_process": "生成后需运行 remove_chroma_key.py 去除绿色背景，输出透明PNG"
        }

    elif slot == 8:
        base["type"] = "淘宝详情页参数图"
        base["style"] = "电商参数说明图， clean infographic，白底，清晰排版"
        base["layout"] = {
            "composition": "上下分区",
            "top": "尺码表表格区域",
            "bottom": "面料成分与洗护说明",
            "occupancy": "80%"
        }
        base["scene"] = {
            "setting": "纯白色背景 RGB(255,255,255)，极简电商信息图风格",
            "lighting": "均匀",
            "note": "此为信息图，需保证文字区域清晰可读"
        }
        base["subject"] = {
            "type": "产品参数信息图",
            "product": product_name,
            "size_chart": {
                "columns": ["尺码", "身高(cm)", "体重(kg)", "衣长", "胸围", "袖长", "裤长"],
                "rows": ["M: 165/88A", "L: 170/92A", "XL: 175/96A", "XXL: 180/100A"]
            },
            "fabric_info": f"面料：{fabric} | 成分：棉100% | 执行标准：GB/T 22844-2009 | 安全类别：GB 18401 B类",
            "care_labels": ["水洗30度", "不可漂白", "悬挂晾干", "低温熨烫", "不可干洗"]
        }
        base["typography"] = {
            "title": "产品参数 / SIZE CHART",
            "font": "简洁无衬线字体",
            "color": "深灰或黑色",
            "table_style": "细线表格，清晰行列分隔"
        }
        base["rendering"] = {
            "quality": "超高清",
            "sharpness": "高",
            "forbidden": ["花哨装饰", "多余配色", "模糊文字"],
            "note": "表格和文字必须清晰，方便消费者对照选购"
        }

    else:
        raise ValueError(f"未知 slot: {slot}，有效范围为 0-8")

    return base


def parse_slots(slots_str: str) -> list:
    """解析 slot 参数，如 '0-5', '0,2,4', 'all'"""
    if not slots_str or not slots_str.strip():
        raise ValueError("slots 参数不能为空")

    if slots_str.lower() == "all":
        return list(range(0, 9))

    slots = set()
    for part in slots_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            start, end = int(start), int(end)
            if start > end:
                start, end = end, start
            if start < 0 or end > 8:
                raise ValueError(f"slot 范围必须在 0-8 之间，收到: {start}-{end}")
            slots.update(range(start, end + 1))
        else:
            slot = int(part)
            if slot < 0 or slot > 8:
                raise ValueError(f"slot 必须在 0-8 之间，收到: {slot}")
            slots.add(slot)
    if not slots:
        raise ValueError(f"无法解析任何有效 slot: {slots_str}")
    return sorted(slots)


def generate_package(product_name: str, desc: str, fabric: str, color: str,
                     ref_path: str, ratio: str, slots: list) -> list:
    """生成指定 slot 的 prompt 列表"""
    ref_note = f"参考图中为{product_name}：{desc}。生成时必须保持同款版型、面料质感和滚边细节"

    prompts = []
    for slot in slots:
        prompt = build_prompt(slot, ratio, product_name, desc, fabric, color, ref_note)
        ratio_str = ratio.replace(":", "x")
        if slot == 2:
            filename = f"taobao_slot{slot}_{ratio_str}_storyboard.json"
        elif slot <= 7:
            filename = f"taobao_slot{slot}_{ratio_str}.png"
        else:
            filename = f"taobao_detail_param_{ratio_str}.png"

        slot_names = {
            0: "模特场景首图", 1: "卖点模特底图", 2: "主图视频脚本",
            3: "面料质感特写", 4: "做工细节", 5: "白底图",
            6: "背面/侧面", 7: "透明底图(绿幕)", 8: "参数图/尺码表"
        }

        prompts.append({
            "slot": slot,
            "name": slot_names.get(slot, f"slot{slot}"),
            "filename_hint": filename,
            "prompt": prompt
        })

    return prompts


def main():
    parser = argparse.ArgumentParser(description="淘宝主图套餐生成器 v2.0")
    parser.add_argument("--name", required=True, help="商品名称")
    parser.add_argument("--desc", required=True, help="商品描述")
    parser.add_argument("--fabric", required=True, help="面料名称")
    parser.add_argument("--color", required=True, help="颜色")
    parser.add_argument("--ref", required=True, help="参考图路径")
    parser.add_argument("--ratio", default="1:1", choices=["1:1", "3:4"], help="主图比例")
    parser.add_argument("--slots", default="0-5", help="生成哪些 slot，如 0-5, 0,2,4, all")
    parser.add_argument("--output", default="taobao_prompts.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    ref_path = Path(args.ref)
    if not ref_path.exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)

    try:
        slots = parse_slots(args.slots)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    package = generate_package(
        product_name=args.name,
        desc=args.desc,
        fabric=args.fabric,
        color=args.color,
        ref_path=args.ref,
        ratio=args.ratio,
        slots=slots
    )

    output = {
        "meta": {
            "product": args.name,
            "ratio": args.ratio,
            "reference_image": str(ref_path.resolve()),
            "slots": slots,
            "notes": "Slot 0=模特场景首图, Slot 1=卖点模特底图(需后期加字), Slot 2=视频脚本, Slot 5=白底图, Slot 7=绿幕透明底"
        },
        "prompts": package
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成 {args.ratio} 主图套餐，保存至: {out_path.resolve()}")
    names = [p['name'] for p in package]
    print(f"共 {len(package)} 项: {' / '.join(names)}")

    if 1 in slots:
        print("\n[提示] Slot 1 为卖点模特底图，生成后请用 Canva/PS 在预留区域叠加卖点文字")
    if 2 in slots:
        print("\n[提示] Slot 2 为视频分镜脚本，请按 storyboard 逐帧生成或使用视频工具制作")
    if 7 in slots:
        print("\n[提示] Slot 7 为绿幕透明底图，生成后请运行以下命令去除背景:")
        codex_home = Path.home() / ".codex"
        print(f'  python "{codex_home}/skills/.system/imagegen/scripts/remove_chroma_key.py" \\')
        print(f'    --input <生成的绿幕图.png> --out <透明底图.png> \\')
        print(f'    --auto-key border --soft-matte --despill')


if __name__ == "__main__":
    main()
