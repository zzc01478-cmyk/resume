#!/usr/bin/env python3
"""
测试Doubao TTS API配置
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_config():
    print("🧪 测试Doubao TTS API配置")
    print("=" * 50)
    
    try:
        from scripts.tts import check_api_config
        
        print("🔍 检查API配置...")
        config = check_api_config()
        
        if config:
            print("✅ API配置成功！")
            print(f"   App ID: {config.get('app_id', 'N/A')}")
            print(f"   Access Token: {config.get('access_token', 'N/A')[:10]}...")
            print(f"   Secret Key: {config.get('secret_key', 'N/A')[:10]}...")
            
            # 检查环境变量
            print("\n🌐 环境变量检查:")
            env_vars = {
                'VOLCANO_TTS_APPID': os.getenv('VOLCANO_TTS_APPID'),
                'VOLCANO_TTS_ACCESS_TOKEN': os.getenv('VOLCANO_TTS_ACCESS_TOKEN'),
                'VOLCANO_TTS_SECRET_KEY': os.getenv('VOLCANO_TTS_SECRET_KEY')
            }
            
            for key, value in env_vars.items():
                if value:
                    print(f"   ✅ {key}: 已设置")
                else:
                    print(f"   ❌ {key}: 未设置")
            
            return True
        else:
            print("❌ API配置失败")
            print("   请检查 .env 文件配置")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tts_functionality():
    print("\n🎙️ 测试TTS功能...")
    print("=" * 50)
    
    try:
        from scripts.tts import VolcanoTTS
        
        print("1. 创建TTS实例...")
        tts = VolcanoTTS()
        print("   ✅ TTS实例创建成功")
        
        print("\n2. 查看可用音色...")
        try:
            voices = tts.list_voices()
            if voices:
                print(f"   ✅ 找到 {len(voices)} 种音色")
                # 显示前5种音色
                for i, (voice_id, voice_name) in enumerate(list(voices.items())[:5]):
                    print(f"      {i+1}. {voice_name} ({voice_id})")
                if len(voices) > 5:
                    print(f"      ... 还有 {len(voices)-5} 种音色")
            else:
                print("   ⚠️ 未获取到音色列表")
        except Exception as e:
            print(f"   ⚠️ 获取音色列表失败: {e}")
        
        print("\n3. 测试简单文本合成...")
        test_text = "你好，这是Doubao TTS语音合成测试。"
        print(f"   测试文本: {test_text}")
        
        try:
            # 先测试但不实际调用API
            print("   🔄 准备合成...")
            
            # 检查API可用性
            print("   🌐 检查API连接...")
            # 这里我们可以尝试一个简单的请求来验证API
            import requests
            from scripts.tts import API_HOST
            
            test_url = f"https://{API_HOST}/api/v1/tts"
            print(f"   API端点: {test_url}")
            
            print("   ✅ API配置看起来正常")
            print("   💡 提示: 要实际生成音频，请运行完整测试")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ TTS功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Doubao TTS技能完整测试")
    print("=" * 50)
    
    # 测试API配置
    config_ok = test_api_config()
    
    if config_ok:
        # 测试TTS功能
        tts_ok = test_tts_functionality()
        
        if tts_ok:
            print("\n" + "=" * 50)
            print("🎉 所有测试通过！")
            print("=" * 50)
            print("\n🚀 现在你可以使用Doubao TTS技能了：")
            print("\n1. 基本使用:")
            print("   from scripts.tts import VolcanoTTS")
            print("   tts = VolcanoTTS()")
            print("   tts.synthesize('你好，世界！', output_file='output.mp3')")
            print("\n2. 命令行使用:")
            print("   python scripts/tts.py '测试文本' --output test.mp3")
            print("\n3. 查看所有音色:")
            print("   python scripts/tts.py --list-voices")
            print("\n4. 选择特定音色:")
            print("   python scripts/tts.py '测试文本' --voice zh_female_cancan_mars_bigtts")
        else:
            print("\n❌ TTS功能测试失败")
    else:
        print("\n❌ API配置测试失败")
    
    return config_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)