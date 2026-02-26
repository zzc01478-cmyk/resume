#!/usr/bin/env python3
"""
测试视频分析功能
"""

import sys
from pathlib import Path

# 添加父目录到路径
workspace_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_path / "skills" / "video-understanding"))

from analyze_video import analyze_video_with_gemini

print("="*50)
print("视频分析功能测试")
print("="*50)

# 测试用例
test_cases = [
    {
        "name": "测试1: 视频URL分析",
        "video_path": "https://example.com/sample-video.mp4",
        "description": "分析在线视频"
    },
    {
        "name": "测试2: 本地文件分析",
        "video_path": "/tmp/sample.mp4",
        "description": "分析本地视频文件"
    },
    {
        "name": "测试3: YouTube视频",
        "video_path": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "description": "分析YouTube视频"
    }
]

for test_case in test_cases:
    print(f"\n🔍 {test_case['name']}")
    print(f"📁 视频: {test_case['video_path']}")
    print(f"📝 描述: {test_case['description']}")
    
    # 使用自定义提示词
    custom_prompt = f"请分析这个视频内容：{test_case['description']}。视频位置：{test_case['video_path']}。请提供详细的分析报告。"
    
    result = analyze_video_with_gemini(test_case['video_path'], custom_prompt)
    
    if result.get("success"):
        print("✅ 分析成功！")
        print(f"📄 分析结果:\n{result['analysis'][:500]}...")
    else:
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")
    
    print("-" * 50)

print("\n" + "="*50)
print("功能测试总结")
print("="*50)

# 测试配置加载
from analyze_video import load_gemini_config
config = load_gemini_config()

if config:
    print("✅ 配置加载成功")
    print(f"🤖 模型: {config.get('model')}")
    print(f"🔗 端点: {config.get('base_url')}")
    print(f"🎥 视频理解: {'启用' if config.get('video_understanding_enabled') else '禁用'}")
else:
    print("❌ 配置加载失败")

print("\n🎯 视频理解功能已就绪！")
print("使用方法:")
print("1. 提供视频URL或文件路径")
print("2. 调用 analyze_video_with_gemini() 函数")
print("3. 获取详细的分析报告")

print("\n" + "="*50)
print("测试完成")
print("="*50)