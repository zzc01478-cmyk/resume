#!/usr/bin/env python3
"""
绕过所有中间层，直接调用飞书REST API发送语音消息
完整独立的解决方案，不依赖OpenClaw或其他中间件
"""

import os
import sys
import json
import requests
import time
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

class DirectFeishuAudioSender:
    """直接飞书REST API语音消息发送器"""
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化直接API客户端
        
        Args:
            app_id: 飞书应用App ID
            app_secret: 飞书应用App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        self.token_expire_time = 0
        
        print(f"🔧 初始化直接飞书API客户端")
        print(f"   App ID: {app_id}")
        print(f"   App Secret: {app_secret[:10]}...")
    
    def _get_access_token_direct(self) -> Optional[str]:
        """
        直接获取access_token（绕过所有中间层）
        
        Returns:
            access_token or None
        """
        # 检查token是否还有效
        if self.access_token and time.time() < self.token_expire_time - 300:
            return self.access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            print("🔑 直接获取access_token...")
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return None
            
            result = response.json()
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                self.token_expire_time = time.time() + result["expire"]
                print(f"   ✅ 获取成功")
                print(f"   有效期: {result['expire']}秒")
                return self.access_token
            else:
                print(f"   ❌ 获取失败: {result.get('msg', '未知错误')}")
                print(f"   错误代码: {result.get('code')}")
                return None
                
        except Exception as e:
            print(f"   ❌ 获取token异常: {e}")
            return None
    
    def _upload_file_direct(self, file_path: str, duration_ms: int) -> Optional[str]:
        """
        直接上传文件到飞书（绕过中间层）
        
        Args:
            file_path: 音频文件路径
            duration_ms: 音频时长（毫秒）
            
        Returns:
            file_key or None
        """
        if not self._get_access_token_direct():
            return None
        
        url = f"{self.base_url}/im/v1/files"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # 确定MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "audio/mpeg"  # 默认
        
        print(f"📤 直接上传文件: {file_name}")
        print(f"   文件大小: {file_size} 字节")
        print(f"   MIME类型: {mime_type}")
        print(f"   时长: {duration_ms}ms")
        
        try:
            with open(file_path, 'rb') as f:
                # 构建multipart/form-data
                files = {
                    "file_type": (None, "opus"),  # 飞书推荐使用opus
                    "file_name": (None, file_name),
                    "duration": (None, str(duration_ms)),
                    "file": (file_name, f, mime_type)
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=30)
                
                if response.status_code != 200:
                    print(f"   ❌ 上传HTTP错误: {response.status_code}")
                    print(f"   响应: {response.text[:200]}")
                    return None
                
                result = response.json()
                if result.get("code") == 0:
                    file_key = result["data"]["file_key"]
                    print(f"   ✅ 上传成功")
                    print(f"   file_key: {file_key}")
                    return file_key
                else:
                    print(f"   ❌ 上传失败: {result.get('msg', '未知错误')}")
                    print(f"   错误代码: {result.get('code')}")
                    print(f"   完整响应: {result}")
                    return None
                    
        except Exception as e:
            print(f"   ❌ 上传文件异常: {e}")
            return None
    
    def _send_audio_message_direct(self, receive_id: str, file_key: str, duration_ms: int) -> Tuple[bool, Optional[str]]:
        """
        直接发送语音消息（绕过中间层）
        
        Args:
            receive_id: 接收者ID
            file_key: 文件key
            duration_ms: 音频时长
            
        Returns:
            (是否成功, 消息ID或错误信息)
        """
        if not self._get_access_token_direct():
            return False, "无法获取access_token"
        
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
        
        # 确定receive_id_type
        if receive_id.startswith("ou_"):
            receive_id_type = "open_id"
        elif receive_id.startswith("u_"):
            receive_id_type = "user_id"
        elif receive_id.startswith("on_"):
            receive_id_type = "union_id"
        elif "@" in receive_id:
            receive_id_type = "email"
        else:
            receive_id_type = "open_id"  # 默认
        
        # ✅ 关键修复：使用params传递receive_id_type
        params = {"receive_id_type": receive_id_type}
        data = {
            "receive_id": receive_id,
            "msg_type": "audio",
            "content": json.dumps(content, ensure_ascii=False)
        }
        
        print(f"📤 直接发送语音消息...")
        print(f"   接收者: {receive_id}")
        print(f"   ID类型: {receive_id_type}")
        print(f"   文件key: {file_key}")
        print(f"   时长: {duration_ms}ms")
        print(f"   params: {json.dumps(params)}")
        print(f"   data: {json.dumps(data, ensure_ascii=False)}")
        
        try:
            # ✅ 使用params参数
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=data,
                timeout=10
            )
            
            print(f"   响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    message_id = result["data"]["message_id"]
                    print(f"   ✅ 发送成功!")
                    print(f"   消息ID: {message_id}")
                    return True, message_id
                else:
                    error_msg = result.get("msg", "未知错误")
                    error_code = result.get("code")
                    print(f"   ❌ 发送失败: {error_msg}")
                    print(f"   错误代码: {error_code}")
                    print(f"   完整响应: {result}")
                    return False, f"{error_code}: {error_msg}"
            else:
                error_text = response.text[:500]
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   响应: {error_text}")
                return False, f"HTTP {response.status_code}: {error_text}"
                
        except Exception as e:
            print(f"   ❌ 发送消息异常: {e}")
            return False, str(e)
    
    def send_audio_direct(self, receive_id: str, audio_file: str, duration_ms: Optional[int] = None) -> bool:
        """
        完整流程：直接发送语音消息
        
        Args:
            receive_id: 接收者ID
            audio_file: 音频文件路径
            duration_ms: 音频时长（毫秒），None则自动估算
            
        Returns:
            是否成功
        """
        print("\n" + "=" * 60)
        print("🚀 开始直接飞书语音消息发送流程")
        print("=" * 60)
        
        # 检查文件
        if not os.path.exists(audio_file):
            print(f"❌ 文件不存在: {audio_file}")
            return False
        
        # 估算时长
        if duration_ms is None:
            duration_ms = self._estimate_audio_duration(audio_file)
        
        print(f"🎯 目标: 发送语音消息给 {receive_id}")
        print(f"📁 音频文件: {audio_file}")
        print(f"⏱️ 时长: {duration_ms}ms ({duration_ms/1000:.1f}秒)")
        
        # 1. 上传文件
        print("\n" + "-" * 40)
        print("步骤1: 上传音频文件")
        print("-" * 40)
        
        file_key = self._upload_file_direct(audio_file, duration_ms)
        if not file_key:
            print("❌ 文件上传失败，终止流程")
            return False
        
        # 2. 发送语音消息
        print("\n" + "-" * 40)
        print("步骤2: 发送语音消息")
        print("-" * 40)
        
        success, result = self._send_audio_message_direct(receive_id, file_key, duration_ms)
        
        print("\n" + "=" * 60)
        if success:
            print(f"🎉 语音消息发送成功!")
            print(f"   消息ID: {result}")
            return True
        else:
            print(f"❌ 语音消息发送失败")
            print(f"   错误: {result}")
            return False
    
    def _estimate_audio_duration(self, file_path: str) -> int:
        """
        估算音频文件时长
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            估算的时长（毫秒）
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # MP3估算：假设128kbps，每秒钟约16KB
            # 更精确的估算
            if file_size < 50000:  # 小文件
                duration_seconds = file_size / 8000  # 64kbps
            elif file_size > 200000:  # 大文件
                duration_seconds = file_size / 24000  # 192kbps
            else:  # 中等文件
                duration_seconds = file_size / 16000  # 128kbps
            
            duration_ms = int(duration_seconds * 1000)
            
            # 确保在合理范围内
            if duration_ms < 1000:
                duration_ms = 1000
            elif duration_ms > 10000:
                duration_ms = 10000
            
            print(f"⏱️ 估算音频时长: {duration_ms}ms ({duration_ms/1000:.1f}秒)")
            return duration_ms
            
        except Exception as e:
            print(f"⚠️ 估算时长失败，使用默认值: {e}")
            return 3000

def test_direct_api():
    """测试直接API调用"""
    print("🧪 测试直接飞书API调用")
    print("=" * 60)
    
    # 使用配置的App ID和App Secret
    app_id = "cli_a913daaab4789bcb"
    app_secret = "TjRmP8aMFTTERjPqVDXsbffEsTuA6GPc"
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 创建直接发送器
    sender = DirectFeishuAudioSender(app_id, app_secret)
    
    # 测试发送第一段语音
    audio_file = "test_output_1.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        print(f"   当前目录: {os.getcwd()}")
        print(f"   可用文件:")
        for f in os.listdir("."):
            if f.endswith(".mp3"):
                print(f"     - {f}")
        return False
    
    # 发送语音消息
    return sender.send_audio_direct(receive_id, audio_file)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="直接飞书REST API语音消息发送工具")
    parser.add_argument("action", choices=["send", "test"], help="操作类型")
    parser.add_argument("--receive-id", help="接收者ID")
    parser.add_argument("--file", help="音频文件路径")
    parser.add_argument("--duration", type=int, help="音频时长(毫秒)")
    
    args = parser.parse_args()
    
    if args.action == "send":
        if not args.receive_id or not args.file:
            print("❌ 需要 --receive-id 和 --file 参数")
            return False
        
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            return False
        
        # 使用配置的App ID和App Secret
        app_id = "cli_a913daaab4789bcb"
        app_secret = "TjRmP8aMFTTERjPqVDXsbffEsTuA6GPc"
        
        # 创建直接发送器
        sender = DirectFeishuAudioSender(app_id, app_secret)
        
        # 发送语音消息
        return sender.send_audio_direct(
            receive_id=args.receive_id,
            audio_file=args.file,
            duration_ms=args.duration
        )
    
    elif args.action == "test":
        return test_direct_api()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)