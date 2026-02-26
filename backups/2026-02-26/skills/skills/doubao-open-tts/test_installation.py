#!/usr/bin/env python3
"""
测试Doubao TTS技能安装
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_installation():
    print("🧪 测试Doubao TTS技能安装")
    print("=" * 50)
    
    # 1. 检查文件是否存在
    required_files = [
        "SKILL.md",
        "README.md",
        "_meta.json",
        "requirements.txt",
        ".env.example",
        "scripts/tts.py",
        "scripts/test_tts.py"
    ]
    
    print("📁 检查文件结构:")
    all_files_exist = True
    for file in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        exists = os.path.exists(file_path)
        print(f"  {'✅' if exists else '❌'} {file}")
        if not exists:
            all_files_exist = False
    
    print(f"\n文件检查: {'✅ 全部通过' if all_files_exist else '❌ 部分文件缺失'}")
    
    # 2. 检查Python模块
    print("\n🐍 检查Python依赖:")
    try:
        import requests
        print(f"  ✅ requests {requests.__version__}")
    except ImportError:
        print("  ❌ requests 未安装")
        print("  运行: pip install requests")
    
    # 3. 检查技能配置
    print("\n⚙️ 检查技能配置:")
    try:
        from scripts.tts import check_api_config
        config = check_api_config()
        if config:
            print(f"  ✅ API配置已设置")
            print(f"    App ID: {config.get('app_id', '未设置')}")
            print(f"    Access Token: {config.get('access_token', '未设置')[:10]}...")
            print(f"    Secret Key: {config.get('secret_key', '未设置')[:10]}...")
        else:
            print("  ℹ️ API配置未设置")
            print("  请编辑 .env 文件或使用 setup_api_config() 设置")
    except Exception as e:
        print(f"  ❌ 检查配置时出错: {e}")
    
    # 4. 显示技能信息
    print("\n📋 技能信息:")
    try:
        with open(os.path.join(os.path.dirname(__file__), "SKILL.md"), "r", encoding="utf-8") as f:
            content = f.read()
            # 提取YAML frontmatter
            import re
            match = re.search(r'^---\n([\s\S]*?)\n---', content)
            if match:
                frontmatter = match.group(1)
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        print(f"  {key.strip()}: {value.strip()}")
    except Exception as e:
        print(f"  ❌ 读取技能信息失败: {e}")
    
    # 5. 使用说明
    print("\n🚀 使用说明:")
    print("=" * 50)
    print("1. 配置API:")
    print("   cp .env.example .env")
    print("   # 编辑 .env 文件，设置火山引擎API凭证")
    print()
    print("2. 安装依赖:")
    print("   pip install -r requirements.txt")
    print()
    print("3. 基本使用:")
    print("   from scripts.tts import VolcanoTTS")
    print("   tts = VolcanoTTS()")
    print("   tts.synthesize('你好，世界！', output_file='output.mp3')")
    print()
    print("4. 命令行使用:")
    print("   python scripts/tts.py '你好，世界！' --output test.mp3")
    print()
    print("5. 查看可用音色:")
    print("   python scripts/tts.py --list-voices")
    print("=" * 50)
    
    return all_files_exist

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)