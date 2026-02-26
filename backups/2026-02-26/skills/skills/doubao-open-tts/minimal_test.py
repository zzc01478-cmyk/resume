#!/usr/bin/env python3
"""
最小测试：验证飞书API是否正常工作
"""

import requests
import json
import time

def minimal_test():
    """最小可行性测试"""
    print("🔬 最小可行性测试")
    print("=" * 50)
    
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
    
    # 2. 尝试最简单的API调用：获取应用信息
    print("\n2. 测试API连通性...")
    
    # 尝试获取应用信息（不需要特殊权限）
    app_info_url = f"{base_url}/application/v6/app"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(app_info_url, headers=headers, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"   ✅ API连通正常")
                app_name = result.get("data", {}).get("name", "未知")
                print(f"   应用名称: {app_name}")
            else:
                print(f"   ❌ 应用信息错误: {result.get('msg')}")
        else:
            print(f"   ❌ HTTP错误")
            print(f"   响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 3. 测试发送消息权限
    print("\n3. 测试发送消息权限...")
    
    message_url = f"{base_url}/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 使用最简单的文本消息测试
    receive_id = "ou_7c53b4d00420faa89d6750f31c5d6ced"
    
    # 尝试飞书文档中的标准格式
    test_data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": "测试消息权限"})
    }
    
    print(f"   发送测试消息...")
    print(f"   数据: {json.dumps(test_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(message_url, headers=headers, json=test_data, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"   ✅ 消息发送成功!")
                print(f"   消息ID: {result['data']['message_id']}")
                return True
            else:
                print(f"   ❌ 消息发送失败: {result.get('msg')}")
                print(f"   错误代码: {result.get('code')}")
                
                # 分析错误
                if result.get("code") == 99992402:
                    print(f"   🔍 错误分析: 权限验证失败")
                    print(f"      可能原因:")
                    print(f"      1. 应用没有发送消息的权限")
                    print(f"      2. 权限尚未生效")
                    print(f"      3. 需要发布新版本")
                elif result.get("code") == 99991401:
                    print(f"   🔍 错误分析: 无权限")
                    print(f"      需要权限: im:message:send")
                else:
                    print(f"   🔍 错误分析: 未知错误")
                    
        else:
            print(f"   ❌ HTTP错误")
            print(f"   响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    return False

def analyze_permission_issue():
    """分析权限问题"""
    print("\n🔍 权限问题分析")
    print("=" * 50)
    
    print("""
错误代码 99992402 的可能原因:

1. **权限未生效**
   - 虽然添加了权限，但尚未发布新版本
   - 发布后需要等待生效（通常几分钟）

2. **权限配置错误**
   - 缺少必需的权限: im:message:send
   - 权限范围不正确

3. **应用状态问题**
   - 应用未启用
   - 应用被限制

4. **API调用问题**
   - 参数格式不正确
   - 使用了错误的API版本

检查步骤:
1. 访问: https://open.feishu.cn/
2. 进入应用管理
3. 检查"权限管理" → 确保 im:message:send 已开启
4. 检查"版本管理与发布" → 确保已创建并发布新版本
5. 等待5-10分钟让权限生效
""")
    
    return True

def create_workaround():
    """创建临时解决方案"""
    print("\n🔄 临时解决方案")
    print("=" * 50)
    
    print("""
如果权限问题无法立即解决，可以:

方案A: 使用OpenClaw内置功能
   虽然显示为文件附件，但:
   - ✅ 音频内容正确
   - ✅ 可以播放
   - ✅ 功能实现

方案B: 等待权限生效
   1. 确认权限已配置并发布
   2. 等待5-30分钟
   3. 重新测试

方案C: 联系支持
   如果权限配置正确但仍然失败
""")
    
    return True

def main():
    print("🎯 飞书语音消息发送 - 最小可行性测试")
    print("=" * 50)
    
    # 运行最小测试
    success = minimal_test()
    
    if not success:
        # 分析权限问题
        analyze_permission_issue()
        
        # 创建临时解决方案
        create_workaround()
    
    print("\n" + "=" * 50)
    print("🎯 测试结果")
    print("=" * 50)
    
    if success:
        print("""
✅ 测试成功! 权限已生效。

下一步:
1. 使用完整的语音消息API
2. 发送真正的语音消息气泡
""")
    else:
        print("""
❌ 测试失败: 权限问题

建议:
1. 检查并确认飞书应用权限配置
2. 等待权限生效（5-30分钟）
3. 在此期间使用文件附件方案
""")
    
    return success

if __name__ == "__main__":
    main()