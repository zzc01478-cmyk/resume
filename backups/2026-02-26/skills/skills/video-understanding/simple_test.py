#!/usr/bin/env python3
"""
最简单的直接测试 - 完全使用用户提供的原始信息
"""

import json
import requests

print("="*50)
print("最简单直接测试 - 使用原始信息")
print("="*50)

# 用户提供的原始信息
API_KEY = "sk-592vE7E0F2h1f0I5D2X1H7e0C0C8I5B1B2A1C0D2F4I5lIJxps"
BASE_URL = "https://api.linkapi.ai/v1"
MODEL = "gemini-3-flash-preview"

print(f"🔗 URL: {BASE_URL}")
print(f"🔑 Key: {API_KEY[:10]}...{API_KEY[-10:]}")
print(f"🤖 模型: {MODEL}")

# 最简单的 OpenAI 格式请求
url = f"{BASE_URL}/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 10
}

print(f"\n📤 发送请求到: {url}")
print(f"📦 请求数据: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"\n📥 响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 成功！")
        print(f"💬 回复: {result}")
    else:
        print(f"❌ 失败")
        print(f"📄 响应内容: {response.text}")
        
except Exception as e:
    print(f"\n❌ 请求异常: {e}")

print("\n" + "="*50)
print("测试完成")
print("="*50)