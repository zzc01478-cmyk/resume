#!/usr/bin/env python3
"""
测试关键发现：receive_id_type应该通过params传递
"""

import requests
import json

def test_params_fix():
    """测试params传递receive_id_type"""
    print("🔧 测试关键发现：receive_id_type通过params传递")
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
    
    # 2. 测试文本消息（验证基本功能）
    print("\n2. 测试文本消息（验证params方式）...")
    
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 使用params传递receive_id_type（根据OpenClaw源码）
    params = {"receive_id_type": "open_id"}
    data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": "测试params传递receive_id_type"})
    }
    
    print(f"   📤 发送测试消息")
    print(f"      params: {json.dumps(params)}")
    print(f"      data: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            message_url,
            headers=headers,
            params=params,
            json=data,
            timeout=10
        )
        
        print(f"      状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"      ✅ 成功! 消息ID: {result['data']['message_id']}")
                print(f"      🎯 验证成功: receive_id_type应该通过params传递!")
                return True
            else:
                print(f"      ❌ 失败: {result.get('msg')}")
                print(f"      错误代码: {result.get('code')}")
                print(f"      完整响应: {result}")
        else:
            print(f"      ❌ HTTP错误")
            print(f"      响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"      ❌ 异常: {e}")
    
    return False

def update_direct_sender():
    """更新直接发送器，使用params传递receive_id_type"""
    print("\n🔄 更新直接发送器使用params方式")
    print("=" * 60)
    
    print("""
需要修改 direct_feishu_audio.py:

原代码（错误）:
data = {
    "receive_id": receive_id,
    "receive_id_type": receive_id_type,  # ❌ 在data中
    "msg_type": "audio",
    "content": json.dumps(content)
}

新代码（正确）:
params = {"receive_id_type": receive_id_type}  # ✅ 在params中
data = {
    "receive_id": receive_id,
    "msg_type": "audio",
    "content": json.dumps(content)
}

然后调用:
response = requests.post(
    url,
    headers=headers,
    params=params,  # ✅ 传递params
    json=data,
    timeout=10
)
""")
    
    return True

def create_fixed_sender():
    """创建修复后的发送器"""
    print("\n🚀 创建修复后的直接发送器")
    print("=" * 60)
    
    fixed_code = '''
def _send_audio_message_direct_fixed(self, receive_id: str, file_key: str, duration_ms: int) -> Tuple[bool, Optional[str]]:
    """
    修复版：使用params传递receive_id_type
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
    else:
        receive_id_type = "open_id"  # 默认
    
    # ✅ 关键修复：使用params传递receive_id_type
    params = {"receive_id_type": receive_id_type}
    data = {
        "receive_id": receive_id,
        "msg_type": "audio",
        "content": json.dumps(content, ensure_ascii=False)
    }
    
    print(f"📤 发送语音消息（修复版）...")
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
                return False, f"{error_code}: {error_msg}"
        else:
            error_text = response.text[:500]
            print(f"   ❌ HTTP错误: {response.status_code}")
            print(f"   响应: {error_text}")
            return False, f"HTTP {response.status_code}: {error_text}"
            
    except Exception as e:
        print(f"   ❌ 发送消息异常: {e}")
        return False, str(e)
'''
    
    print(fixed_code)
    
    return True

def main():
    print("🎯 修复飞书API调用方式")
    print("=" * 60)
    
    # 测试params方式
    success = test_params_fix()
    
    if success:
        # 更新发送器
        update_direct_sender()
        
        # 创建修复后的发送器
        create_fixed_sender()
    else:
        print("\n❌ 测试失败，权限问题仍然存在")
        print("""
可能的原因:
1. 应用权限 im:message:send 未生效
2. 需要等待权限生效
3. 需要发布新版本

建议:
1. 检查飞书应用权限配置
2. 确认已发布新版本
3. 等待5-30分钟让权限生效
""")
    
    print("\n" + "=" * 60)
    print("🎯 总结")
    print("=" * 60)
    
    if success:
        print("""
✅ 找到了关键问题:
receive_id_type 应该通过 params 传递，而不是 data!

下一步:
1. 更新 direct_feishu_audio.py 使用params方式
2. 重新测试发送语音消息
3. 发送真正的语音消息气泡
""")
    else:
        print("""
❌ 权限问题仍然存在

即使修复了API调用方式，权限问题也需要解决:

1. 确认飞书应用权限 im:message:send 已开启
2. 确认已创建并发布新版本
3. 等待权限生效（5-30分钟）
4. 然后使用修复后的API调用方式
""")
    
    return success

if __name__ == "__main__":
    main()