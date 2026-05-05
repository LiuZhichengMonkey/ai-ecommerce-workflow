# AI 电商工作流 (AI E-commerce Workflow)

基于 GPT Image 2 + Codex CLI 的电商视觉与文案自动化生成工作流。

## 功能概览

| 模块 | 工具 | 说明 |
|:---|:---|:---|
| **淘宝主图** | `taobao_image_kit.py` | 生成9张主图套餐（模特/视频脚本/面料/白底/透明底等） |
| **淘宝详情页** | `taobao_detail_kit.py` | 生成10屏详情页长图prompt（海报/情感/尺码/数据/信任等） |
| **淘宝SKU** | `taobao_sku_gen.py` | 多色SKU图批量生成 |
| **小红书封面** | `xiaohongshu_cover_gen.py` | 4种风格封面（magazine/bold/collage/cozy） |
| **图片检测** | `ai_audit_tool.py` | 噪点/色温/EXIF/手部检测 |
| **图片增强** | `enhance_ai_photo.py` | AI图后期处理（噪点/色温/暗角） |
| **文案生成** | `copywriting_gen.py` | 小红书/淘宝文案自动生成 |
| **文案Review** | `copywriting_review.py` | 5维度评分+AI感标注 |
| **文案迭代** | `copywriting_iterate.py` | 自动三轮迭代直到达标 |
| **蓝图Skill** | `skills/gpt-image-2-blueprint/` | JSON结构化prompt生成 |
| **评分Skill** | `skills/image-audit/` | 图片主观评分+修复建议 |

## 快速开始

### 1. 安装依赖

```bash
pip install pillow numpy scipy mediapipe
```

### 2. 配置 Codex CLI 路径

修改 `generate_image.py` 中的 `codex_path` 为你的实际安装路径，通常在：
```
C:/Users/<用户名>/AppData/Roaming/npm/codex.cmd
```

### 3. 生成淘宝主图

```bash
python taobao_image_kit.py \
  --name "男士云朵棉睡衣套装" \
  --desc "短袖翻领，浅蓝色，白色滚边，胸前双口袋" \
  --fabric "云朵棉泡泡纱" \
  --color "浅蓝色" \
  --ref "C:/path/to/reference.jpg" \
  --ratio 1:1 \
  --slots 0-5
```

### 4. 生成文案（含自动Review迭代）

```bash
python copywriting_iterate.py \
  --product "男士云朵棉睡衣套装" \
  --fabric "云朵棉泡泡纱" \
  --color "浅蓝色" \
  --features "短袖翻领,白色滚边,胸前双口袋,柔软蓬松" \
  --platform xiaohongshu \
  --type long \
  --max-rounds 5 \
  --output final_copy.json
```

## 文档

完整标准作业流程见 [`AI_买家秀生成SOP.md`](./AI_买家秀生成SOP.md)。

## 项目结构

```
.
├── taobao_image_kit.py          # 淘宝主图生成器
├── taobao_detail_kit.py         # 淘宝详情页生成器
├── taobao_sku_gen.py            # SKU多色图生成器
├── xiaohongshu_cover_gen.py     # 小红书封面生成器
├── generate_image.py            # 图片生成包装器
├── ai_audit_tool.py             # 客观检测工具
├── enhance_ai_photo.py          # 图片后期增强
├── copywriting_gen.py           # 文案生成器
├── copywriting_review.py        # Review Agent
├── copywriting_iterate.py       # 迭代优化脚本
├── templates/                   # 文案框架模板
│   ├── xiaohongshu_copy.md
│   ├── taobao_copy.md
│   └── anti_ai_constraints.md
├── skills/                      # Claude Skill
│   ├── gpt-image-2-blueprint/
│   └── image-audit/
├── output/                      # 生成结果（按品类分组）
└── AI_买家秀生成SOP.md          # 完整SOP文档
```

## 注意事项

- 生成的图片默认保存在 `~/.codex/generated_images/`，可通过 `--output` 指定路径
- 文案生成依赖 Codex CLI 的 text generation 能力
- 图片文件（.png/.jpg）已通过 `.gitignore` 排除，仅保留代码和文档

## 版本

v1.2 — 2026-05-04
