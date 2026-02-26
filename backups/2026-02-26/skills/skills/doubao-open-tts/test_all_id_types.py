#!/usr/bin/env python3
"""
测试所有可能的receive_id_type
"""

import requests
import json

def test_id_types():
    """测试所有ID类型"""
    print("🔧 测试所有receive_id_type")
    print("=" * 50)
    
    # 飞书配置
    app_id = "cli_a913daaab4789bcb"
    app_secret = "TjRmP8aMFTTERjPqVDXsbffEsTuA6GPc"
    base_url = "https://open.feishu.cn/open-apis"
    
    # 1. 获取token
    print("1. 获取access_token...")
    token_url = f"{base_url}/auth/v3/tenant_access_token/internal"
    response = requests.post(token_url, json={"app_id": app_id, "app_secret": app_secret})
    
    if response.status_code != 200:
        print(f"   ❌ 获取token失败: {response.text}")
        return False
    
    token_data = response.json()
    if token_data.get("code") != 0:
        print(f"   ❌ token错误: {token_data}")
        return False
    
    access_token = token_data["tenant_access_token"]
    print(f"   ✅ 获取成功")
    
    # 2. 测试所有可能的ID类型
    print("\n2. 测试所有receive_id_type...")
    
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 接收者ID
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 所有可能的ID类型
    id_types = [
        "open_id",
        "user_id", 
        "union_id",
        "email",
        "chat_id"
    ]
    
    for id_type in id_types:
        print(f"\n   📤 测试: receive_id_type = {id_type}")
        
        data = {
            "receive_id": receive_id,
            "receive_id_type": id_type,
            "msg_type": "text",
            "content": json.dumps({"text": f"测试ID类型: {id_type}"})
        }
        
        try:
            response = requests.post(message_url, headers=headers, json=data, timeout=10)
            print(f"      状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print(f"      ✅ 成功! 消息ID: {result['data']['message_id']}")
                    print(f"      🎯 正确的ID类型是: {id_type}")
                    return id_type
                else:
                    print(f"      ❌ 失败: {result.get('msg')}")
            else:
                print(f"      ❌ HTTP错误")
                print(f"      响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    # 3. 尝试获取用户信息来确定ID类型
    print("\n3. 尝试获取用户信息...")
    print("""
可能的问题:
1. ou_7c53b4d00420faa89d6750f31c5d6ced 可能不是有效的open_id
2. 需要先通过其他API获取用户信息
3. 可能需要使用user_id而不是open_id
""")
    
    # 尝试通过手机号或邮箱获取用户信息
    print("\n4. 其他可能性:")
    print("""
a) 可能之前成功是因为:
   - 使用了不同的API版本
   - 使用了不同的参数组合
   - 使用了不同的ID格式

b) 可能的解决方案:
   1. 尝试使用user_id而不是open_id
   2. 先获取用户信息确认ID类型
   3. 查看OpenClaw内部如何发送消息
""")
    
    return None

def check_openclaw_internal():
    """检查OpenClaw内部如何发送消息"""
    print("\n🔍 检查OpenClaw内部消息发送")
    print("=" * 50)
    
    print("""
OpenClaw的message工具可能:
1. 内部处理了receive_id_type
2. 自动转换ID类型
3. 使用不同的API端点

查看方法:
1. 检查OpenClaw飞书插件源码
2. 查看消息发送日志
3. 尝试使用message工具的高级参数
""")
    
    # 检查飞书插件目录
    feishu_plugin_path = "/root/.openclaw/extensions/qqbot/node_modules/openclaw/extensions/feishu"
    print(f"\n飞书插件路径: {feishu_plugin_path}")
    
    return True

def main():
    print("🎯 找回成功发送语音消息的方法")
    print("=" * 50)
    
    # 测试所有ID类型
    correct_id_type = test_id_types()
    
    # 检查OpenClaw内部
    check_openclaw_internal()
    
    print("\n" + "=" * 50)
    print("🎯 基于测试的发现")
    print("=" * 50)
    
    if correct_id_type:
        print(f"""
✅ 找到了正确的ID类型: {correct_id_type}

解决方案:
1. 在feishu_audio_api.py中使用:
   receive_id_type = "{correct_id_type}"
   
2. 重新发送语音消息
""")
    else:
        print("""
❌ 所有ID类型测试都失败

可能的原因:
1. 应用权限仍然有问题
2. ID格式不正确
3. 需要其他认证方式

建议:
1. 查看OpenClaw如何成功发送消息
2. 检查飞书应用的实际权限状态
3. 尝试使用message工具的原始方式
""")
    
    return True

if __name__ == "__main__":
    main()