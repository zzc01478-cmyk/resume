#!/bin/bash
# 设置高德地图API密钥环境变量
export AMAP_API_KEY="3cc2c28498d55a83f16667a4681b8340"
echo "✅ AMAP_API_KEY环境变量已设置"

# 如果需要，可以直接运行工具测试
echo "测试搜索功能..."
python amap_tool.py search --keywords "咖啡店" --city "上海" 2>/dev/null | head -5

echo ""
echo "使用方法："
echo "1. 先设置环境变量: source set_env.sh"
echo "2. 运行工具: python amap_tool.py search --keywords \"关键词\" --city \"城市\""
echo "3. 或运行路由规划: python amap_tool.py route --origin \"起点\" --destination \"终点\" --mode driving --city \"城市\""