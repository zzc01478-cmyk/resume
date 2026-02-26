#!/usr/bin/env python3
"""
飞书语音消息API调用演示
展示完整的REST API调用流程
"""

import json
import os

def demo_api_flow():
    """演示完整的API调用流程"""
    print("🚀 飞书语音消息API调用流程演示")
    print("=" * 60)
    
    # 接收者ID（已知）
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    print(f"📱 接收者ID: {receive_id}")
    print(f"📁 音频文件: test_output_1.mp3 (84KB)")
    print(f"⏱️ 估算时长: 5250ms")
    
    print("\n" + "=" * 60)
    print("📋 完整API调用流程")
    print("=" * 60)
    
    print("""
步骤1: 获取access_token
--------------------------------
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "cli_xxxxxx",
  "app_secret": "xxxxxx-xxxx-xxxx-xxxx-xxxxxxxx"
}

响应:
{
  "code": 0,
  "msg": "success",
  "tenant_access_token": "t-xxxxxx",
  "expire": 7200
}
""")
    
    print("""
步骤2: 上传文件获取file_key
--------------------------------
POST https://open.feishu.cn/open-apis/im/v1/files
Authorization: Bearer t-xxxxxx
Content-Type: multipart/form-data

表单数据:
- file_type: opus
- file_name: test_output_1.mp3
- duration: 5250
- file: (二进制文件数据, Content-Type: audio/mpeg)

响应:
{
  "code": 0,
  "msg": "success",
  "data": {
    "file_key": "file_v2_xxxxxx"
  }
}
""")
    
    print("""
步骤3: 发送语音消息
--------------------------------
POST https://open.feishu.cn/open-apis/im/v1/messages
Authorization: Bearer t-xxxxxx
Content-Type: application/json

{
  "receive_id": "ou_7c53b4d00420faa89d6750f31c5d6ced",
  "msg_type": "audio",
  "content": "{\\"file_key\\": \\"file_v2_xxxxxx\\", \\"duration\\": 5250}"
}

响应:
{
  "code": 0,
  "msg": "success",
  "data": {
    "message_id": "om_xxxxxx"
  }
}
""")
    
    print("\n" + "=" * 60)
    print("🔧 实际Python代码")
    print("=" * 60)
    
    print("""
import requests
import json

class FeishuAudioSender:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
    
    def get_access_token(self):
        '''获取access_token'''
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        data = {"app_id": self.app_id, "app_secret": self.app_secret}
        response = requests.post(url, json=data)
        return response.json()["tenant_access_token"]
    
    def upload_file(self, file_path, duration_ms):
        '''上传文件获取file_key'''
        url = f"{self.base_url}/im/v1/files"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        with open(file_path, 'rb') as f:
            files = {
                "file_type": (None, "opus"),
                "file_name": (None, os.path.basename(file_path)),
                "duration": (None, str(duration_ms)),
                "file": (os.path.basename(file_path), f, "audio/mpeg")
            }
            response = requests.post(url, headers=headers, files=files)
            return response.json()["data"]["file_key"]
    
    def send_audio_message(self, receive_id, file_key, duration_ms):
        '''发送语音消息'''
        url = f"{self.base_url}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        content = {"file_key": file_key, "duration": duration_ms}
        data = {
            "receive_id": receive_id,
            "msg_type": "audio",
            "content": json.dumps(content)
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()["data"]["message_id"]
    
    def send(self, receive_id, file_path, duration_ms=3000):
        '''完整流程'''
        self.access_token = self.get_access_token()
        file_key = self.upload_file(file_path, duration_ms)
        message_id = self.send_audio_message(receive_id, file_key, duration_ms)
        return message_id

# 使用示例
sender = FeishuAudioSender("cli_xxxxxx", "your_app_secret")
message_id = sender.send(
    receive_id="ou_7c53b4d00420faa89d6750f31c5d6ced",
    file_path="test_output_1.mp3",
    duration_ms=5250
)
print(f"✅ 语音消息发送成功，消息ID: {message_id}")
""")
    
    print("\n" + "=" * 60)
    print("🎯 下一步行动")
    print("=" * 60)
    
    print("""
要实际发送语音消息，你需要:

1. 获取飞书应用凭证
   - App ID: 从飞书开放平台获取
   - App Secret: 从飞书开放平台获取

2. 运行完整脚本
   python feishu_audio_api.py send \\
       --app-id "你的App ID" \\
       --app-secret "你的App Secret" \\
       --receive-id "ou_7c53b4d00420faa89d6750f31c5d6ced" \\
       --file "test_output_1.mp3"

3. 验证结果
   - 检查飞书是否收到语音消息
   - 确认显示为语音气泡而非文件
""")
    
    return True

if __name__ == "__main__":
    demo_api_flow()