#!/usr/bin/env python3
"""
测试 Gemini 配置
"""

import json
import os
import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("Gemini 配置测试")
print("="*50)

if not config_path.exists():
    print(f"❌ 配置文件不存在: {config_path}")
    print("请先创建配置文件并设置 API key")
    sys.exit(1)

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    gemini_config = config.get("gemini", {})
    
    print(f"✅ 配置文件加载成功")
    print(f"📁 配置文件路径: {config_path}")
    print(f"🤖 模型: {gemini_config.get('model', '未设置')}")
    print(f"🔑 API Key 已设置: {'是' if gemini_config.get('api_key') else '否'}")
    print(f"🎥 视频理解启用: {gemini_config.get('video_understanding_enabled', False)}")
    
    if gemini_config.get('api_key'):
        # 检查 API key 格式
        api_key = gemini_config['api_key']
        if len(api_key) > 10:
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
            print(f"🔐 API Key (部分显示): {masked_key}")
        else:
            print("⚠️  API Key 格式可能不正确")
    else:
        print("❌ 请设置 Gemini API key")
        
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)

print("="*50)
print("测试完成")
print("="*50)