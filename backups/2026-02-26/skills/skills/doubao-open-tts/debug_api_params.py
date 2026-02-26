#!/usr/bin/env python3
"""
调试飞书API参数，找出正确的调用方式
"""

import requests
import json

def debug_api_parameters():
    """调试API参数"""
    print("🔧 调试飞书API参数")
    print("=" * 60)
    
    # 配置
    app_id = "cli_a913daaab4789bcb"
    app_secret = "TjRmP8aMFTTERjPqVDXsbffEsTuA6GPc"
    base_url = "https://open.feishu.cn/open-apis"
    
    # 1. 获取token
    print("1. 获取access_token...")
    token_url = f"{base_url}/auth/v3/tenant_access_token/internal"
    response = requests.post(token_url, json={"app_id": app_id, "app_secret": app_secret})
    
    if response.status_code != 200:
        print(f"   ❌ HTTP错误: {response.status_code}")
        return False
    
    token_data = response.json()
    if token_data.get("code") != 0:
        print(f"   ❌ Token错误: {token_data}")
        return False
    
    access_token = token_data["tenant_access_token"]
    print(f"   ✅ 获取成功")
    
    # 2. 尝试不同的参数组合
    print("\n2. 尝试不同的参数组合...")
    
    message_url = f"{self.base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "测试1: 使用params传递receive_id_type",
            "params": {"receive_id_type": "open_id"},
            "data": {
                "receive_id": receive_id,
                "msg_type": "text",
                "content": json.dumps({"text": "测试params方式"})
            }
        },
        {
            "name": "测试2: 在data中传递receive_id_type",
            "params": {},
            "data": {
                "receive_id": receive_id,
                "receive_id_type": "open_id",
                "msg_type": "text",
                "content": json.dumps({"text": "测试data方式"})
            }
        },
        {
            "name": "测试3: 使用query参数",
            "params": {"receive_id_type": "open_id"},
            "data": {
                "receive_id": receive_id,
                "msg_type": "text",
                "content": json.dumps({"text": "测试query方式"})
            }
        },
        {
            "name": "测试4: 查看OpenClaw源码调用方式",
            "params": {},
            "data": {
                "receive_id": receive_id,
                "msg_type": "text",
                "content": json.dumps({"text": "测试源码方式"})
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n   📤 {test['name']}")
        print(f"      参数: {json.dumps(test['params'])}")
        print(f"      数据: {json.dumps(test['data'], ensure_ascii=False)}")
        
        try:
            # 尝试不同的调用方式
            if test['params']:
                # 使用params参数
                response = requests.post(
                    message_url,
                    headers=headers,
                    params=test['params'],
                    json=test['data'],
                    timeout=10
                )
            else:
                # 直接发送
                response = requests.post(
                    message_url,
                    headers=headers,
                    json=test['data'],
                    timeout=10
                )
            
            print(f"      状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print(f"      ✅ 成功! 消息ID: {result['data']['message_id']}")
                    print(f"      🎯 正确的调用方式: {test['name']}")
                    return test
                else:
                    print(f"      ❌ 失败: {result.get('msg')}")
                    print(f"      错误代码: {result.get('code')}")
            else:
                print(f"      ❌ HTTP错误")
                print(f"      响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    # 3. 查看OpenClaw实际如何调用
    print("\n3. 查看OpenClaw源码调用方式...")
    print("""
从 media.ts 源码看到:

const response = await client.im.message.create({
  params: { receive_id_type: receiveIdType },  // 注意：这里是params
  data: {
    receive_id: receiveId,
    content,
    msg_type: "file",
  },
});

关键发现:
1. receive_id_type 是通过 params 传递的，不是 data
2. 这可能就是问题所在！
""")
    
    return None

def test_with_params():
    """使用params传递receive_id_type"""
    print("\n🔄 测试使用params传递receive_id_type")
    print("=" * 60)
    
    # 配置
    app_id = "cli_a913daaab4789bcb"
    app_secret = "TjRmP8aMFTTERjPqVDXsbffEsTuA6GPc"
    base_url = "https://open.feishu.cn/open-apis"
    
    # 获取token
    token_url = f"{base_url}/auth/v3/tenant_access_token/internal"
    response = requests.post(token_url, json={"app_id": app_id, "app_secret": app_secret})
    
    if response.status_code != 200:
        print(f"❌ 获取token失败: {response.status_code}")
        return False
    
    token_data = response.json()
    if token_data.get("code") != 0:
        print(f"❌ Token错误: {token_data}")
        return False
    
    access_token = token_data["tenant_access_token"]
    
    # 测试使用params
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 使用params传递receive_id_type
    params = {"receive_id_type": "open_id"}
    data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": "测试params传递receive_id_type"})
    }
    
    print(f"📤 测试params方式")
    print(f"   params: {json.dumps(params)}")
    print(f"   data: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            message_url,
            headers=headers,
            params=params,
            json=data,
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"   ✅ 成功! 消息ID: {result['data']['message_id']}")
                print(f"   🎯 关键发现: receive_id_type应该通过params传递!")
                return True
            else:
                print(f"   ❌ 失败: {result.get('msg')}")
                print(f"   错误代码: {result.get('code')}")
                print(f"   完整响应: {result}")
        else:
            print(f"   ❌ HTTP错误")
            print(f"   响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    return False

def main():
    print("🎯 调试飞书API参数调用方式")
    print("=" * 60)
    
    # 调试参数
    debug_api_parameters()
    
    # 测试params方式
    test_with_params()
    
    print("\n" + "=" * 60)
    print("🎯 关键发现")
    print("=" * 60)
    
    print("""
基于OpenClaw源码分析:

✅ 关键发现:
receive_id_type 应该通过 params 传递，而不是 data!

错误的方式:
{
  "receive_id": "ou_xxx",
  "receive_id_type": "open_id",  # ❌ 在data中
  "msg_type": "audio",
  "content": "..."
}

正确的方式（根据OpenClaw源码）:
params: {"receive_id_type": "open_id"}  # ✅ 在params中
data: {
  "receive_id": "ou_xxx",
  "msg_type": "audio", 
  "content": "..."
}

这就是为什么一直失败的原因!
""")
    
    return True

if __name__ == "__main__":
    main()