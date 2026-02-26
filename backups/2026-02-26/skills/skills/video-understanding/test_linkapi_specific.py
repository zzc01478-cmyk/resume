#!/usr/bin/env python3
"""
专门测试 linkapi.ai 中转站
"""

import json
import requests
import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("专门测试 linkapi.ai 中转站")
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
    
    # 尝试直接访问 linkapi.ai 的根路径，看看是否有信息
    print("\n🔍 检查 linkapi.ai 基本信息")
    
    try:
        # 尝试访问根路径
        response = requests.get(base_url, timeout=10)
        print(f"   📊 根路径状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   📄 响应: {response.text[:500]}")
    except Exception as e:
        print(f"   ❌ 访问根路径失败: {e}")
    
    # 尝试常见的 OpenAI 兼容端点
    print("\n🔍 测试 OpenAI 兼容端点")
    
    endpoints = [
        "/chat/completions",
        "/v1/chat/completions",
        "/completions",
        "/v1/completions",
        "/embeddings",
        "/v1/embeddings",
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 简单的测试数据
    chat_data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 10
    }
    
    completion_data = {
        "model": model,
        "prompt": "Hello",
        "max_tokens": 10
    }
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n   📍 测试端点: {endpoint}")
        
        # 根据端点类型选择数据
        if "chat" in endpoint:
            test_data = chat_data
        else:
            test_data = completion_data
        
        try:
            response = requests.post(url, headers=headers, json=test_data, timeout=15)
            print(f"      📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ 成功！")
                print(f"      📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}...")
                break
            elif response.status_code == 401:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "认证失败")
                print(f"      🔒 认证失败: {error_msg}")
            elif response.status_code == 404:
                print(f"      ⚠️  端点不存在")
            else:
                print(f"      ❌ 失败: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"      ⏰ 超时")
        except requests.exceptions.ConnectionError:
            print(f"      🔌 连接错误")
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    # 尝试不同的模型名称变体
    print("\n🔍 尝试不同的模型名称")
    
    model_variants = [
        model,  # gemini-3-flash-preview
        "gemini-3-flash",  # 可能的短名称
        "gemini-3",  # 更短的名称
        "gemini-2.0-flash-exp",  # Gemini 2.0
        "gemini-pro",  # Gemini Pro
        "gemini-1.5-pro",  # Gemini 1.5 Pro
        "gpt-4",  # 测试是否是 GPT 中转
        "claude-3-opus",  # 测试是否是 Claude 中转
    ]
    
    test_url = f"{base_url}/chat/completions"
    
    for model_variant in model_variants:
        print(f"\n   🤖 测试模型: {model_variant}")
        
        data = {
            "model": model_variant,
            "messages": [
                {"role": "user", "content": "Say 'test'"}
            ],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(test_url, headers=headers, json=data, timeout=10)
            print(f"      📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ 成功！使用模型: {model_variant}")
                print(f"      💬 回复: {result.get('choices', [{}])[0].get('message', {}).get('content', '无内容')}")
                break
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "")
                if "model" in error_msg.lower():
                    print(f"      ⚠️  模型不存在: {error_msg[:100]}")
                else:
                    print(f"      ❌ 请求错误: {error_msg[:100]}")
            else:
                print(f"      📄 响应: {response.text[:150]}...")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    # 尝试获取模型列表（如果支持）
    print("\n🔍 尝试获取模型列表")
    
    models_url = f"{base_url}/models"
    
    try:
        response = requests.get(models_url, headers=headers, timeout=10)
        print(f"   📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 成功获取模型列表！")
            
            if isinstance(result, dict) and "data" in result:
                models = result["data"]
                print(f"   📋 找到 {len(models)} 个模型:")
                for m in models[:10]:  # 显示前10个
                    model_id = m.get("id", "未知")
                    print(f"      - {model_id}")
            else:
                print(f"   📄 响应格式: {json.dumps(result, indent=2, ensure_ascii=False)[:400]}...")
        else:
            print(f"   📄 响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("测试完成")
print("="*50)