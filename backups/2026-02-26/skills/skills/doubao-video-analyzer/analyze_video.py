#!/usr/bin/env python3
"""
豆包视频分析器
使用火山引擎豆包大模型进行视频内容分析
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import base64

try:
    from openai import OpenAI
    import requests
    from PIL import Image
    import cv2
    import numpy as np
    from moviepy.editor import VideoFileClip
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请安装: pip install openai requests pillow opencv-python moviepy")
    raise

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VideoAnalysisResult:
    """视频分析结果"""
    summary: str
    scenes: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    objects: List[str]
    technical_analysis: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        md = f"""# 视频分析报告

## 内容摘要
{self.summary}

## 场景分析
"""
        for i, scene in enumerate(self.scenes, 1):
            md += f"{i}. **{scene.get('start_time', 'N/A')} - {scene.get('end_time', 'N/A')}**\n"
            md += f"   - 描述: {scene.get('description', 'N/A')}\n"
            if scene.get('objects'):
                md += f"   - 物体: {', '.join(scene['objects'])}\n"
            if scene.get('actions'):
                md += f"   - 动作: {', '.join(scene['actions'])}\n"
            md += "\n"
        
        if self.events:
            md += "## 关键事件\n"
            for event in self.events:
                md += f"- **{event.get('time', 'N/A')}**: {event.get('description', 'N/A')}"
                if event.get('importance'):
                    md += f" (重要性: {event['importance']})"
                md += "\n"
        
        if self.objects:
            md += f"\n## 识别物体\n{', '.join(self.objects)}\n"
        
        md += "\n## 技术分析\n"
        for key, value in self.technical_analysis.items():
            md += f"- **{key}**: {value}\n"
        
        md += f"\n## 元数据\n"
        for key, value in self.metadata.items():
            md += f"- **{key}**: {value}\n"
        
        return md


class VideoAnalyzer:
    """豆包视频分析器"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
        model: str = "doubao-seed-1-6-251015",
        timeout: int = 300
    ):
        """
        初始化视频分析器
        
        Args:
            api_key: 豆包API Key，如果为None则从环境变量ARK_API_KEY获取
            base_url: API基础URL
            model: 使用的模型
            timeout: 超时时间（秒）
        """
        self.api_key = api_key or os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("请提供API Key或设置环境变量ARK_API_KEY")
        
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        
        # 初始化OpenAI客户端（兼容格式）
        self.client = OpenAI(
            base_url=base_url,
            api_key=self.api_key,
            timeout=timeout
        )
        
        logger.info(f"视频分析器初始化完成，使用模型: {model}")
    
    def extract_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        提取视频基本信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            # 使用OpenCV获取视频信息
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            # 获取基本信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if fps > 0:
                duration = frame_count / fps
            else:
                duration = 0
            
            cap.release()
            
            # 使用moviepy获取更多信息
            try:
                clip = VideoFileClip(video_path)
                duration = clip.duration
                if hasattr(clip, 'audio') and clip.audio:
                    audio_info = {
                        "has_audio": True,
                        "audio_fps": clip.audio.fps,
                        "audio_nchannels": clip.audio.nchannels
                    }
                else:
                    audio_info = {"has_audio": False}
                clip.close()
            except Exception as e:
                logger.warning(f"使用moviepy获取音频信息失败: {e}")
                audio_info = {"has_audio": False}
            
            # 获取文件大小
            file_size = os.path.getsize(video_path)
            
            return {
                "width": width,
                "height": height,
                "fps": fps,
                "frame_count": frame_count,
                "duration": duration,
                "file_size": file_size,
                "file_size_mb": file_size / (1024 * 1024),
                "resolution": f"{width}x{height}",
                "audio_info": audio_info,
                "format": os.path.splitext(video_path)[1].lower()
            }
            
        except Exception as e:
            logger.error(f"提取视频信息失败: {e}")
            return {"error": str(e)}
    
    def upload_video(self, video_path: str) -> str:
        """
        上传视频文件到火山引擎
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            文件ID
        """
        try:
            logger.info(f"开始上传视频: {video_path}")
            
            # 检查文件大小（最大512MB）
            file_size = os.path.getsize(video_path)
            if file_size > 512 * 1024 * 1024:
                raise ValueError(f"视频文件过大: {file_size/(1024*1024):.2f}MB > 512MB")
            
            # 上传文件
            with open(video_path, "rb") as f:
                file_response = self.client.files.create(
                    file=f,
                    purpose="user_data"
                )
            
            file_id = file_response.id
            logger.info(f"视频上传成功，文件ID: {file_id}")
            
            # 等待文件处理完成
            max_wait_time = 300  # 最大等待5分钟
            wait_interval = 2    # 每2秒检查一次
            
            start_time = time.time()
            while time.time() - start_time < max_wait_time:
                file_info = self.client.files.retrieve(file_id)
                
                if file_info.status == "processed":
                    logger.info("视频处理完成")
                    return file_id
                elif file_info.status == "failed":
                    raise ValueError(f"视频处理失败: {file_info}")
                elif file_info.status == "error":
                    raise ValueError(f"视频处理错误: {file_info}")
                
                logger.info(f"视频处理中... 状态: {file_info.status}")
                time.sleep(wait_interval)
            
            raise TimeoutError("视频处理超时")
            
        except Exception as e:
            logger.error(f"上传视频失败: {e}")
            raise
    
    def analyze_with_prompt(
        self,
        video_path: str,
        prompt: str,
        stream: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        使用自定义提示词分析视频
        
        Args:
            video_path: 视频文件路径
            prompt: 分析提示词
            stream: 是否使用流式响应
            
        Returns:
            分析结果
        """
        try:
            # 上传视频
            file_id = self.upload_video(video_path)
            
            # 构建请求
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_video",
                            "file_id": file_id
                        },
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            logger.info(f"开始分析视频，提示词: {prompt[:100]}...")
            
            if stream:
                # 流式响应
                response = self.client.responses.create(
                    model=self.model,
                    input=messages,
                    stream=True
                )
                
                result_text = ""
                for event in response:
                    if event.type == "response.output_text.delta":
                        result_text += event.delta
                        print(event.delta, end="", flush=True)
                    elif event.type == "response.completed":
                        logger.info(f"分析完成，使用token: {event.response.usage}")
                
                return result_text
            else:
                # 非流式响应
                response = self.client.responses.create(
                    model=self.model,
                    input=messages,
                    stream=False
                )
                
                if response.output and response.output[0].content:
                    result_text = response.output[0].content[0].text
                    logger.info(f"分析完成，使用token: {response.usage}")
                    return result_text
                else:
                    raise ValueError("未收到有效响应")
                    
        except Exception as e:
            logger.error(f"分析视频失败: {e}")
            raise
    
    def analyze_detailed(self, video_path: str) -> VideoAnalysisResult:
        """
        执行详细视频分析
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频分析结果对象
        """
        try:
            # 提取视频信息
            video_info = self.extract_video_info(video_path)
            logger.info(f"视频信息: {video_info}")
            
            # 构建详细分析提示词
            prompt = """请对这个视频进行详细分析，包括以下内容：

1. **内容摘要**：用一段话概括视频的主要内容、主题和核心信息。

2. **场景分析**：按时间顺序分析视频中的各个场景，每个场景包括：
   - 开始时间和结束时间（HH:mm:ss格式）
   - 场景描述
   - 出现的物体
   - 发生的动作
   - 情感氛围

3. **关键事件**：提取视频中的关键事件，包括：
   - 发生时间
   - 事件描述
   - 重要性（高/中/低）

4. **识别物体**：列出视频中出现的主要物体。

5. **技术分析**：评价视频的：
   - 画面质量（清晰度、色彩、光线）
   - 音频质量（如果有）
   - 制作水平
   - 改进建议

请以结构化的方式输出分析结果。"""
            
            # 执行分析
            analysis_text = self.analyze_with_prompt(video_path, prompt, stream=False)
            
            # 解析分析结果（这里简化处理，实际可能需要更复杂的解析）
            # 在实际应用中，可以要求模型输出JSON格式，或者使用正则表达式解析
            
            # 创建分析结果对象
            result = VideoAnalysisResult(
                summary=self._extract_summary(analysis_text),
                scenes=self._extract_scenes(analysis_text),
                events=self._extract_events(analysis_text),
                objects=self._extract_objects(analysis_text),
                technical_analysis=self._extract_technical_analysis(analysis_text),
                metadata={
                    "video_info": video_info,
                    "analysis_time": datetime.now().isoformat(),
                    "model_used": self.model,
                    "video_path": video_path
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"详细分析失败: {e}")
            raise
    
    def analyze_summary(self, video_path: str) -> str:
        """
        快速摘要分析
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频摘要
        """
        prompt = "请用一段话概括这个视频的主要内容、主题和核心信息。"
        return self.analyze_with_prompt(video_path, prompt, stream=False)
    
    def analyze_events(self, video_path: str) -> List[Dict[str, Any]]:
        """
        分析视频事件时间线
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            事件列表
        """
        prompt = """请提取这个视频中的关键事件，以JSON格式输出，每个事件包括：
- time: 发生时间（HH:mm:ss格式）
- description: 事件描述
- importance: 重要性（高/中/低）
- involved: 涉及的人物或物体

请只输出JSON格式，不要有其他文字。"""
        
        result = self.analyze_with_prompt(video_path, prompt, stream=False)
        
        try:
            # 尝试解析JSON
            events = json.loads(result)
            if isinstance(events, list):
                return events
            else:
                return [events]
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            logger.warning("无法解析JSON，返回原始文本")
            return [{"description": result, "time": "N/A", "importance": "N/A"}]
    
    def _extract_summary(self, text: str) -> str:
        """从分析文本中提取摘要"""
        # 简化实现，实际可以使用更智能的提取方法
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if "内容摘要" in line or "摘要" in line or "概括" in line:
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        return text[:500] + "..." if len(text) > 500 else text
    
    def _extract_scenes(self, text: str) -> List[Dict[str, Any]]:
        """从分析文本中提取场景"""
        scenes = []
        lines = text.split('\n')
        
        current_scene = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测场景开始（简化实现）
            if "场景" in line and ("开始" in line or "时间" in line):
                if current_scene:
                    scenes.append(current_scene)
                
                # 提取时间信息
                import re
                time_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
                start_time = time_match.group(1) if time_match else "N/A"
                
                current_scene = {
                    "start_time": start_time,
                    "end_time": "N/A",
                    "description": "",
                    "objects": [],
                    "actions": []
                }
            elif current_scene and "描述" in line:
                current_scene["description"] = line.replace("描述:", "").strip()
            elif current_scene and ("物体" in line or "物品" in line):
                objects_text = line.replace("物体:", "").replace("物品:", "").strip()
                current_scene["objects"] = [obj.strip() for obj in objects_text.split(',') if obj.strip()]
            elif current_scene and ("动作" in line or "行为" in line):
                actions_text = line.replace("动作:", "").replace("行为:", "").strip()
                current_scene["actions"] = [action.strip() for action in actions_text.split(',') if action.strip()]
        
        if current_scene:
            scenes.append(current_scene)
        
        return scenes if scenes else [{"description": "无法提取详细场景信息", "start_time": "N/A", "end_time": "N/A"}]
    
    def _extract_events(self, text: str) -> List[Dict[str, Any]]:
        """从分析文本中提取事件"""
        events = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测事件行（简化实现）
            if ("事件" in line or "关键" in line) and "时间" in line:
                import re
                time_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
                time_str = time_match.group(1) if time_match else "N/A"
                
                # 提取描述
                desc_start = line.find(':')
                if desc_start == -1:
                    desc_start = line.find('：')
                
                description = line[desc_start+1:].strip() if desc_start != -1 else line
                
                # 提取重要性
                importance = "中"
                if "高" in line:
                    importance = "高"
                elif "低" in line:
                    importance = "低"
                
                events.append({
                    "time": time_str,
                    "description": description,
                    "importance": importance
                })
        
        return events if events else [{"time": "N/A", "description": "无法提取事件信息", "importance": "中"}]
    
    def _extract_objects(self, text: str) -> List[str]:
        """从分析文本中提取物体"""
        objects = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "物体" in line or "物品" in line or "物体:" in line or "物品:" in line:
                # 提取物体列表
                obj_text = line.replace("物体:", "").replace("物品:", "").strip()
                if obj_text:
                    # 尝试分割逗号、分号或空格
                    for sep in [',', '、', ';', '，']:
                        if sep in obj_text:
                            objects.extend([obj.strip() for obj in obj_text.split(sep) if obj.strip()])
                            break
                    else:
                        objects.append(obj_text)
        
        # 去重
        return list(set(objects)) if objects else ["无法提取物体信息"]
    
    def _extract_technical_analysis(self, text: str) -> Dict[str, Any]:
        """从分析文本中提取技术分析"""
        analysis = {}
        lines = text.split('\n')
        
        current_key = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测技术分析部分
            if "技术" in line and "分析" in line:
                continue
            
            # 检测键值对
            if ':' in line or '：' in line:
                sep = ':' if ':' in line else '：'
                parts = line.split(sep, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    analysis[key] = value
        
        # 如果没有提取到，使用默认值
        if not analysis:
            analysis = {
                "画面质量": "无法评估",
                "音频质量": "无法评估", 
                "制作水平": "无法评估",
                "改进建议": "无"
            }
        
        return analysis


def analyze_video(
    video_path: str,
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    output_format: str = "text",
    model: str = "doubao-seed-1-6-251015"
) -> Union[str, Dict[str, Any], VideoAnalysisResult]:
    """
    快速分析视频的便捷函数
    
    Args:
        video_path: 视频文件路径
        prompt: 自定义提示词，如果为None则使用默认分析
        api_key: API Key
        output_format: 输出格式，支持 "text", "json", "markdown", "object"
        model: 使用的模型
        
    Returns:
        根据output_format返回不同格式的结果
    """
    try:
        # 创建分析器
        analyzer = VideoAnalyzer(api_key=api_key, model=model)
        
        if prompt:
            # 使用自定义提示词
            result = analyzer.analyze_with_prompt(video_path, prompt, stream=False)
            
            if output_format == "json":
                return {"analysis": result}
            else:
                return result
        else:
            # 使用详细分析
            result = analyzer.analyze_detailed(video_path)
            
            if output_format == "json":
                return result.to_dict()
            elif output_format == "markdown":
                return result.to_markdown()
            elif output_format == "object":
                return result
            else:  # text
                return result.summary
                
    except Exception as e:
        logger.error(f"分析视频失败: {e}")
        return f"分析失败: {str(e)}"


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description="豆包视频分析器")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("--api-key", help="豆包API Key，如果不提供则从环境变量ARK_API_KEY获取")
    parser.add_argument("--prompt", help="自定义分析提示词")
    parser.add_argument("--output-format", choices=["text", "json", "markdown"], default="text", help="输出格式")
    parser.add_argument("--model", default="doubao-seed-1-6-251015", help="使用的模型")
    parser.add_argument("--detailed", action="store_true", help="执行详细分析")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.video_path):
        print(f"错误: 文件不存在: {args.video_path}")
        return 1
    
    try:
        if args.detailed:
            # 详细分析
            analyzer = VideoAnalyzer(api_key=args.api_key, model=args.model)
            result = analyzer.analyze_detailed(args.video_path)
            
            if args.output_format == "json":
                print(result.to_json())
            elif args.output_format == "markdown":
                print(result.to_markdown())
            else:
                print("# 视频分析报告")
                print(f"\n## 内容摘要\n{result.summary}")
                print(f"\n## 识别物体\n{', '.join(result.objects)}")
                print(f"\n## 技术分析")
                for key, value in result.technical_analysis.items():
                    print(f"- {key}: {value}")
        else:
            # 快速分析
            result = analyze_video(
                video_path=args.video_path,
                prompt=args.prompt,
                api_key=args.api_key,
                output_format=args.output_format,
                model=args.model
            )
            
            if isinstance(result, dict) and args.output_format == "json":
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())