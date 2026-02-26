#!/usr/bin/env python3
"""
模拟OpenClaw发送语音消息的完整流程
"""

import requests
import json
import os

def simulate_openclaw_flow():
    """模拟OpenClaw的完整流程"""
    print("🔧 模拟OpenClaw发送流程")
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
    
    # 2. 上传文件（模拟OpenClaw）
    print("\n2. 上传文件（模拟OpenClaw）...")
    
    file_path = "test_output_1.mp3"
    file_name = os.path.basename(file_path)
    
    upload_url = f"{base_url}/im/v1/files"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # OpenClaw使用 file_type: "opus"
    with open(file_path, 'rb') as f:
        files = {
            "file_type": (None, "opus"),
            "file_name": (None, file_name),
            "duration": (None, "5250"),  # 音频时长
            "file": (file_name, f, "audio/mpeg")
        }
        
        print(f"   上传文件: {file_name}")
        print(f"   file_type: opus")
        print(f"   duration: 5250ms")
        
        response = requests.post(upload_url, headers=headers, files=files, timeout=30)
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                file_key = result["data"]["file_key"]
                print(f"   ✅ 上传成功，file_key: {file_key[:20]}...")
            else:
                print(f"   ❌ 上传失败: {result}")
                return False
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    
    # 3. 发送消息（模拟OpenClaw）
    print("\n3. 发送消息（模拟OpenClaw）...")
    
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 尝试不同的消息类型
    test_cases = [
        {
            "name": "方法A: msg_type = 'file' (OpenClaw方式)",
            "msg_type": "file",
            "content": {"file_key": file_key}
        },
        {
            "name": "方法B: msg_type = 'audio' (语音消息)",
            "msg_type": "audio", 
            "content": {"file_key": file_key, "duration": 5250}
        },
        {
            "name": "方法C: 不带receive_id_type",
            "msg_type": "audio",
            "content": {"file_key": file_key, "duration": 5250},
            "no_receive_id_type": True
        }
    ]
    
    for test in test_cases:
        print(f"\n   📤 测试: {test['name']}")
        
        data = {
            "receive_id": receive_id,
            "msg_type": test["msg_type"],
            "content": json.dumps(test["content"], ensure_ascii=False)
        }
        
        # 添加receive_id_type（除非测试C）
        if not test.get("no_receive_id_type", False):
            data["receive_id_type"] = "open_id"
        
        print(f"       数据: {json.dumps(data, ensure_ascii=False)}")
        
        try:
            response = requests.post(message_url, headers=headers, json=data, timeout=10)
            print(f"       状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print(f"       ✅ 成功! 消息ID: {result['data']['message_id']}")
                    print(f"       🎯 正确的方法是: {test['name']}")
                    return test
                else:
                    print(f"       ❌ 失败: {result.get('msg')}")
            else:
                print(f"       ❌ HTTP错误")
                print(f"       响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"       ❌ 异常: {e}")
    
    # 4. 分析可能的原因
    print("\n4. 分析可能的原因...")
    print("""
可能的问题:
1. 应用权限虽然开通，但尚未生效
2. 需要等待几分钟让权限生效
3. 可能需要重新登录或刷新token
4. 飞书API版本问题

建议:
1. 等待5-10分钟让权限生效
2. 尝试使用OpenClaw的message工具发送文件
3. 检查飞书应用的实际权限状态
""")
    
    return None

def check_permission_status():
    """检查权限状态"""
    print("\n🔐 检查权限生效状态")
    print("=" * 50)
    
    print("""
飞书权限生效流程:
1. 在开放平台添加权限
2. 创建新版本
3. 提交审核（企业自建应用通常自动通过）
4. 发布版本
5. 等待生效（通常几分钟）

检查方法:
1. 访问: https://open.feishu.cn/
2. 进入应用管理
3. 查看"版本管理与发布"
4. 确认最新版本已发布
5. 查看"权限管理"确认权限已开启

如果已发布但仍然失败:
1. 等待5-10分钟
2. 尝试重新获取access_token
3. 检查是否有其他限制
""")
    
    return True

def main():
    print("🎯 模拟OpenClaw发送语音消息")
    print("=" * 50)
    
    # 模拟OpenClaw流程
    success_method = simulate_openclaw_flow()
    
    # 检查权限状态
    check_permission_status()
    
    print("\n" + "=" * 50)
    print("🎯 基于模拟的发现")
    print("=" * 50)
    
    if success_method:
        print(f"""
✅ 找到了成功的方法: {success_method['name']}

关键参数:
- msg_type: {success_method['msg_type']}
- receive_id_type: {"open_id" if not success_method.get('no_receive_id_type') else "无"}
- content: {json.dumps(success_method['content'], indent=2)}

立即使用这个方法发送语音消息!
""")
    else:
        print("""
❌ 所有方法都失败了

可能的原因和解决方案:

1. **权限尚未生效**
   - 等待5-10分钟
   - 确认应用已发布

2. **使用OpenClaw的message工具**
   - 虽然显示为文件附件，但功能可用
   - 等待权限生效后再尝试API

3. **临时解决方案**
   - 发送文本描述 + 文件附件
   - 说明这是语音内容

建议:
1. 先使用message工具发送文件附件
2. 等待权限完全生效
3. 稍后尝试真正的语音消息API
""")
    
    return True

if __name__ == "__main__":
    main()