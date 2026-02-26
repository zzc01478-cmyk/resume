#!/usr/bin/env python3
"""
测试新 API key
"""

import json
import requests

print("="*50)
print("测试新 API key")
print("="*50)

# 新 API key
NEW_API_KEY = "sk-592AXfbbIUo2g28D0PKydpEcxdQEZVF40Sg2MqJN6OlIJxps"
BASE_URL = "https://api.linkapi.ai/v1"
MODEL = "gemini-3-flash-preview"

print(f"🔗 URL: {BASE_URL}")
print(f"🔑 新 Key: {NEW_API_KEY[:10]}...{NEW_API_KEY[-10:]}")
print(f"🤖 模型: {MODEL}")

# 测试1: 标准 OpenAI 格式
print("\n🔍 测试1: 标准 OpenAI 格式")
url = f"{BASE_URL}/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {NEW_API_KEY}"
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "请说'API测试成功'来确认连接正常。"}
    ],
    "max_tokens": 20
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=15)
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 成功！")
        
        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            print(f"💬 回复: {reply}")
        else:
            print(f"📄 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 失败: {response.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")

# 测试2: 尝试不同的端点
print("\n🔍 测试2: 尝试 /completions 端点")
completion_url = f"{BASE_URL}/completions"

completion_data = {
    "model": MODEL,
    "prompt": "Say 'test passed':",
    "max_tokens": 10
}

try:
    response = requests.post(completion_url, headers=headers, json=completion_data, timeout=15)
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 成功！")
        print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"📄 响应: {response.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")

print("\n" + "="*50)
print("测试完成")
print("="*50)