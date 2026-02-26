#!/usr/bin/env python3
"""
测试正确的请求格式
"""

import json
import requests

print("="*50)
print("测试正确的请求格式")
print("="*50)

API_KEY = "sk-592AXfbbIUo2g28D0PKydpEcxdQEZVF40Sg2MqJN6OlIJxps"
BASE_URL = "https://api.linkapi.ai/v1"
MODEL = "gemini-3-flash-preview"

print(f"🔗 URL: {BASE_URL}")
print(f"🔑 Key: {API_KEY[:10]}...{API_KEY[-10:]}")
print(f"🤖 模型: {MODEL}")

# 尝试不同的请求格式
formats = [
    {
        "name": "OpenAI 标准格式",
        "url": f"{BASE_URL}/chat/completions",
        "data": {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "请用中文回复'连接测试成功'。"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
    },
    {
        "name": "简单格式",
        "url": f"{BASE_URL}/chat/completions",
        "data": {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "Hello, say 'test passed' in Chinese."}
            ]
        }
    },
    {
        "name": "Gemini 可能格式",
        "url": f"{BASE_URL}/chat/completions",
        "data": {
            "model": MODEL,
            "contents": [
                {
                    "parts": [
                        {"text": "请说'测试成功'"}
                    ]
                }
            ]
        }
    }
]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

for fmt in formats:
    print(f"\n🔍 测试格式: {fmt['name']}")
    print(f"📤 请求数据: {json.dumps(fmt['data'], indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(fmt['url'], headers=headers, json=fmt['data'], timeout=15)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 成功！")
            
            # 尝试不同的响应格式
            if "choices" in result and len(result["choices"]) > 0:
                if "message" in result["choices"][0]:
                    reply = result["choices"][0]["message"]["content"]
                    print(f"💬 回复: {reply}")
                elif "text" in result["choices"][0]:
                    reply = result["choices"][0]["text"]
                    print(f"💬 回复: {reply}")
            elif "candidates" in result and len(result["candidates"]) > 0:
                if "content" in result["candidates"][0]:
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"💬 回复: {reply}")
            else:
                print(f"📄 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                
        elif response.status_code == 400:
            print(f"❌ 请求格式错误: {response.text[:200]}...")
        else:
            print(f"📄 响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

# 测试视频分析提示词
print("\n🔍 测试视频分析提示词")
video_test_data = {
    "model": MODEL,
    "messages": [
        {
            "role": "user", 
            "content": "请分析这个视频内容，包括：\n1. 视频的主要内容和主题\n2. 关键场景和视觉元素\n3. 音频信息（如果有）\n4. 情感氛围和风格\n5. 潜在用途和适用场景\n\n请用中文输出详细的分析报告。"
        }
    ],
    "max_tokens": 500
}

try:
    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=video_test_data, timeout=20)
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 视频分析提示词测试成功！")
        
        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            print(f"💬 模型回复: {reply[:200]}...")
        else:
            print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}...")
    else:
        print(f"📄 响应: {response.text[:200]}...")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")

print("\n" + "="*50)
print("测试完成")
print("="*50)