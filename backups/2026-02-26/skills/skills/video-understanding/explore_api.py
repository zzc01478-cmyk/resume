#!/usr/bin/env python3
"""
探索中转站 API 格式
"""

import json
import requests
import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("探索中转站 API 格式")
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
    
    # 尝试不同的认证方式
    auth_methods = [
        {"name": "Bearer Token", "headers": {"Authorization": f"Bearer {api_key}"}},
        {"name": "API Key Header", "headers": {"X-API-Key": api_key}},
        {"name": "API Key Query", "headers": {}, "query_param": True},
        {"name": "Basic Auth", "headers": {"Authorization": f"Basic {api_key}"}},
    ]
    
    # 尝试不同的端点
    endpoints = [
        "/chat/completions",
        "/v1/chat/completions",
        "/generate",
        "/v1/generate",
        "/completions",
        "/v1/completions",
    ]
    
    test_data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Hello"
            }
        ],
        "max_tokens": 10
    }
    
    for auth_method in auth_methods:
        print(f"\n🔍 尝试认证方式: {auth_method['name']}")
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            
            headers = {
                "Content-Type": "application/json",
                **auth_method.get("headers", {})
            }
            
            # 如果是查询参数方式
            if auth_method.get("query_param"):
                url = f"{url}?api_key={api_key}"
            
            print(f"   📍 测试端点: {endpoint}")
            
            try:
                response = requests.post(url, headers=headers, json=test_data, timeout=10)
                print(f"      📊 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      ✅ 成功！")
                    result = response.json()
                    print(f"      📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                    break
                elif response.status_code == 404:
                    print(f"      ⚠️  端点不存在")
                elif response.status_code == 401:
                    print(f"      🔒 认证失败")
                else:
                    print(f"      ❌ 失败: {response.text[:100]}...")
                    
            except requests.exceptions.Timeout:
                print(f"      ⏰ 超时")
            except requests.exceptions.ConnectionError:
                print(f"      🔌 连接错误")
            except Exception as e:
                print(f"      ❌ 异常: {e}")
    
    print("\n" + "="*50)
    print("额外测试：检查API文档或健康端点")
    print("="*50)
    
    # 尝试获取API信息
    info_endpoints = ["/", "/health", "/status", "/v1/models", "/models"]
    
    for endpoint in info_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 检查端点: {endpoint}")
        
        try:
            # 尝试GET请求
            response = requests.get(url, timeout=10)
            print(f"   📊 GET 状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   📄 响应: {response.text[:200]}...")
                
            # 尝试带认证头的GET请求
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   🔐 带认证 GET 状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   📄 响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
except Exception as e:
    print(f"❌ 探索失败: {e}")

print("\n" + "="*50)
print("探索完成")
print("="*50)