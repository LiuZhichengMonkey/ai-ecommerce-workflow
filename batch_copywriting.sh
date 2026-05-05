#!/bin/bash
set -e

PYTHON="/c/Users/zhicheng.liu/AppData/Roaming/uv/python/cpython-3.14.3-windows-x86_64-none/python.exe"
ITERATE="$HOME/copywriting_iterate.py"

# 商品1: 男士云朵棉睡衣
echo "========== 商品1: 男士云朵棉睡衣 =========="

$PYTHON $ITERATE --product "男士云朵棉睡衣套装" --fabric "云朵棉泡泡纱" --color "浅蓝色" --features "短袖翻领,白色滚边,胸前双口袋,柔软蓬松" --platform xiaohongshu --type short --max-rounds 5 --output "$HOME/output/男士云朵棉睡衣/xiaohongshu_short.json"
echo "[1/11] 男士睡衣 xiaohongshu short done"

$PYTHON $ITERATE --product "男士云朵棉睡衣套装" --fabric "云朵棉泡泡纱" --color "浅蓝色" --features "短袖翻领,白色滚边,胸前双口袋,柔软蓬松" --platform taobao --type long --max-rounds 5 --output "$HOME/output/男士云朵棉睡衣/taobao_long.json"
echo "[2/11] 男士睡衣 taobao long done"

$PYTHON $ITERATE --product "男士云朵棉睡衣套装" --fabric "云朵棉泡泡纱" --color "浅蓝色" --features "短袖翻领,白色滚边,胸前双口袋,柔软蓬松" --platform taobao --type short --max-rounds 5 --output "$HOME/output/男士云朵棉睡衣/taobao_short.json"
echo "[3/11] 男士睡衣 taobao short done"

# 商品2: 女士甜美风家居服
echo "========== 商品2: 女士甜美风家居服 =========="

$PYTHON $ITERATE --product "女士甜美风家居服套装" --fabric "紧赛精梳棉" --color "粉色" --features "圆领短袖T恤,七分裤,心形印花,甜美可爱" --platform xiaohongshu --type long --max-rounds 5 --output "$HOME/output/女士甜美风家居服/xiaohongshu_long.json"
echo "[4/11] 女士家居服 xiaohongshu long done"

$PYTHON $ITERATE --product "女士甜美风家居服套装" --fabric "紧赛精梳棉" --color "粉色" --features "圆领短袖T恤,七分裤,心形印花,甜美可爱" --platform xiaohongshu --type short --max-rounds 5 --output "$HOME/output/女士甜美风家居服/xiaohongshu_short.json"
echo "[5/11] 女士家居服 xiaohongshu short done"

$PYTHON $ITERATE --product "女士甜美风家居服套装" --fabric "紧赛精梳棉" --color "粉色" --features "圆领短袖T恤,七分裤,心形印花,甜美可爱" --platform taobao --type long --max-rounds 5 --output "$HOME/output/女士甜美风家居服/taobao_long.json"
echo "[6/11] 女士家居服 taobao long done"

$PYTHON $ITERATE --product "女士甜美风家居服套装" --fabric "紧赛精梳棉" --color "粉色" --features "圆领短袖T恤,七分裤,心形印花,甜美可爱" --platform taobao --type short --max-rounds 5 --output "$HOME/output/女士甜美风家居服/taobao_short.json"
echo "[7/11] 女士家居服 taobao short done"

# 商品3: 娇得巧29.04款
echo "========== 商品3: 娇得巧29.04款 =========="

$PYTHON $ITERATE --product "娇得巧29.04款女士家居服" --fabric "紧赛精梳棉" --color "豆红/蓝/绿/粉" --features "圆领短袖T恤,七分裤,心形印花,多色可选" --platform xiaohongshu --type long --max-rounds 5 --output "$HOME/output/娇得巧29.04款/xiaohongshu_long.json"
echo "[8/11] 娇得巧 xiaohongshu long done"

$PYTHON $ITERATE --product "娇得巧29.04款女士家居服" --fabric "紧赛精梳棉" --color "豆红/蓝/绿/粉" --features "圆领短袖T恤,七分裤,心形印花,多色可选" --platform xiaohongshu --type short --max-rounds 5 --output "$HOME/output/娇得巧29.04款/xiaohongshu_short.json"
echo "[9/11] 娇得巧 xiaohongshu short done"

$PYTHON $ITERATE --product "娇得巧29.04款女士家居服" --fabric "紧赛精梳棉" --color "豆红/蓝/绿/粉" --features "圆领短袖T恤,七分裤,心形印花,多色可选" --platform taobao --type long --max-rounds 5 --output "$HOME/output/娇得巧29.04款/taobao_long.json"
echo "[10/11] 娇得巧 taobao long done"

$PYTHON $ITERATE --product "娇得巧29.04款女士家居服" --fabric "紧赛精梳棉" --color "豆红/蓝/绿/粉" --features "圆领短袖T恤,七分裤,心形印花,多色可选" --platform taobao --type short --max-rounds 5 --output "$HOME/output/娇得巧29.04款/taobao_short.json"
echo "[11/11] 娇得巧 taobao short done"

echo "========== 全部完成 =========="
