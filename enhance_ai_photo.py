#!/usr/bin/env python3
"""
AI 生成图后期增强脚本
针对第三版男士睡衣买家秀的快速提分处理
"""

import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np


def add_real_noise(arr: np.ndarray, intensity: float = 30, salt_pepper: float = 0.015):
    """添加真实传感器级噪点：高斯 + 椒盐"""
    result = arr.astype(np.float32)

    # 高斯噪声
    gauss = np.random.normal(0, intensity, result.shape)
    result += gauss

    # 椒盐噪声（模拟传感器坏点）
    salt_mask = np.random.random(result.shape[:2]) < salt_pepper
    pepper_mask = np.random.random(result.shape[:2]) < salt_pepper

    result[salt_mask] = np.clip(result[salt_mask] + 60, 0, 255)
    result[pepper_mask] = np.clip(result[pepper_mask] - 60, 0, 255)

    return np.clip(result, 0, 255).astype(np.uint8)


def adjust_warmth(arr: np.ndarray, warmth_offset: float = -25):
    """调整色温：负值降低暖度（减少红/黄，增加蓝/绿）"""
    result = arr.astype(np.float32)

    # 降低红色通道
    result[:, :, 0] = np.clip(result[:, :, 0] + warmth_offset, 0, 255)
    # 降低绿色通道（轻微）
    result[:, :, 1] = np.clip(result[:, :, 1] + warmth_offset * 0.3, 0, 255)
    # 增加蓝色通道
    result[:, :, 2] = np.clip(result[:, :, 2] - warmth_offset * 0.8, 0, 255)

    return result.astype(np.uint8)


def add_vignette(img: Image.Image, strength: float = 0.25):
    """添加轻微暗角（模拟手机镜头边缘失光）"""
    width, height = img.size

    # 创建径向渐变遮罩
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    # 中心亮、边缘暗
    mask = 1 - (R * strength)
    mask = np.clip(mask, 0.6, 1.0)  # 不要太极端

    arr = np.array(img).astype(np.float32)
    for c in range(3):
        arr[:, :, c] *= mask

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def enhance_ai_photo(input_path: str, output_path: str):
    """主处理流程"""
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)

    print(f"原始尺寸: {img.size}")
    print(f"原始亮度均值: {np.mean(arr):.1f}")

    # Step 1: 降低色温（AI 过暖了，向真实照片的 neutral-warm 靠拢）
    arr = adjust_warmth(arr, warmth_offset=-20)
    print("[1/4] 色温校正完成: -20 暖度偏移")

    # Step 2: 轻微提升对比度（AI 图通常偏灰）
    img_temp = Image.fromarray(arr)
    enhancer = ImageEnhance.Contrast(img_temp)
    img_temp = enhancer.enhance(1.15)  # 提升 15% 对比度
    arr = np.array(img_temp)
    print("[2/4] 对比度提升完成: +15%")

    # Step 3: 添加真实噪点（温和版）
    arr = add_real_noise(arr, intensity=15, salt_pepper=0.008)
    print("[3/4] 真实噪点叠加完成: intensity=15")

    # Step 4: 轻微暗角（温和版）
    img_result = Image.fromarray(arr)
    img_result = add_vignette(img_result, strength=0.12)
    print("[4/4] 暗角添加完成: strength=0.12")

    # 保存
    img_result.save(output_path, quality=92)
    print(f"\n保存成功: {output_path}")

    # 验证
    result_arr = np.array(img_result)
    print(f"处理后亮度均值: {np.mean(result_arr):.1f}")
    print(f"处理后 red-blue 偏差: {np.mean(result_arr[:,:,0]) - np.mean(result_arr[:,:,2]):.1f} (越低越不偏暖)")


def main():
    if len(sys.argv) < 3:
        # 默认处理第三版图片
        default_input = str(Path.home() / ".codex" / "generated_images" / "019de454-28fb-79b3-9b81-eff98d21aa50" / "ig_0ae42ada7ed2a1000169f4d216decc819988b2ca619a623be8.png")
        default_output = str(Path.home() / "Desktop" / "AI_第三版_增强后.jpg")

        if not Path(default_input).exists():
            print(f"错误: 找不到默认输入文件: {default_input}")
            print("用法: python enhance_ai_photo.py <input.png> <output.jpg>")
            sys.exit(1)

        enhance_ai_photo(default_input, default_output)
    else:
        enhance_ai_photo(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
