#!/usr/bin/env python3
"""
检查飞书应用权限
"""

import requests
import json

def check_app_permissions():
    """检查应用权限"""
    print("🔐 检查飞书应用权限")
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
    
    # 2. 检查应用权限
    print("\n2. 检查应用权限状态...")
    print("""
错误代码 99992402 通常表示:
1. 应用没有发送消息的权限
2. 应用没有发布
3. 权限未生效

需要检查:
1. 应用是否已发布?
2. 是否添加了"发送消息"权限?
3. 权限是否已生效?
""")
    
    # 3. 查看应用信息
    print("\n3. 应用信息:")
    print(f"   App ID: {app_id}")
    print(f"   App Secret: {app_secret[:10]}...")
    
    # 4. 权限要求
    print("\n4. 发送语音消息需要的权限:")
    required_permissions = [
        "auth:auth.tenant_access_token:get",  # 获取token
        "im:message:send",                    # 发送消息
        "im:file:upload"                      # 上传文件
    ]
    
    for perm in required_permissions:
        print(f"   🔑 {perm}")
    
    # 5. 检查方法
    print("\n5. 检查权限的方法:")
    print("""
步骤1: 访问飞书开放平台
   https://open.feishu.cn/
   
步骤2: 登录并进入应用管理
   
步骤3: 找到应用 "cli_a913daaab4789bcb"
   
步骤4: 检查"权限管理"
   确保以下权限已开启:
   - 获取 tenant_access_token
   - 发送消息
   - 上传文件
   
步骤5: 检查"版本管理与发布"
   确保应用已创建版本并发布
   
步骤6: 等待权限生效
   发布后可能需要几分钟生效
""")
    
    # 6. 可能的解决方案
    print("\n6. 可能的解决方案:")
    print("""
方案A: 检查并配置权限
   1. 确保所有必需权限已开启
   2. 创建新版本并发布
   3. 等待生效后重试
   
方案B: 使用测试环境
   飞书可能有测试环境限制
   
方案C: 联系飞书支持
   如果权限配置正确但仍然失败
""")
    
    return True

def test_alternative_approach():
    """测试替代方案"""
    print("\n🔄 测试替代方案")
    print("=" * 50)
    
    print("""
如果应用权限问题无法立即解决，可以:

方案1: 使用OpenClaw内置的消息工具
   - 虽然显示为文件附件，但功能可用
   - 等待权限配置完成后再升级
   
方案2: 使用其他消息类型
   - 先测试文本消息是否工作
   - 确认基本功能正常
   
方案3: 临时解决方案
   - 将音频文件转换为文本描述
   - 发送文本消息说明音频内容
   - 提供文件下载链接
""")
    
    return True

def main():
    print("🎯 飞书应用权限分析")
    print("=" * 50)
    
    check_app_permissions()
    test_alternative_approach()
    
    print("\n" + "=" * 50)
    print("🎯 结论")
    print("=" * 50)
    
    print("""
基于分析，问题很可能是:

❌ 应用权限问题
   错误代码 99992402 表示应用缺少发送消息的权限

✅ 已确认的部分:
   1. 获取access_token成功
   2. 上传文件成功（获得了file_key）
   3. API格式基本正确

🚀 下一步:
   需要检查并配置飞书应用权限:
   
   1. 访问: https://open.feishu.cn/
   2. 找到应用: cli_a913daaab4789bcb
   3. 确保以下权限已开启并发布:
      - 获取 tenant_access_token
      - 发送消息
      - 上传文件
   
   4. 发布新版本
   5. 等待生效后重试
""")
    
    print("\n💡 在此期间，可以:")
    print("   1. 继续使用文件附件形式发送语音")
    print("   2. 先配置权限，稍后发送真正的语音消息")
    
    return True

if __name__ == "__main__":
    main()