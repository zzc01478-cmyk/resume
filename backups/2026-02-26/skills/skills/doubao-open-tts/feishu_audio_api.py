#!/usr/bin/env python3
"""
使用飞书REST API发送语音消息
完整流程：获取token → 上传文件 → 发送语音消息
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any

class FeishuAudioSender:
    """飞书语音消息发送器"""
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        """
        初始化飞书客户端
        
        Args:
            app_id: 飞书应用App ID
            app_secret: 飞书应用App Secret
        """
        self.base_url = "https://open.feishu.cn/open-apis"
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        self.access_token = None
        self.token_expire_time = 0
        
        if not self.app_id or not self.app_secret:
            print("❌ 缺少飞书应用凭证")
            print("   请设置环境变量或直接传入参数:")
            print("   - FEISHU_APP_ID: 飞书应用App ID")
            print("   - FEISHU_APP_SECRET: 飞书应用App Secret")
            print("\n   或者创建 .env 文件:")
            print("   FEISHU_APP_ID=your_app_id")
            print("   FEISHU_APP_SECRET=your_app_secret")
    
    def get_access_token(self) -> Optional[str]:
        """
        获取飞书访问令牌
        
        Returns:
            access_token or None
        """
        # 检查token是否还有效（提前5分钟刷新）
        if self.access_token and time.time() < self.token_expire_time - 300:
            return self.access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            print("🔑 获取飞书访问令牌...")
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                self.token_expire_time = time.time() + result["expire"]
                print(f"✅ 获取成功，有效期: {result['expire']}秒")
                return self.access_token
            else:
                print(f"❌ 获取失败: {result.get('msg', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"❌ 获取token异常: {e}")
            return None
    
    def upload_file(self, file_path: str, duration_ms: int = 3000) -> Optional[str]:
        """
        上传文件到飞书获取file_key
        
        Args:
            file_path: 音频文件路径
            duration_ms: 音频时长（毫秒）
            
        Returns:
            file_key or None
        """
        if not self.get_access_token():
            return None
        
        url = f"{self.base_url}/im/v1/files"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 确定文件类型和MIME类型
        if file_ext == '.mp3':
            file_type = "opus"  # 飞书推荐使用opus
            mime_type = "audio/mpeg"
        elif file_ext == '.opus':
            file_type = "opus"
            mime_type = "audio/ogg"
        elif file_ext == '.wav':
            file_type = "opus"  # 转换为opus
            mime_type = "audio/wav"
        else:
            file_type = "opus"
            mime_type = "audio/mpeg"
        
        try:
            print(f"📤 上传文件: {file_name}")
            print(f"   类型: {file_type}, 时长: {duration_ms}ms")
            
            with open(file_path, 'rb') as f:
                files = {
                    "file_type": (None, file_type),
                    "file_name": (None, file_name),
                    "duration": (None, str(duration_ms)),
                    "file": (file_name, f, mime_type)
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if result.get("code") == 0:
                    file_key = result["data"]["file_key"]
                    print(f"✅ 上传成功，file_key: {file_key[:20]}...")
                    return file_key
                else:
                    print(f"❌ 上传失败: {result.get('msg', '未知错误')}")
                    print(f"   响应: {result}")
                    return None
                    
        except Exception as e:
            print(f"❌ 上传文件异常: {e}")
            return None
    
    def send_audio_message(self, receive_id: str, file_key: str, duration_ms: int = 3000) -> bool:
        """
        发送语音消息
        
        Args:
            receive_id: 接收者ID (如: ou_xxx)
            file_key: 文件key（从upload_file获取）
            duration_ms: 音频时长（毫秒）
            
        Returns:
            是否成功
        """
        if not self.get_access_token():
            return False
        
        url = f"{self.base_url}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # 构建语音消息内容
        content = {
            "file_key": file_key,
            "duration": duration_ms
        }
        
        # 根据飞书文档，可能不需要receive_id_type字段
        # 文档示例: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create
        # 根据OpenClaw源码，可能应该使用 "file" 而不是 "audio"
        # 尝试两种方式
        msg_type = "audio"  # 先尝试audio
        
        data = {
            "receive_id": receive_id,
            "receive_id_type": "open_id",
            "msg_type": msg_type,
            "content": json.dumps(content, ensure_ascii=False)
        }
        
        try:
            print(f"📤 发送语音消息给: {receive_id}")
            print(f"   文件key: {file_key[:20]}...")
            print(f"   时长: {duration_ms}ms")
            print(f"   请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            print(f"   响应状态码: {response.status_code}")
            print(f"   响应内容: {response.text[:500]}")
            
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                message_id = result["data"]["message_id"]
                print(f"✅ 发送成功，消息ID: {message_id}")
                return True
            else:
                print(f"❌ 发送失败: {result.get('msg', '未知错误')}")
                print(f"   响应: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 发送消息异常: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   错误响应: {e.response.text[:500]}")
            return False
    
    def send_audio_file(self, receive_id: str, file_path: str, duration_ms: int = None) -> bool:
        """
        完整流程：上传文件并发送语音消息
        
        Args:
            receive_id: 接收者ID
            file_path: 音频文件路径
            duration_ms: 音频时长（毫秒），None则自动估算
            
        Returns:
            是否成功
        """
        print(f"\n🚀 开始发送语音消息流程")
        print("=" * 50)
        
        # 估算时长
        if duration_ms is None:
            duration_ms = self.estimate_audio_duration(file_path)
        
        # 1. 上传文件获取file_key
        file_key = self.upload_file(file_path, duration_ms)
        if not file_key:
            return False
        
        # 2. 发送语音消息
        success = self.send_audio_message(receive_id, file_key, duration_ms)
        
        print("=" * 50)
        if success:
            print(f"🎉 语音消息发送完成！")
        else:
            print(f"❌ 语音消息发送失败")
        
        return success
    
    def estimate_audio_duration(self, file_path: str) -> int:
        """
        估算音频文件时长（毫秒）
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            估算的时长（毫秒）
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # MP3估算：假设128kbps，每秒钟约16KB
            if file_size < 50000:  # 小文件
                duration_seconds = file_size / 8000
            elif file_size > 200000:  # 大文件
                duration_seconds = file_size / 24000
            else:  # 中等文件
                duration_seconds = file_size / 16000
            
            duration_ms = int(duration_seconds * 1000)
            
            # 确保在合理范围内
            if duration_ms < 1000:
                duration_ms = 1000
            elif duration_ms > 10000:
                duration_ms = 10000
            
            print(f"⏱️ 估算时长: {duration_ms}ms ({duration_ms/1000:.1f}秒)")
            return duration_ms
            
        except Exception as e:
            print(f"⚠️ 估算时长失败，使用默认值: {e}")
            return 3000

