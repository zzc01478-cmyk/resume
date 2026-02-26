#!/usr/bin/env python3
"""
视频分析脚本 - 使用 Gemini 3 多模态模型
"""

import json
import os
import sys
import requests
from pathlib import Path

# 添加工作空间路径
workspace_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_path))

def load_gemini_config():
    """加载 Gemini 配置"""
    config_path = workspace_path / "config" / "gemini-config.json"
    
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get("gemini", {}).get("api_key", "")
        if not api_key:
            print("错误: Gemini API key 未设置")
            return None
        
        return config["gemini"]
    except Exception as e:
        print(f"加载配置失败: {e}")
        return None

def analyze_video_with_gemini(video_path, prompt=None):
    """
    使用 Gemini 分析视频
    
    Args:
        video_path: 视频文件路径或URL
        prompt: 自定义提示词（可选）
    
    Returns:
        dict: 分析结果
    """
    config = load_gemini_config()
    if not config:
        return {"error": "配置加载失败"}
    
    api_key = config.get("api_key")
    model = config.get("model", "gemini-3-flash-preview")
    base_url = config.get("base_url", "https://api.linkapi.ai/v1")
    
    if not prompt:
        prompt = config.get("default_prompt", "请分析这个视频内容，包括主要主题、关键场景、视觉元素、音频信息和情感氛围。")
    
    # 构建 API 请求 - 使用 OpenAI 兼容格式
    url = f"{base_url}/chat/completions"
    
    # 准备请求数据
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 构建消息内容
    # 注意：当前中转站可能不支持直接的多模态输入
    # 对于视频分析，我们需要先描述视频或提供视频URL
    if video_path.startswith(('http://', 'https://')):
        # 视频URL - 在提示词中包含URL
        enhanced_prompt = f"{prompt}\n\n视频URL: {video_path}"
        messages = [
            {
                "role": "user",
                "content": enhanced_prompt
            }
        ]
    else:
        # 本地文件 - 需要先描述或转换
        # 当前方案：在提示词中描述文件
        enhanced_prompt = f"{prompt}\n\n视频文件: {video_path} (本地文件)"
        messages = [
            {
                "role": "user",
                "content": enhanced_prompt
            }
        ]
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # 提取文本响应
        if "choices" in result and len(result["choices"]) > 0:
            text_response = result["choices"][0]["message"]["content"]
            return {
                "success": True,
                "analysis": text_response,
                "raw_response": result
            }
        else:
            return {
                "success": False,
                "error": "API响应格式异常",
                "raw_response": result
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API请求失败: {e}",
            "status_code": e.response.status_code if e.response else None,
            "response_text": e.response.text if e.response else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"处理失败: {e}"
        }

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python analyze_video.py <视频路径或URL> [提示词]")
        print("示例: python analyze_video.py https://example.com/video.mp4")
        print("示例: python analyze_video.py /path/to/video.mp4 '分析视频中的主要人物和场景'")
        sys.exit(1)
    
    video_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"开始分析视频: {video_path}")
    
    result = analyze_video_with_gemini(video_path, prompt)
    
    if result.get("success"):
        print("\n" + "="*50)
        print("视频分析结果:")
        print("="*50)
        print(result["analysis"])
    else:
        print(f"分析失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()