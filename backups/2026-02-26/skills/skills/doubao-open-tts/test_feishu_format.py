#!/usr/bin/env python3
"""
测试飞书API的正确格式
"""

import requests
import json

def test_api_format():
    """测试API格式"""
    print("🔧 测试飞书API格式")
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
    print(f"   ✅ 获取成功: {access_token[:20]}...")
    
    # 2. 测试不同的消息格式
    print("\n2. 测试消息格式...")
    
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 接收者ID
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 尝试不同的格式
    test_formats = [
        {
            "name": "格式1: 带receive_id_type",
            "data": {
                "receive_id": receive_id,
                "receive_id_type": "open_id",
                "msg_type": "text",
                "content": json.dumps({"text": "测试消息格式1"})
            }
        },
        {
            "name": "格式2: 不带receive_id_type",
            "data": {
                "receive_id": receive_id,
                "msg_type": "text", 
                "content": json.dumps({"text": "测试消息格式2"})
            }
        },
        {
            "name": "格式3: 使用user_id类型",
            "data": {
                "receive_id": receive_id,
                "receive_id_type": "user_id",
                "msg_type": "text",
                "content": json.dumps({"text": "测试消息格式3"})
            }
        },
        {
            "name": "格式4: 查看API文档示例",
            "data": {
                "receive_id": receive_id,
                "msg_type": "text",
                "content": '{"text":"测试消息格式4"}'
            }
        }
    ]
    
    for test in test_formats:
        print(f"\n   📤 测试: {test['name']}")
        print(f"      数据: {json.dumps(test['data'], ensure_ascii=False)}")
        
        try:
            response = requests.post(message_url, headers=headers, json=test['data'], timeout=10)
            print(f"      状态码: {response.status_code}")
            print(f"      响应: {response.text[:200]}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print(f"      ✅ 成功! 消息ID: {result['data']['message_id']}")
                else:
                    print(f"      ❌ 失败: {result.get('msg')}")
            else:
                print(f"      ❌ HTTP错误")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    # 3. 查看飞书API文档
    print("\n3. 飞书API文档参考:")
    print("""
根据飞书官方文档:
https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create

请求体格式:
{
  "receive_id": "ou_7d8a6e6df7621556ef0e7ad51fxxxxxx",
  "msg_type": "text",
  "content": "{\\"text\\":\\"test content\\"}"
}

注意: 文档示例中没有receive_id_type字段!
可能receive_id_type是可选参数，或者通过其他方式确定。
""")
    
    return True

def check_user_info():
    """检查用户信息"""
    print("\n🔍 检查用户信息")
    print("=" * 50)
    
    print("""
可能的问题:
1. ou_7c53b4d00420faa89d6750f31c5d6ced 是open_id吗?
2. 需要确认用户ID的类型

检查方法:
1. 使用飞书API获取用户信息
2. 确认ID类型
3. 使用正确的receive_id_type
""")
    
    return True

def main():
    print("🎯 飞书消息格式测试")
    print("=" * 50)
    
    test_api_format()
    check_user_info()
    
    print("\n" + "=" * 50)
    print("🎯 发现的问题")
    print("=" * 50)
    
    print("""
关键发现:
1. 飞书API文档示例中没有receive_id_type字段
2. 错误信息说需要receive_id_type，但文档没有
3. 可能ou_7c53b4d00420faa89d6750f31c5d6ced不是open_id

解决方案:
1. 尝试去掉receive_id_type字段
2. 尝试使用其他ID类型(user_id, union_id等)
3. 先获取用户信息确认ID类型
""")
    
    return True

if __name__ == "__main__":
    main()