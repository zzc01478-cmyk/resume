#!/usr/bin/env python3
"""
测试 OpenAI 兼容格式
"""

import json
import requests
import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("测试 OpenAI 兼容格式")
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
    print(f"🔑 API Key 前缀: {api_key[:10]}...")
    
    # 这个 key 以 "sk-" 开头，看起来是 OpenAI 格式
    # 尝试 OpenAI 兼容的端点
    
    # 端点1: /v1/chat/completions (标准 OpenAI)
    url = f"{base_url}/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 尝试不同的模型名称
    model_variants = [
        model,  # gemini-3-flash-preview
        "gpt-3.5-turbo",  # 常见的 OpenAI 模型
        "gpt-4",  # 另一个常见模型
        "text-davinci-003",  # 补全模型
        model.replace("gemini-", "gpt-"),  # 替换前缀
    ]
    
    for model_variant in model_variants:
        print(f"\n🔍 尝试模型: {model_variant}")
        
        data = {
            "model": model_variant,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Please say 'test successful'."
                }
            ],
            "max_tokens": 50
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            print(f"   📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 成功！")
                
                if "choices" in result and len(result["choices"]) > 0:
                    reply = result["choices"][0]["message"]["content"]
                    print(f"   💬 回复: {reply}")
                else:
                    print(f"   📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                    
            elif response.status_code == 404:
                print(f"   ⚠️  端点不存在")
            elif response.status_code == 400:
                print(f"   ❌ 请求错误: {response.text[:200]}...")
            elif response.status_code == 401:
                print(f"   🔒 认证失败: {response.text[:200]}...")
            else:
                print(f"   ❌ 失败: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 尝试补全端点
    print("\n🔍 尝试补全端点")
    
    completion_url = f"{base_url}/completions"
    
    for model_variant in ["text-davinci-003", "gpt-3.5-turbo-instruct", model]:
        print(f"\n   🤖 模型: {model_variant}")
        
        completion_data = {
            "model": model_variant,
            "prompt": "Say 'hello world':",
            "max_tokens": 10
        }
        
        try:
            response = requests.post(completion_url, headers=headers, json=completion_data, timeout=15)
            print(f"      📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ 成功！")
                print(f"      📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
            else:
                print(f"      📄 响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
            
    # 尝试获取模型列表
    print("\n🔍 尝试获取可用模型")
    
    models_url = f"{base_url}/models"
    
    try:
        response = requests.get(models_url, headers=headers, timeout=15)
        print(f"   📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 成功！")
            
            if "data" in result:
                models = result["data"]
                print(f"   📋 可用模型 ({len(models)} 个):")
                for m in models[:5]:  # 只显示前5个
                    print(f"      - {m.get('id', '未知')}")
                if len(models) > 5:
                    print(f"      ... 还有 {len(models)-5} 个模型")
            else:
                print(f"   📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}...")
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