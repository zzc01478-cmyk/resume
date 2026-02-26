#!/usr/bin/env python3
"""
测试 Gemini 原生 API 格式
"""

import json
import requests
import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("测试 Gemini 原生 API 格式")
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
    
    # 尝试 Gemini 原生格式
    # 格式1: Google AI Studio 格式
    print("\n🔍 尝试格式1: Google AI Studio 格式")
    
    # 移除可能的 /v1 后缀，因为中转站可能已经包含了
    if base_url.endswith('/v1'):
        api_base = base_url
    else:
        api_base = f"{base_url}/v1"
    
    url = f"{api_base}/models/{model}:generateContent"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 尝试两种认证方式
    auth_options = [
        {"name": "Query Parameter", "url": f"{url}?key={api_key}"},
        {"name": "Bearer Header", "url": url, "headers": {"Authorization": f"Bearer {api_key}"}},
        {"name": "X-Goog-Api-Key", "url": url, "headers": {"X-Goog-Api-Key": api_key}},
    ]
    
    test_data = {
        "contents": [{
            "parts": [{
                "text": "Hello! Please respond with 'API test successful'."
            }]
        }]
    }
    
    for auth_option in auth_options:
        print(f"\n   🔐 认证方式: {auth_option['name']}")
        
        test_url = auth_option['url']
        test_headers = headers.copy()
        if 'headers' in auth_option:
            test_headers.update(auth_option['headers'])
        
        try:
            response = requests.post(test_url, headers=test_headers, json=test_data, timeout=15)
            print(f"      📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ 成功！")
                
                # 提取响应
                if "candidates" in result and len(result["candidates"]) > 0:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"      💬 回复: {text}")
                else:
                    print(f"      📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                    
            elif response.status_code == 404:
                print(f"      ⚠️  端点不存在")
            elif response.status_code == 400:
                print(f"      ❌ 请求格式错误")
                print(f"      📄 错误: {response.text[:200]}...")
            elif response.status_code == 401 or response.status_code == 403:
                print(f"      🔒 认证失败")
                print(f"      📄 错误: {response.text[:200]}...")
            else:
                print(f"      ❌ 失败: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print(f"      ⏰ 超时")
        except requests.exceptions.ConnectionError:
            print(f"      🔌 连接错误")
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    # 格式2: 尝试简单的文本生成
    print("\n🔍 尝试格式2: 简单文本生成")
    
    simple_data = {
        "prompt": "Hello! Say 'test passed'.",
        "model": model,
        "max_tokens": 50
    }
    
    simple_url = f"{base_url}/generate"
    
    for auth_option in auth_options[:1]:  # 只试第一种
        test_url = auth_option['url'].replace(":generateContent", "")
        test_url = test_url.replace("?key=", "/generate?key=")
        
        print(f"\n   🔐 测试端点: {test_url}")
        
        try:
            response = requests.post(test_url, headers=headers, json=simple_data, timeout=15)
            print(f"      📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ 成功！")
                print(f"      📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
            else:
                print(f"      📄 响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
            
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("测试完成")
print("="*50)