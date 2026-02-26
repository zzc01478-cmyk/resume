#!/usr/bin/env python3
"""
豆包视频分析器测试脚本
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_video import VideoAnalyzer, analyze_video


def test_video_info_extraction():
    """测试视频信息提取"""
    print("=== 测试视频信息提取 ===")
    
    # 创建一个测试视频路径（这里需要实际存在的视频文件）
    test_video = "test_video.mp4"  # 替换为实际视频文件
    
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        print("请创建一个测试视频或使用现有视频")
        return
    
    try:
        analyzer = VideoAnalyzer(api_key=os.getenv("ARK_API_KEY"))
        video_info = analyzer.extract_video_info(test_video)
        
        print("视频信息:")
        print(json.dumps(video_info, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"提取视频信息失败: {e}")
        return False


def test_quick_analysis():
    """测试快速分析"""
    print("\n=== 测试快速分析 ===")
    
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        return False
    
    try:
        # 使用便捷函数
        result = analyze_video(
            video_path=test_video,
            prompt="请用一段话描述这个视频的主要内容",
            output_format="text"
        )
        
        print("快速分析结果:")
        print(result)
        
        return True
    except Exception as e:
        print(f"快速分析失败: {e}")
        return False


def test_detailed_analysis():
    """测试详细分析"""
    print("\n=== 测试详细分析 ===")
    
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        return False
    
    try:
        analyzer = VideoAnalyzer(api_key=os.getenv("ARK_API_KEY"))
        result = analyzer.analyze_detailed(test_video)
        
        print("详细分析结果 (Markdown格式):")
        print(result.to_markdown())
        
        # 保存到文件
        output_file = "video_analysis_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.to_markdown())
        
        print(f"\n分析报告已保存到: {output_file}")
        
        return True
    except Exception as e:
        print(f"详细分析失败: {e}")
        return False


def test_event_analysis():
    """测试事件分析"""
    print("\n=== 测试事件分析 ===")
    
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        return False
    
    try:
        analyzer = VideoAnalyzer(api_key=os.getenv("ARK_API_KEY"))
        events = analyzer.analyze_events(test_video)
        
        print("事件分析结果:")
        print(json.dumps(events, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"事件分析失败: {e}")
        return False


def test_custom_prompt():
    """测试自定义提示词"""
    print("\n=== 测试自定义提示词 ===")
    
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        return False
    
    custom_prompt = """请分析这个视频的技术特征：
1. 画面质量如何？
2. 色彩表现如何？
3. 光线使用是否恰当？
4. 构图有什么特点？
5. 给出改进建议。"""
    
    try:
        analyzer = VideoAnalyzer(api_key=os.getenv("ARK_API_KEY"))
        result = analyzer.analyze_with_prompt(test_video, custom_prompt)
        
        print("自定义提示词分析结果:")
        print(result)
        
        return True
    except Exception as e:
        print(f"自定义提示词分析失败: {e}")
        return False


def create_sample_video():
    """创建示例视频（用于测试）"""
    print("\n=== 创建示例视频 ===")
    
    try:
        import cv2
        import numpy as np
        
        # 创建一个简单的测试视频
        output_path = "test_sample_video.mp4"
        width, height = 640, 480
        fps = 30
        duration = 5  # 5秒
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for i in range(fps * duration):
            # 创建渐变背景
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 添加渐变
            for y in range(height):
                color_value = int(255 * y / height)
                frame[y, :, 0] = color_value  # 蓝色通道
                frame[y, :, 1] = 255 - color_value  # 绿色通道
                frame[y, :, 2] = 128  # 红色通道
            
            # 添加移动的矩形
            rect_size = 100
            x_pos = int((i / (fps * duration)) * (width - rect_size))
            y_pos = height // 2 - rect_size // 2
            
            cv2.rectangle(frame, 
                         (x_pos, y_pos), 
                         (x_pos + rect_size, y_pos + rect_size), 
                         (0, 255, 0), 
                         -1)
            
            # 添加文字
            cv2.putText(frame, "Test Video", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        
        print(f"示例视频已创建: {output_path}")
        print(f"大小: {os.path.getsize(output_path) / 1024:.1f} KB")
        
        return output_path
        
    except ImportError:
        print("需要OpenCV来创建示例视频: pip install opencv-python")
        return None
    except Exception as e:
        print(f"创建示例视频失败: {e}")
        return None


def main():
    """主测试函数"""
    print("豆包视频分析器测试")
    print("=" * 50)
    
    # 检查API Key
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("警告: 未设置ARK_API_KEY环境变量")
        print("请设置: export ARK_API_KEY='your_api_key_here'")
        print("或直接在代码中提供API Key")
    
    # 检查测试视频
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        print("1. 请放置一个测试视频文件到当前目录")
        print("2. 或者创建示例视频")
        
        choice = input("是否创建示例视频? (y/n): ")
        if choice.lower() == 'y':
            test_video = create_sample_video()
            if not test_video:
                print("无法继续测试")
                return
    
    if not os.path.exists(test_video):
        print("没有可用的测试视频，无法继续测试")
        return
    
    print(f"使用测试视频: {test_video}")
    print(f"文件大小: {os.path.getsize(test_video) / (1024*1024):.2f} MB")
    
    # 运行测试
    tests = [
        ("视频信息提取", test_video_info_extraction),
        ("快速分析", test_quick_analysis),
        ("详细分析", test_detailed_analysis),
        ("事件分析", test_event_analysis),
        ("自定义提示词", test_custom_prompt),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("-" * 50)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")


if __name__ == "__main__":
    main()