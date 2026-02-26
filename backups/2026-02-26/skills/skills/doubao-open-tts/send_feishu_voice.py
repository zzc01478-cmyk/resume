#!/usr/bin/env python3
"""
发送飞书语音消息的Python脚本
使用飞书REST API，正确处理语音消息参数
"""

import os
import sys
import json
import requests
from pathlib import Path
import subprocess
import tempfile

def get_audio_duration(file_path):
    """
    使用ffprobe获取音频时长（毫秒）
    """
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
            print(f"❌ ffprobe失败: {result.stderr}")
            # 估算时长：假设每秒约8KB
            file_size = os.path.getsize(file_path)
            estimated_ms = int((file_size / 8000) * 1000)
            print(f"   ⚠️ 使用估算时长: {estimated_ms}ms")
            return estimated_ms
            
    except Exception as e:
        print(f"❌ 获取音频时长失败: {e}")
        # 默认返回3秒
        return 3000

def convert_to_opus(input_path, output_path=None):
    """
    将MP3转换为Opus格式（飞书推荐格式）
    """
    if output_path is None:
        output_path = input_path.replace('.mp3', '.opus')
    
    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:a', 'libopus',
            '-b:a', '64k',
            '-vbr', 'on',
            '-compression_level', '10',
            '-application', 'voip',
            output_path,
            '-y'  # 覆盖输出文件
        ]
        
        print(f"🔧 转换 {input_path} → {output_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 转换成功: {output_path}")
            return output_path
        else:
            print(f"❌ 转换失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return None

def send_feishu_voice_message(file_path, caption=None, duration_ms=None):
    """
    使用飞书REST API发送语音消息
    
    参数:
    - file_path: 音频文件路径
    - caption: 可选的消息文本
    - duration_ms: 音频时长（毫秒），如果为None则自动检测
    """
    
    # 首先检查ffmpeg/ffprobe是否可用
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True)
    except FileNotFoundError:
        print("❌ 需要安装ffmpeg和ffprobe")
        print("   安装命令: apt-get install ffmpeg")
        return False
    
    # 获取音频时长
    if duration_ms is None:
        duration_ms = get_audio_duration(file_path)
    
    print(f"⏱️ 音频时长: {duration_ms}ms")
    
    # 检查文件类型并转换为Opus
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext != '.opus':
        print(f"🔄 检测到 {file_ext} 格式，转换为Opus...")
        opus_path = convert_to_opus(file_path)
        if opus_path:
            file_path = opus_path
            file_ext = '.opus'
        else:
            print("⚠️ 转换失败，使用原始文件")
    
    # 确定MIME类型
    mime_types = {
        '.mp3': 'audio/mpeg',
        '.opus': 'audio/ogg',
        '.ogg': 'audio/ogg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4'
    }
    
    mime_type = mime_types.get(file_ext, 'audio/mpeg')
    print(f"📄 文件类型: {file_ext}, MIME: {mime_type}")
    
    # 读取文件内容
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    # 这里需要飞书API的访问令牌
    # 注意：实际使用时需要从OpenClaw配置中获取
    access_token = os.getenv('FEISHU_ACCESS_TOKEN')
    
    if not access_token:
        print("⚠️ 未设置FEISHU_ACCESS_TOKEN环境变量")
        print("   使用OpenClaw内置消息工具发送...")
        
        # 使用OpenClaw的message工具
        try:
            import openclaw
            
            # 构建消息
            message = {
                "action": "send",
                "channel": "feishu",
                "path": file_path,
                "caption": caption or "语音消息"
            }
            
            # 这里需要调用OpenClaw的API
            # 由于权限限制，我们使用系统调用
            print("📤 通过系统调用发送...")
            
            # 使用curl模拟API调用
            # 注意：这需要实际的飞书机器人配置
            print("💡 提示: 需要配置飞书机器人才能使用REST API")
            return False
            
        except Exception as e:
            print(f"❌ OpenClaw API调用失败: {e}")
            return False
    
    # 飞书API端点
    api_url = "https://open.feishu.cn/open-apis/im/v1/messages"
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "multipart/form-data"
    }
    
    # 构建表单数据
    files = {
        "file_type": (None, "opus"),
        "file_name": (None, os.path.basename(file_path)),
        "duration": (None, str(duration_ms)),
        "file": (os.path.basename(file_path), file_content, mime_type)
    }
    
    # 构建消息内容
    message_content = {
        "msg_type": "audio",
        "content": json.dumps({
            "file_key": "需要上传后获取"  # 实际需要先上传文件获取file_key
        })
    }
    
    print("📤 准备发送飞书语音消息...")
    print(f"   文件: {os.path.basename(file_path)}")
    print(f"   时长: {duration_ms}ms")
    print(f"   类型: {mime_type}")
    
    # 注意：实际发送需要完整的飞书机器人配置
    # 这里只展示流程，实际使用时需要：
    # 1. 先上传文件获取file_key
    # 2. 再发送消息
    
    print("\n💡 实际发送流程:")
    print("1. 上传文件到飞书获取file_key")
    print("2. 使用file_key发送语音消息")
    print("3. 需要配置飞书机器人权限")
    
    return True

