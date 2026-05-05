#!/usr/bin/env python3
"""
AI Image Audit Tool — 买家秀/对镜自拍 AI 感客观检测
输出 JSON 报告，供 LLM Skill 进一步分析

Usage:
    python ai_audit_tool.py path/to/image.jpg
    python ai_audit_tool.py path/to/image.jpg --hands  # 需要 mediapipe
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image, ExifTags
import numpy as np

# 可选依赖：手部检测
MEDIAPIPE_AVAILABLE = False
mp = None
mp_hands = None
mp_drawing = None
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    pass


def analyze_exif(img: Image.Image) -> dict:
    """检查 EXIF：AI 图通常缺少相机元数据"""
    has_exif = False
    camera_info = {}
    try:
        exif = img._getexif()
        if exif:
            has_exif = True
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag in ("Make", "Model", "DateTime", "LensModel", "FNumber", "ISOSpeedRatings", "FocalLength"):
                    camera_info[tag] = str(value)
    except Exception:
        pass

    return {
        "has_exif": has_exif,
        "camera_info": camera_info,
        "suspicious": not has_exif,
        "note": "AI 生成图通常缺少 EXIF 相机元数据" if not has_exif else "包含相机 EXIF，更可能是真实照片"
    }


def analyze_noise(img_np: np.ndarray) -> dict:
    """噪点分析：AI 图高频成分通常过于均匀/平滑"""
    gray = np.mean(img_np, axis=2).astype(np.float32)

    # 拉普拉斯算子提取高频细节
    laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    from scipy.ndimage import convolve
    high_freq = convolve(gray, laplacian)

    std = float(np.std(high_freq))
    mean_abs = float(np.mean(np.abs(high_freq)))

    # 经验阈值（基于常见观察）
    # 真实手机照片通常 std > 15
    # AI 生成图通常 std < 10（过于平滑）
    if std < 8:
        assessment = "过于平滑，疑似 AI 生成"
        score = 2
    elif std < 12:
        assessment = "偏平滑，可能有轻度 AI 处理"
        score = 5
    elif std < 18:
        assessment = "噪点水平正常，接近真实手机照片"
        score = 7
    else:
        assessment = "噪点丰富，更像真实拍摄"
        score = 9

    return {
        "high_freq_std": round(std, 2),
        "high_freq_mean_abs": round(mean_abs, 2),
        "score": score,
        "assessment": assessment
    }


def analyze_histogram(img_np: np.ndarray) -> dict:
    """亮度/色彩分布分析"""
    gray = np.mean(img_np, axis=2)
    brightness_mean = float(np.mean(gray))
    brightness_std = float(np.std(gray))

    # 色彩分布
    r, g, b = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2]
    color_variance = float(np.std([np.mean(r), np.mean(g), np.mean(b)]))

    # 直方图均匀度（AI 图有时直方图过于集中）
    hist, _ = np.histogram(gray, bins=64, range=(0, 255))
    hist_uniformity = float(np.std(hist))

    # 判断是否偏暖（买家秀通常暖黄调更真实）
    warm_bias = float(np.mean(r) - np.mean(b))

    return {
        "brightness_mean": round(brightness_mean, 1),
        "brightness_std": round(brightness_std, 1),
        "color_variance": round(color_variance, 2),
        "hist_uniformity": round(hist_uniformity, 2),
        "warm_bias": round(warm_bias, 1),
        "tone_assessment": "偏暖色调，较真实" if warm_bias > 5 else "中性或偏冷"
    }


def analyze_hands(img: Image.Image) -> dict:
    """手部检测：数手指、检测异常"""
    if not MEDIAPIPE_AVAILABLE:
        return {
            "available": False,
            "note": "mediapipe 未安装，跳过手部检测。安装：pip install mediapipe"
        }

    rgb = np.array(img.convert("RGB"))
    with mp_hands.Hands(static_image_mode=True, max_num_hands=4, min_detection_confidence=0.5) as hands:
        results = hands.process(rgb)

        if not results.multi_hand_landmarks:
            return {
                "available": True,
                "hands_detected": 0,
                "fingers_per_hand": [],
                "alerts": ["未检测到手部"],
                "note": "可能手部被遮挡或未入镜"
            }

        hand_reports = []
        alerts = []

        for idx, landmarks in enumerate(results.multi_hand_landmarks):
            # 简单的手指伸展检测（基于指尖与掌根的距离）
            tips = [8, 12, 16, 20]  # 食指、中指、无名指、小指指尖
            thumb_tip = 4
            wrist = 0

            fingers_extended = 0

            # 拇指判断
            thumb_dist = np.linalg.norm(
                np.array([landmarks.landmark[thumb_tip].x, landmarks.landmark[thumb_tip].y]) -
                np.array([landmarks.landmark[wrist].x, landmarks.landmark[wrist].y])
            )
            if thumb_dist > 0.15:
                fingers_extended += 1

            # 其他四指
            for tip in tips:
                tip_dist = np.linalg.norm(
                    np.array([landmarks.landmark[tip].x, landmarks.landmark[tip].y]) -
                    np.array([landmarks.landmark[wrist].x, landmarks.landmark[wrist].y])
                )
                if tip_dist > 0.2:
                    fingers_extended += 1

            hand_reports.append({
                "hand_index": idx,
                "fingers_extended": fingers_extended,
                "landmark_count": len(landmarks.landmark)
            })

            if fingers_extended > 5:
                alerts.append(f"手部 #{idx+1} 检测到 {fingers_extended} 个伸展手指，异常")
            elif fingers_extended < 0:
                alerts.append(f"手部 #{idx+1} 手指检测异常")

        return {
            "available": True,
            "hands_detected": len(results.multi_hand_landmarks),
            "fingers_per_hand": [h["fingers_extended"] for h in hand_reports],
            "alerts": alerts if alerts else ["手指数量正常"],
            "detail": hand_reports
        }


def audit(image_path: str, check_hands: bool = False) -> dict:
    """主入口"""
    path = Path(image_path)
    if not path.exists():
        return {"error": f"文件不存在: {image_path}"}

    img = Image.open(path)
    img_np = np.array(img)

    report = {
        "file": str(path.name),
        "size": img.size,
        "mode": img.mode,
        "exif": analyze_exif(img),
        "noise": analyze_noise(img_np),
        "histogram": analyze_histogram(img_np),
    }

    if check_hands:
        report["hands"] = analyze_hands(img)

    # 综合风险提示
    risks = []
    if not report["exif"]["has_exif"]:
        risks.append("缺少 EXIF 元数据")
    if report["noise"]["score"] <= 5:
        risks.append("图像过于平滑，缺乏真实噪点")
    if check_hands and report["hands"].get("available") and report["hands"].get("alerts"):
        for alert in report["hands"]["alerts"]:
            if "异常" in alert:
                risks.append(alert)

    report["risk_summary"] = {
        "risk_level": "HIGH" if len(risks) >= 2 else "MEDIUM" if len(risks) == 1 else "LOW",
        "risks": risks if risks else ["无明显客观异常"]
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="AI 买家秀图片客观检测工具")
    parser.add_argument("image", help="图片路径")
    parser.add_argument("--hands", action="store_true", help="启用手部检测（需要 mediapipe）")
    parser.add_argument("--output", "-o", help="输出 JSON 文件路径（默认 stdout）")
    args = parser.parse_args()

    # scipy 是噪声分析必需的
    try:
        import scipy.ndimage
    except ImportError:
        print("错误：缺少 scipy。请运行: pip install scipy", file=sys.stderr)
        sys.exit(1)

    report = audit(args.image, check_hands=args.hands)

    json_str = json.dumps(report, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"报告已保存至: {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
