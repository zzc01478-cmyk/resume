#!/usr/bin/env python3
"""
快速测试Doubao TTS语音合成
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    print("🚀 Doubao TTS快速测试")
    print("=" * 50)
    
    try:
        from scripts.tts import VolcanoTTS
        
        # 创建TTS实例
        tts = VolcanoTTS()
        
        # 测试文本
        test_texts = [
            "你好，这是Doubao TTS语音合成测试。",
            "欢迎使用火山引擎语音合成服务。",
            "语音合成技术让文字变得有声有色。"
        ]
        
        for i, text in enumerate(test_texts):
            print(f"\n🎯 测试 {i+1}: {text}")
            
            output_file = f"test_output_{i+1}.mp3"
            
            try:
                print(f"   🔄 合成中...")
                result = tts.synthesize(
                    text=text,
                    output_file=output_file,
                    voice_type="zh_female_cancan_mars_bigtts",  # 使用默认音色
                    speed=1.0,
                    volume=1.0
                )
                
                if result and os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"   ✅ 合成成功！")
                    print(f"      文件: {result}")
                    print(f"      大小: {file_size} 字节")
                    print(f"      时长: 约 {len(text) * 0.5:.1f} 秒")
                else:
                    print(f"   ❌ 合成失败")
                    
            except Exception as e:
                print(f"   ❌ 合成错误: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("📋 测试总结:")
        print("=" * 50)
        
        # 检查生成的文件
        test_files = [f"test_output_{i+1}.mp3" for i in range(len(test_texts))]
        
        for file in test_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"✅ {file}: {size} 字节")
            else:
                print(f"❌ {file}: 文件未生成")
        
        print("\n🎉 测试完成！")
        print("💡 提示: 生成的MP3文件可以在当前目录找到")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)