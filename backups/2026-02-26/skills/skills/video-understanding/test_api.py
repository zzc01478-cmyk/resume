#!/usr/bin/env python3
"""
测试 Gemini API 连接
"""

import json
import requests
import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("Gemini API 连接测试")
print("="*50)

# 加载配置
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    gemini_config = config.get("gemini", {})
    api_key = gemini_config.get("api_key")
    model = gemini_config.get("model", "gemini-3-flash-preview")
    base_url = gemini_config.get("base_url", "https://api.linkapi.ai/v1")
    
    if not api_key:
        print("❌ API key 未设置")
        sys.exit(1)
    
    print(f"🔗 API 端点: {base_url}")
    print(f"🤖 模型: {model}")
    
    # 测试简单的文本请求
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    test_data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "你好！请回复'API连接成功'来确认连接正常。"
            }
        ],
        "max_tokens": 50
    }
    
    print("🔄 发送测试请求...")
    
    try:
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 连接成功！")
            
            if "choices" in result and len(result["choices"]) > 0:
                reply = result["choices"][0]["message"]["content"]
                print(f"💬 模型回复: {reply}")
            else:
                print("⚠️  响应格式异常")
                print(f"📄 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
        elif response.status_code == 401:
            print("❌ 认证失败 - API key 可能无效")
            print(f"📄 错误信息: {response.text}")
        elif response.status_code == 404:
            print("❌ 端点不存在 - 请检查 API URL")
            print(f"📄 错误信息: {response.text}")
        else:
            print(f"❌ 请求失败 - 状态码: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 - 网络连接或API响应缓慢")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 无法连接到API服务器")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        
except FileNotFoundError:
    print(f"❌ 配置文件不存在: {config_path}")
except json.JSONDecodeError:
    print(f"❌ 配置文件格式错误")
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("="*50)
print("测试完成")
print("="*50)