def test_without_credentials():
    """无凭证情况下的测试"""
    print("🧪 飞书语音消息API测试（无凭证）")
    print("=" * 60)
    
    print("📋 需要的信息:")
    print("1. 飞书应用App ID")
    print("2. 飞书应用App Secret")
    print("3. 接收者ID (如: ou_7c53b4d00420faa89d6750f31c5d6ced)")
    
    print("\n🔧 获取方法:")
    print("1. 访问飞书开放平台: https://open.feishu.cn/")
    print("2. 创建企业自建应用")
    print("3. 获取App ID和App Secret")
    print("4. 为应用添加以下权限:")
    print("   - 获取 tenant_access_token")
    print("   - 发送消息")
    print("   - 上传文件")
    
    print("\n💡 使用示例:")
    print("""
# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# 运行脚本
python feishu_audio_api.py send \\
    --receive-id "ou_xxx" \\
    --file "audio.mp3" \\
    --duration 3000
""")
    
    print("\n📁 当前可用的音频文件:")
    audio_dir = os.path.dirname(os.path.abspath(__file__))
    audio_files = [
        os.path.join(audio_dir, "test_output_1.mp3"),
        os.path.join(audio_dir, "test_output_2.mp3"),
        os.path.join(audio_dir, "test_output_3.mp3")
    ]
    
    for file_path in audio_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {os.path.basename(file_path)} ({size} 字节)")
    
    return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="飞书语音消息发送工具")
    parser.add_argument("action", choices=["send", "test"], help="操作类型")
    parser.add_argument("--receive-id", help="接收者ID")
    parser.add_argument("--file", help="音频文件路径")
    parser.add_argument("--duration", type=int, help="音频时长(毫秒)")
    parser.add_argument("--app-id", help="飞书App ID")
    parser.add_argument("--app-secret", help="飞书App Secret")
    
    args = parser.parse_args()
    
    if args.action == "send":
        if not args.receive_id or not args.file:
            print("❌ 需要 --receive-id 和 --file 参数")
            return False
        
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            return False
        
        # 创建发送器
        sender = FeishuAudioSender(args.app_id, args.app_secret)
        
        # 检查凭证
        if not sender.app_id or not sender.app_secret:
            print("❌ 缺少飞书应用凭证")
            print("   请提供 --app-id 和 --app-secret 参数")
            print("   或设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量")
            return False
        
        # 发送语音消息
        return sender.send_audio_file(
            receive_id=args.receive_id,
            file_path=args.file,
            duration_ms=args.duration
        )
    
    elif args.action == "test":
        return test_without_credentials()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)