#!/usr/bin/env python3
"""
快速测试视频分析
"""

import json
import requests
from pathlib import Path

print("="*50)
print("快速视频分析测试")
print("="*50)

# 加载配置
workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    gemini_config = config.get("gemini", {})
    api_key = gemini_config.get("api_key")
    model = gemini_config.get("model", "gemini-3-flash-preview")
    base_url = gemini_config.get("base_url", "https://api.linkapi.ai/v1")
    
    print(f"✅ 配置加载成功")
    print(f"🤖 模型: {model}")
    print(f"🔗 端点: {base_url}")
    
    # 测试视频分析
    print("\n🔍 测试视频分析功能")
    
    video_url = "https://example.com/sample-video.mp4"
    prompt = """请分析这个视频内容，包括：
1. 视频的主要内容和主题
2. 关键场景和视觉元素  
3. 音频信息（如果有）
4. 情感氛围和风格
5. 潜在用途和适用场景

视频URL: https://example.com/sample-video.mp4

请用中文输出详细的分析报告。"""
    
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    print(f"📤 发送视频分析请求...")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 视频分析请求成功！")
            
            if "choices" in result and len(result["choices"]) > 0:
                analysis = result["choices"][0]["message"]["content"]
                print(f"\n📄 分析结果:")
                print("-" * 50)
                print(analysis[:1000])
                if len(analysis) > 1000:
                    print("... (完整分析已截断)")
                print("-" * 50)
            else:
                print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ 请求失败: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "="*50)
print("测试完成")
print("="*50)