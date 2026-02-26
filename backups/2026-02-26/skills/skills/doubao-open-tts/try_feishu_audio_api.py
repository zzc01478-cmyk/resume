#!/usr/bin/env python3
"""
尝试使用飞书API发送语音消息
"""

import os
import sys
import json
import requests
from pathlib import Path

def try_direct_api():
    """尝试直接调用飞书API"""
    print("🚀 尝试直接调用飞书API发送语音消息")
    print("=" * 60)
    
    # 飞书API端点
    base_url = "https://open.feishu.cn/open-apis"
    
    # 需要的信息（实际使用时需要配置）
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    access_token = os.getenv("FEISHU_ACCESS_TOKEN")
    
    print("🔍 检查飞书配置:")
    print(f"   FEISHU_APP_ID: {'✅ 已设置' if app_id else '❌ 未设置'}")
    print(f"   FEISHU_APP_SECRET: {'✅ 已设置' if app_secret else '❌ 未设置'}")
    print(f"   FEISHU_ACCESS_TOKEN: {'✅ 已设置' if access_token else '❌ 未设置'}")
    
    if not access_token:
        print("\n❌ 缺少飞书访问令牌")
        print("   需要先获取access_token才能调用API")
        return False
    
    # 音频文件
    audio_files = [
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_1.mp3",
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_2.mp3",
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_3.mp3"
    ]
    
    print(f"\n📁 找到 {len(audio_files)} 个音频文件")
    
    # 尝试发送第一个文件
    test_file = audio_files[0]
    if os.path.exists(test_file):
        print(f"\n🎯 尝试发送: {os.path.basename(test_file)}")
        
        # 步骤1: 上传文件获取file_key
        print("1. 上传文件获取file_key...")
        
        upload_url = f"{base_url}/im/v1/files"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            with open(test_file, 'rb') as f:
                files = {
                    "file_type": (None, "opus"),
                    "file_name": (None, "audio.opus"),
                    "duration": (None, "3000"),
                    "file": (os.path.basename(test_file), f, "audio/mpeg")
                }
                
                print(f"   📤 上传到: {upload_url}")
                print(f"   📄 文件: {os.path.basename(test_file)}")
                print(f"   🔑 Token: {access_token[:10]}...")
                
                # 这里实际应该发送请求，但需要正确的权限
                print("   ⚠️ 需要飞书机器人文件上传权限")
                print("   💡 建议: 配置飞书机器人并申请相应权限")
                
        except Exception as e:
            print(f"   ❌ 上传失败: {e}")
    
    return True

def try_message_tool_with_audio():
    """尝试使用message工具发送语音消息"""
    print("\n" + "=" * 60)
    print("🔧 尝试使用OpenClaw message工具发送语音消息")
    print("=" * 60)
    
    print("检查message工具是否支持语音消息...")
    
    # 查看message工具的帮助信息
    print("\n📋 message工具参数参考:")
    print("""
message.send({
    action: "send",
    channel: "feishu",
    target: "user:ou_xxx",  # 接收者
    message: "文本消息",     # 文本内容
    path: "/path/to/file",  # 文件路径
    caption: "文件描述",     # 文件描述
    // 可能支持的语音消息参数:
    msg_type: "audio",      // 消息类型
    duration: 3000,         // 时长(ms)
    file_type: "opus"       // 文件类型
})
""")
    
    print("\n💡 可能的问题:")
    print("1. message工具可能不支持直接发送语音消息类型")
    print("2. 需要特定的参数格式")
    print("3. 飞书API对语音消息有特殊要求")
    
    return True

def alternative_solutions():
    """替代解决方案"""
    print("\n" + "=" * 60)
    print("🔄 替代解决方案")
    print("=" * 60)
    
    print("""
方案1: 使用飞书官方SDK
--------------------------------
```python
from lark_oapi import Client, AudioMessage

# 初始化客户端
client = Client.builder() \\
    .app_id("your_app_id") \\
    .app_secret("your_app_secret") \\
    .build()

# 上传文件获取file_key
file_key = client.im.v1.files.upload(...)

# 发送语音消息
message = AudioMessage.builder() \\
    .receive_id("ou_xxx") \\
    .file_key(file_key) \\
    .duration(3000) \\
    .build()

client.im.v1.messages.create(message)
```

方案2: 使用curl直接调用API
--------------------------------
```bash
# 1. 获取access_token
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/ \\
  -H "Content-Type: application/json" \\
  -d '{"app_id":"your_app_id","app_secret":"your_app_secret"}'

# 2. 上传文件
curl -X POST https://open.feishu.cn/open-apis/im/v1/files \\
  -H "Authorization: Bearer {access_token}" \\
  -F "file_type=opus" \\
  -F "file_name=audio.opus" \\
  -F "duration=3000" \\
  -F "file=@audio.opus"

# 3. 发送消息
curl -X POST https://open.feishu.cn/open-apis/im/v1/messages \\
  -H "Authorization: Bearer {access_token}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "receive_id": "ou_xxx",
    "msg_type": "audio",
    "content": "{\\"file_key\\": \\"file_key_here\\"}"
  }'
```

方案3: 使用现有文件发送，期待飞书自动识别
--------------------------------
继续使用当前方法，飞书可能:
1. 自动将MP3文件识别为语音
2. 在客户端显示为可播放的音频
3. 虽然不是"语音消息"类型，但功能相同
""")
    
    return True

def main():
    print("🎙️ 飞书语音消息发送探索")
    print("=" * 60)
    
    # 尝试直接API
    try_direct_api()
    
    # 尝试message工具
    try_message_tool_with_audio()
    
    # 替代方案
    alternative_solutions()
    
    print("\n" + "=" * 60)
    print("🎯 建议行动")
    print("=" * 60)
    
    print("""
基于当前情况，建议:

立即行动:
1. 检查已发送的文件在飞书中是否可播放
2. 如果是可播放的音频文件，功能已实现

如需真正的"语音消息"类型:
1. 配置飞书机器人并获取相应权限
2. 使用飞书官方SDK或REST API
3. 按照语音消息规范上传和发送

当前最快速方案:
继续使用现有方法，虽然显示为"文件"但功能相同
""")
    
    return True

if __name__ == "__main__":
    main()