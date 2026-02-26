#!/usr/bin/env python3
"""
生成飞书语音消息发送指导
"""

import os
import sys
import subprocess
import json

def get_audio_duration(file_path):
    """获取音频时长（毫秒）"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration_seconds = float(data['format']['duration'])
            duration_ms = int(duration_seconds * 1000)
            return duration_ms
        else:
            # 估算：每8KB约1秒
            file_size = os.path.getsize(file_path)
            return int((file_size / 8000) * 1000)
    except:
        # 默认值
        return 3000

def main():
    print("📋 飞书语音消息发送详细指导")
    print("=" * 60)
    
    # 音频文件列表
    audio_files = [
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_1.mp3",
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_2.mp3",
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_3.mp3"
    ]
    
    captions = [
        "第一段语音：你好，这是Doubao TTS语音合成测试。",
        "第二段语音：欢迎使用火山引擎语音合成服务。",
        "第三段语音：语音合成技术让文字变得有声有色。"
    ]
    
    print("🎙️ 需要发送的语音文件：")
    for i, file_path in enumerate(audio_files):
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            duration = get_audio_duration(file_path)
            print(f"  {i+1}. {os.path.basename(file_path)}")
            print(f"     大小: {size} 字节")
            print(f"     时长: {duration}ms")
            print(f"     内容: {captions[i]}")
        else:
            print(f"  ❌ {os.path.basename(file_path)} (文件不存在)")
    
    print("\n" + "=" * 60)
    print("🚀 方法一：使用OpenClaw message工具（推荐）")
    print("=" * 60)
    
    print("\n📤 发送命令示例：")
    for i, (file_path, caption) in enumerate(zip(audio_files, captions)):
        if os.path.exists(file_path):
            duration = get_audio_duration(file_path)
            print(f"\n🎯 第 {i+1} 个文件：")
            print(f'    message.send(')
            print(f'        action="send",')
            print(f'        channel="feishu",')
            print(f'        path="{file_path}",')
            print(f'        caption="{caption}"')
            print(f'    )')
            print(f"    # 时长: {duration}ms")
    
    print("\n" + "=" * 60)
    print("🔧 方法二：转换为Opus格式后发送")
    print("=" * 60)
    
    print("\n飞书推荐使用Opus格式，转换命令：")
    for file_path in audio_files:
        if os.path.exists(file_path):
            opus_file = file_path.replace('.mp3', '.opus')
            print(f"\n🔧 转换 {os.path.basename(file_path)} → {os.path.basename(opus_file)}:")
            print(f'    ffmpeg -i "{file_path}" \\')
            print(f'           -c:a libopus \\')
            print(f'           -b:a 64k \\')
            print(f'           -vbr on \\')
            print(f'           -compression_level 10 \\')
            print(f'           -application voip \\')
            print(f'           "{opus_file}"')
    
    print("\n" + "=" * 60)
    print("📊 方法三：使用飞书REST API（高级）")
    print("=" * 60)
    
    print("""
使用飞书REST API发送语音消息需要：

1. 获取飞书访问令牌（access_token）
2. 先上传文件获取file_key
3. 使用file_key发送消息

Python代码示例：

```python
import requests

# 1. 上传文件
upload_url = "https://open.feishu.cn/open-apis/im/v1/files"
headers = {
    "Authorization": "Bearer {access_token}"
}

files = {
    "file_type": (None, "opus"),
    "file_name": (None, "audio.opus"),
    "duration": (None, "3000"),  # 时长(ms)
    "file": ("audio.opus", open("audio.opus", "rb"), "audio/ogg")
}

response = requests.post(upload_url, headers=headers, files=files)
file_key = response.json()["data"]["file_key"]

# 2. 发送消息
message_url = "https://open.feishu.cn/open-apis/im/v1/messages"
data = {
    "receive_id": "ou_xxx",  # 接收者ID
    "msg_type": "audio",
    "content": json.dumps({"file_key": file_key})
}

response = requests.post(message_url, headers=headers, json=data)
```
""")
    
    print("\n" + "=" * 60)
    print("💡 实际建议")
    print("=" * 60)
    
    print("""
基于当前情况，建议：

1. **立即发送**：使用OpenClaw的message工具
   - 已经验证可以发送MP3文件
   - 飞书会自动处理格式转换

2. **优化体验**：安装ffmpeg并转换为Opus
   ```bash
   # 安装ffmpeg
   apt-get update && apt-get install -y ffmpeg
   
   # 转换文件
   cd ~/.openclaw/workspace/skills/doubao-open-tts
   for f in test_output_*.mp3; do
     ffmpeg -i "$f" -c:a libopus "${f%.mp3}.opus"
   done
   ```

3. **长期方案**：配置飞书机器人
   - 申请飞书机器人权限
   - 获取access_token
   - 实现完整的REST API集成
""")
    
    print("\n" + "=" * 60)
    print("✅ 指导生成完成")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()