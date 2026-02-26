#!/usr/bin/env python3
"""
直接测试飞书API，尝试获取当前配置
"""

import os
import sys
import json

def check_openclaw_feishu_config():
    """检查OpenClaw的飞书配置"""
    print("🔍 检查OpenClaw飞书配置")
    print("=" * 50)
    
    # 可能的配置文件路径
    config_paths = [
        "/root/.openclaw/config.json",
        "/root/.openclaw/feishu.json",
        os.path.expanduser("~/.openclaw/config.json"),
        os.path.join(os.path.dirname(__file__), "../../../config.json")
    ]
    
    found_config = False
    for path in config_paths:
        if os.path.exists(path):
            print(f"📁 找到配置文件: {path}")
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    # 查找飞书相关配置
                    feishu_config = config.get('feishu') or config.get('Feishu') or {}
                    if feishu_config:
                        print(f"✅ 找到飞书配置:")
                        for key, value in feishu_config.items():
                            if 'secret' in key.lower() or 'token' in key.lower():
                                print(f"   {key}: {'*' * 10}{value[-4:] if value else ''}")
                            else:
                                print(f"   {key}: {value}")
                        found_config = True
                    else:
                        print(f"   ℹ️ 未找到飞书配置")
            except Exception as e:
                print(f"   ❌ 读取失败: {e}")
    
    if not found_config:
        print("❌ 未找到飞书配置文件")
    
    return found_config

def test_message_tool_capabilities():
    """测试message工具的能力"""
    print("\n🔧 测试message工具能力")
    print("=" * 50)
    
    print("message工具可能支持的参数:")
    print("""
message.send({
    action: "send",
    channel: "feishu",
    target: "user:ou_xxx",
    
    // 文本消息
    message: "文本内容",
    
    // 文件消息
    path: "/path/to/file",
    caption: "文件描述",
    
    // 可能支持的语音消息参数
    msg_type: "audio",
    file_key: "file_v2_xxx",  // 需要先上传获取
    duration: 3000,
    
    // 其他参数
    asVoice: true,  // 已测试
    file_type: "opus",
    mime_type: "audio/ogg"
})
""")
    
    print("\n💡 关键问题:")
    print("1. message工具是否支持直接传递file_key?")
    print("2. 是否需要先通过其他方式上传文件?")
    print("3. OpenClaw是否内部处理了文件上传?")
    
    return True

def try_alternative_approach():
    """尝试替代方法"""
    print("\n🔄 尝试替代方法")
    print("=" * 50)
    
    print("""
方法A: 使用OpenClaw内部机制
--------------------------------
如果OpenClaw已经处理了飞书认证，可能:
1. 自动获取access_token
2. 内部上传文件
3. 只需要正确参数格式

方法B: 模拟你发送图片的方式
--------------------------------
你发送了: {"image_key":"img_v3_02v8_xxx"}
这说明:
1. 图片已经上传到飞书
2. 获得了image_key
3. 可以直接使用key发送

对于语音，需要:
1. 上传音频文件获取file_key
2. 使用file_key发送语音消息

方法C: 请求OpenClaw支持
--------------------------------
如果当前工具不支持，可以:
1. 请求添加语音消息支持
2. 使用其他消息平台
3. 等待功能更新
""")
    
    return True

def main():
    print("🎯 飞书语音消息发送深度分析")
    print("=" * 50)
    
    # 检查配置
    has_config = check_openclaw_feishu_config()
    
    # 测试工具能力
    test_message_tool_capabilities()
    
    # 尝试替代方法
    try_alternative_approach()
    
    print("\n" + "=" * 50)
    print("🎯 立即行动建议")
    print("=" * 50)
    
    if has_config:
        print("""
✅ 检测到飞书配置，可以尝试:

1. 直接使用message工具的高级参数
2. 查看OpenClaw文档了解完整参数
3. 尝试不同的参数组合
""")
    else:
        print("""
❌ 未检测到飞书配置，需要:

方案1: 配置飞书应用
   1. 创建飞书自建应用
   2. 获取App ID和App Secret
   3. 配置到OpenClaw

方案2: 使用当前有限功能
   继续使用文件附件形式

方案3: 联系OpenClaw支持
   请求添加语音消息功能
""")
    
    print("\n💡 基于你发送的image_key，我推测:")
    print("   1. 你已经知道飞书文件系统的运作方式")
    print("   2. 你需要的是音频文件的file_key")
    print("   3. 当前工具可能无法直接获取file_key")
    
    return True

if __name__ == "__main__":
    main()