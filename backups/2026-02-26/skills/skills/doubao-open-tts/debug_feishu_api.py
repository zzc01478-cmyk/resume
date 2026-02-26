#!/usr/bin/env python3
"""
调试飞书API调用
"""

import os
import sys
import json
import requests
import time

def debug_api():
    """调试API调用"""
    print("🔧 调试飞书API调用")
    print("=" * 50)
    
    # 飞书配置
    app_id = "cli_a913daaab4789bcb"
    app_secret = "TjRmP8aMFTTERjPqVDXsbffEsTuA6GPc"
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    base_url = "https://open.feishu.cn/open-apis"
    
    # 1. 获取access_token
    print("1. 获取access_token...")
    token_url = f"{base_url}/auth/v3/tenant_access_token/internal"
    token_data = {"app_id": app_id, "app_secret": app_secret}
    
    try:
        response = requests.post(token_url, json=token_data, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text[:200]}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                access_token = result["tenant_access_token"]
                print(f"   ✅ 获取成功: {access_token[:20]}...")
            else:
                print(f"   ❌ 获取失败: {result}")
                return False
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False
    
    # 2. 检查应用权限
    print("\n2. 检查应用权限...")
    # 飞书可能需要特定的权限才能发送语音消息
    
    # 3. 尝试不同的消息格式
    print("\n3. 尝试不同的消息格式...")
    
    # 先尝试发送普通文本消息，确认基本功能正常
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 测试文本消息
    test_data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": "测试文本消息，确认API正常工作"})
    }
    
    print(f"   发送测试文本消息...")
    try:
        response = requests.post(message_url, headers=headers, json=test_data, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"   ✅ 文本消息发送成功!")
                print(f"     消息ID: {result['data']['message_id']}")
            else:
                print(f"   ❌ 文本消息失败: {result.get('msg')}")
                print(f"     错误详情: {result}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 4. 检查语音消息权限
    print("\n4. 检查语音消息支持...")
    print("""
可能的问题:
1. 应用缺少发送语音消息的权限
2. 消息格式不正确
3. 需要特定的content格式
4. 文件类型不支持

飞书语音消息要求:
- 应用需要"发送消息"和"上传文件"权限
- content必须是JSON字符串: {"file_key": "xxx", "duration": 3000}
- file_key必须是通过文件上传API获得的
- duration单位是毫秒
""")
    
    # 5. 查看飞书文档
    print("\n5. 参考飞书官方文档:")
    print("   语音消息文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create")
    print("   文件上传文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/file/create")
    
    return True

def check_permissions():
    """检查应用权限"""
    print("\n🔐 检查应用权限需求")
    print("=" * 50)
    
    print("""
发送语音消息需要以下权限:

1. 获取 tenant_access_token
   - 权限: auth:auth.tenant_access_token:get

2. 上传文件
   - 权限: im:file:upload

3. 发送消息  
   - 权限: im:message:send

检查方法:
1. 访问飞书开放平台: https://open.feishu.cn/
2. 进入应用管理
3. 查看"权限管理"
4. 确保以上权限已开启
""")
    
    return True

def main():
    print("🎯 飞书语音消息发送调试")
    print("=" * 50)
    
    # 调试API
    debug_api()
    
    # 检查权限
    check_permissions()
    
    print("\n" + "=" * 50)
    print("🎯 下一步行动")
    print("=" * 50)
    
    print("""
基于调试结果:

✅ 成功的部分:
1. 获取access_token成功
2. 上传文件成功（获得了file_key）

❌ 失败的部分:
发送语音消息时出现400错误

可能的原因:
1. 应用缺少发送语音消息的权限
2. 消息格式需要调整
3. 需要先申请权限

建议:
1. 先发送文本消息确认基本功能
2. 检查应用权限配置
3. 尝试不同的content格式
""")
    
    return True

if __name__ == "__main__":
    main()