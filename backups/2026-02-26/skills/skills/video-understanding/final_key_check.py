#!/usr/bin/env python3
"""
最终 API key 检查
"""

import json
import base64
import hashlib
from pathlib import Path

workspace_path = Path(__file__).parent.parent.parent
config_path = workspace_path / "config" / "gemini-config.json"

print("="*50)
print("API Key 格式分析")
print("="*50)

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    gemini_config = config.get("gemini", {})
    api_key = gemini_config.get("api_key", "")
    
    if not api_key:
        print("❌ API key 为空")
        sys.exit(1)
    
    print(f"🔑 API Key 长度: {len(api_key)} 字符")
    print(f"🔑 API Key 前缀: {api_key[:20]}...")
    print(f"🔑 API Key 后缀: ...{api_key[-20:]}")
    
    # 分析 key 格式
    print("\n🔍 Key 格式分析:")
    
    if api_key.startswith("sk-"):
        print("   ✅ 格式: OpenAI 风格 (sk- 开头)")
        
        # OpenAI key 通常是 51 字符
        if len(api_key) == 51:
            print("   ✅ 长度: 标准 OpenAI key 长度 (51 字符)")
        else:
            print(f"   ⚠️  长度: 非标准长度 ({len(api_key)} 字符)")
            
    elif api_key.startswith("AIza"):
        print("   ✅ 格式: Google AI Studio 风格 (AIza 开头)")
    elif ":" in api_key:
        print("   ✅ 格式: 可能包含用户名:密码格式")
    elif len(api_key) == 64:
        print("   ✅ 格式: 可能是 64 字符的 hex key")
    else:
        print("   ⚠️  格式: 未知格式")
    
    # 检查是否可能是 base64 编码
    print("\n🔍 Base64 检查:")
    try:
        # 移除可能的 sk- 前缀
        key_body = api_key[3:] if api_key.startswith("sk-") else api_key
        
        # 尝试解码
        decoded = base64.b64decode(key_body + '=' * (-len(key_body) % 4))
        print(f"   ✅ 可能是 Base64 编码")
        print(f"   📊 解码后长度: {len(decoded)} 字节")
        print(f"   📊 解码后 Hex: {decoded.hex()[:50]}...")
    except:
        print("   ❌ 不是有效的 Base64")
    
    # 检查字符组成
    print("\n🔍 字符组成分析:")
    
    import string
    
    lowercase = sum(1 for c in api_key if c in string.ascii_lowercase)
    uppercase = sum(1 for c in api_key if c in string.ascii_uppercase)
    digits = sum(1 for c in api_key if c in string.digits)
    special = len(api_key) - lowercase - uppercase - digits
    
    print(f"   📊 小写字母: {lowercase} ({lowercase/len(api_key)*100:.1f}%)")
    print(f"   📊 大写字母: {uppercase} ({uppercase/len(api_key)*100:.1f}%)")
    print(f"   📊 数字: {digits} ({digits/len(api_key)*100:.1f}%)")
    print(f"   📊 特殊字符: {special} ({special/len(api_key)*100:.1f}%)")
    
    # 常见问题检查
    print("\n🔍 常见问题检查:")
    
    issues = []
    
    # 检查是否有空格
    if ' ' in api_key:
        issues.append("包含空格")
    
    # 检查是否有换行符
    if '\n' in api_key or '\r' in api_key:
        issues.append("包含换行符")
    
    # 检查是否被截断
    if api_key.endswith('...'):
        issues.append("可能被截断")
    
    # 检查常见无效模式
    if api_key == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        issues.append("示例 key (需要替换)")
    
    if len(api_key) < 20:
        issues.append("过短")
    
    if issues:
        print(f"   ⚠️  发现问题: {', '.join(issues)}")
    else:
        print("   ✅ 未发现明显格式问题")
    
    print("\n" + "="*50)
    print("建议:")
    print("="*50)
    
    print("1. 🔑 验证 API key 有效性")
    print("   - 这个 key 可能已过期或被撤销")
    print("   - 请联系中转站提供商确认 key 状态")
    
    print("\n2. 📋 获取使用文档")
    print("   - 请求中转站提供 API 使用文档")
    print("   - 确认正确的请求格式和端点")
    
    print("\n3. 🎯 测试其他用途")
    print("   - 尝试在 Postman 或 curl 中测试")
    print("   - 确认 key 是否支持视频多模态")
    
    print("\n4. 🔄 备用方案")
    print("   - 考虑使用原生的 Google Gemini API")
    print("   - 申请 Google AI Studio 的 API key")
    
except Exception as e:
    print(f"❌ 分析失败: {e}")

print("\n" + "="*50)
print("分析完成")
print("="*50)