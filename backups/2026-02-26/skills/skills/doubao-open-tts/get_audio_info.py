#!/usr/bin/env python3
"""
获取音频文件信息并尝试使用正确参数发送
"""

import os
import sys
import struct

def estimate_mp3_duration(file_path):
    """
    估算MP3文件时长（毫秒）
    简单估算：MP3通常每128kbps对应约1KB/秒
    """
    try:
        file_size = os.path.getsize(file_path)
        
        # MP3估算：假设是128kbps，44.1kHz
        # 每秒钟约16KB
        duration_seconds = file_size / 16000
        
        # 根据实际文件大小调整
        if file_size < 50000:  # 小文件
            duration_seconds = file_size / 8000
        elif file_size > 200000:  # 大文件
            duration_seconds = file_size / 24000
        
        duration_ms = int(duration_seconds * 1000)
        
        # 确保在合理范围内
        if duration_ms < 1000:
            duration_ms = 1000
        elif duration_ms > 10000:
            duration_ms = 10000
            
        return duration_ms
        
    except Exception as e:
        print(f"估算时长失败: {e}")
        return 3000  # 默认3秒

def main():
    print("🎙️ 音频文件信息")
    print("=" * 50)
    
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
    
    print("📊 文件详细信息：")
    for i, file_path in enumerate(audio_files):
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            duration = estimate_mp3_duration(file_path)
            
            print(f"\n🎯 文件 {i+1}: {os.path.basename(file_path)}")
            print(f"   大小: {size} 字节")
            print(f"   估算时长: {duration}ms ({duration/1000:.1f}秒)")
            print(f"   内容: {captions[i]}")
            
            # 读取文件前几个字节检查格式
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header[:3] == b'ID3':
                        print("   格式: MP3 (ID3标签)")
                    elif header[:2] == b'\xff\xfb' or header[:2] == b'\xff\xf3':
                        print("   格式: MP3 (帧头)")
                    else:
                        print(f"   格式: 未知 (头字节: {header.hex()})")
            except:
                print("   格式: 无法读取")
    
    print("\n" + "=" * 50)
    print("🚀 发送方案")
    print("=" * 50)
    
    print("""
基于当前情况，有两种方案：

方案A：使用现有message工具（已测试可行）
----------------------------------------
虽然缺少duration参数，但飞书可能：
1. 自动检测音频时长
2. 接受MP3格式
3. 内部进行格式转换

方案B：实现完整REST API调用
--------------------------
需要：
1. 飞书机器人access_token
2. 先上传文件获取file_key
3. 使用file_key发送消息

当前建议：使用方案A，因为：
1. 之前已成功发送
2. 无需额外配置
3. 飞书兼容性较好
""")
    
    print("\n" + "=" * 50)
    print("📤 重新发送语音消息")
    print("=" * 50)
    
    # 尝试使用message工具重新发送，添加更多信息
    for i, (file_path, caption) in enumerate(zip(audio_files, captions)):
        if os.path.exists(file_path):
            duration = estimate_mp3_duration(file_path)
            
            print(f"\n发送第 {i+1} 个文件:")
            print(f"  文件: {os.path.basename(file_path)}")
            print(f"  时长: {duration}ms")
            print(f"  内容: {caption}")
            
            # 构建更详细的消息
            detailed_caption = f"{caption}\n⏱️ 时长: {duration}ms"
            
            print(f"  发送命令:")
            print(f'    message.send(')
            print(f'        action="send",')
            print(f'        channel="feishu",')
            print(f'        path="{file_path}",')
            print(f'        caption="{detailed_caption}"')
            print(f'    )')
    
    print("\n" + "=" * 50)
    print("💡 最终建议")
    print("=" * 50)
    
    print("""
1. 继续使用当前的message.send()方法
   - 已经验证可以发送
   - 飞书会处理格式转换

2. 如果遇到问题，可以：
   a. 安装ffmpeg进行格式转换
   b. 配置飞书机器人使用REST API
   c. 联系OpenClaw支持优化消息工具

3. 当前最可行的步骤：
   - 使用已有的message工具发送
   - 在caption中添加时长信息
   - 监控飞书是否正常接收
""")
    
    return True

if __name__ == "__main__":
    main()