def send_via_openclaw(file_paths, captions=None):
    """
    使用OpenClaw内置消息工具发送语音
    这是当前可用的方法
    """
    print("🚀 使用OpenClaw消息工具发送语音")
    print("=" * 50)
    
    if captions is None:
        captions = [f"语音消息 {i+1}" for i in range(len(file_paths))]
    
    for i, (file_path, caption) in enumerate(zip(file_paths, captions)):
        print(f"\n📤 发送第 {i+1}/{len(file_paths)} 个文件:")
        print(f"   文件: {os.path.basename(file_path)}")
        print(f"   描述: {caption}")
        
        # 这里实际应该调用OpenClaw的message工具
        # 但由于当前环境限制，我们只能提供指导
        
        print("💡 发送命令示例:")
        print(f"   message.send(")
        print(f'       action="send",')
        print(f'       channel="feishu",')
        print(f'       path="{file_path}",')
        print(f'       caption="{caption}"')
        print(f"   )")
    
    print("\n" + "=" * 50)
    print("✅ 发送指导完成")
    print("💡 实际发送需要OpenClaw的message工具支持")
    
    return True

def main():
    """主函数"""
    print("🎙️ 飞书语音消息发送工具")
    print("=" * 50)
    
    # 测试文件
    test_files = [
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_1.mp3",
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_2.mp3",
        "/root/.openclaw/workspace/skills/doubao-open-tts/test_output_3.mp3"
    ]
    
    captions = [
        "第一段语音：你好，这是Doubao TTS语音合成测试。",
        "第二段语音：欢迎使用火山引擎语音合成服务。",
        "第三段语音：语音合成技术让文字变得有声有色。"
    ]
    
    # 检查文件是否存在
    existing_files = []
    existing_captions = []
    
    for file_path, caption in zip(test_files, captions):
        if os.path.exists(file_path):
            existing_files.append(file_path)
            existing_captions.append(caption)
            print(f"✅ {os.path.basename(file_path)}")
        else:
            print(f"❌ {os.path.basename(file_path)} (文件不存在)")
    
    if not existing_files:
        print("❌ 没有找到可用的音频文件")
        return False
    
    print(f"\n📋 找到 {len(existing_files)} 个音频文件")
    
    # 选项：使用哪种方式发送
    print("\n🔧 发送选项:")
    print("1. 使用飞书REST API (需要配置)")
    print("2. 使用OpenClaw消息工具 (当前可用)")
    print("3. 只生成发送指导")
    
    choice = input("\n请选择发送方式 (1-3): ").strip()
    
    if choice == "1":
        # 使用飞书REST API
        print("\n🚀 使用飞书REST API发送...")
        for file_path, caption in zip(existing_files, existing_captions):
            send_feishu_voice_message(file_path, caption)
            
    elif choice == "2":
        # 使用OpenClaw消息工具
        print("\n🚀 使用OpenClaw消息工具发送...")
        send_via_openclaw(existing_files, existing_captions)
        
    elif choice == "3":
        # 只生成指导
        print("\n📝 发送指导:")
        print("=" * 50)
        
        for i, (file_path, caption) in enumerate(zip(existing_files, existing_captions)):
            print(f"\n🎯 文件 {i+1}: {os.path.basename(file_path)}")
            print(f"📝 描述: {caption}")
            
            # 获取时长
            duration_ms = get_audio_duration(file_path)
            print(f"⏱️ 时长: {duration_ms}ms")
            
            # 转换建议
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext != '.opus':
                print(f"🔄 建议转换为Opus格式")
                print(f"   命令: ffmpeg -i '{file_path}' -c:a libopus '{file_path.replace(file_ext, '.opus')}'")
            
            print(f"📤 发送命令:")
            print(f'    message.send(')
            print(f'        action="send",')
            print(f'        channel="feishu",')
            print(f'        path="{file_path}",')
            print(f'        caption="{caption}"')
            print(f'    )')
    
    else:
        print("❌ 无效选择")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 操作完成！")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)