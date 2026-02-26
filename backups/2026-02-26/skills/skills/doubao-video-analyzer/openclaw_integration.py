#!/usr/bin/env python3
"""
豆包视频分析器 - OpenClaw集成
将视频分析功能集成到OpenClaw工作流中
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_video import VideoAnalyzer, analyze_video, VideoAnalysisResult


class DoubaoVideoSkill:
    """豆包视频分析技能 - OpenClaw集成类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化技能
        
        Args:
            config: 配置字典，包含API Key等设置
        """
        self.config = config or {}
        self.api_key = self.config.get("api_key") or os.getenv("ARK_API_KEY")
        
        if not self.api_key:
            raise ValueError("需要提供API Key或设置ARK_API_KEY环境变量")
        
        # 初始化分析器
        self.analyzer = VideoAnalyzer(
            api_key=self.api_key,
            base_url=self.config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3"),
            model=self.config.get("model", "doubao-seed-1-6-251015"),
            timeout=self.config.get("timeout", 300)
        )
        
        # 输出目录
        self.output_dir = Path(self.config.get("output_dir", "./video_analysis_output"))
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"豆包视频分析技能初始化完成")
        print(f"输出目录: {self.output_dir}")
        print(f"使用模型: {self.analyzer.model}")
    
    async def analyze_video_file(
        self,
        video_path: str,
        analysis_type: str = "detailed",
        user_prompt: Optional[str] = None,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        分析视频文件
        
        Args:
            video_path: 视频文件路径
            analysis_type: 分析类型，支持 "summary", "detailed", "events", "custom"
            user_prompt: 自定义提示词（当analysis_type为"custom"时使用）
            output_format: 输出格式，支持 "text", "json", "markdown"
            
        Returns:
            分析结果字典
        """
        try:
            print(f"开始分析视频: {video_path}")
            
            if not os.path.exists(video_path):
                return {
                    "success": False,
                    "error": f"视频文件不存在: {video_path}"
                }
            
            # 检查文件大小
            file_size = os.path.getsize(video_path)
            if file_size > 512 * 1024 * 1024:  # 512MB
                return {
                    "success": False,
                    "error": f"视频文件过大: {file_size/(1024*1024):.2f}MB > 512MB"
                }
            
            # 根据分析类型执行不同的分析
            if analysis_type == "summary":
                # 快速摘要
                result = await asyncio.to_thread(
                    self.analyzer.analyze_summary, video_path
                )
                
                output = {
                    "summary": result,
                    "analysis_type": "summary"
                }
                
            elif analysis_type == "detailed":
                # 详细分析
                result = await asyncio.to_thread(
                    self.analyzer.analyze_detailed, video_path
                )
                
                if output_format == "json":
                    output = result.to_dict()
                elif output_format == "markdown":
                    output = {"markdown": result.to_markdown()}
                else:
                    output = {"text": result.summary}
                
                output["analysis_type"] = "detailed"
                
            elif analysis_type == "events":
                # 事件分析
                result = await asyncio.to_thread(
                    self.analyzer.analyze_events, video_path
                )
                
                output = {
                    "events": result,
                    "analysis_type": "events"
                }
                
            elif analysis_type == "custom" and user_prompt:
                # 自定义分析
                result = await asyncio.to_thread(
                    self.analyzer.analyze_with_prompt, video_path, user_prompt
                )
                
                output = {
                    "analysis": result,
                    "analysis_type": "custom",
                    "user_prompt": user_prompt
                }
                
            else:
                return {
                    "success": False,
                    "error": f"不支持的分析类型: {analysis_type}"
                }
            
            # 保存结果到文件
            output_file = self._save_analysis_result(
                video_path=video_path,
                result=output,
                analysis_type=analysis_type,
                output_format=output_format
            )
            
            # 返回结果
            return {
                "success": True,
                "analysis_type": analysis_type,
                "output_format": output_format,
                "result": output,
                "output_file": str(output_file),
                "video_info": await asyncio.to_thread(
                    self.analyzer.extract_video_info, video_path
                )
            }
            
        except Exception as e:
            print(f"分析视频失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type
            }
    
    def _save_analysis_result(
        self,
        video_path: str,
        result: Dict[str, Any],
        analysis_type: str,
        output_format: str
    ) -> Path:
        """
        保存分析结果到文件
        
        Args:
            video_path: 视频文件路径
            result: 分析结果
            analysis_type: 分析类型
            output_format: 输出格式
            
        Returns:
            输出文件路径
        """
        # 生成文件名
        video_name = Path(video_path).stem
        timestamp = int(time.time())
        filename = f"{video_name}_{analysis_type}_{timestamp}"
        
        if output_format == "json":
            output_file = self.output_dir / f"{filename}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        elif output_format == "markdown":
            output_file = self.output_dir / f"{filename}.md"
            if "markdown" in result:
                content = result["markdown"]
            else:
                # 生成简单的Markdown
                content = f"# 视频分析报告\n\n"
                content += f"**视频文件**: {video_path}\n\n"
                content += f"**分析类型**: {analysis_type}\n\n"
                content += f"**分析结果**:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
        
        else:  # text
            output_file = self.output_dir / f"{filename}.txt"
            if "text" in result:
                content = result["text"]
            elif "summary" in result:
                content = result["summary"]
            else:
                content = str(result)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
        
        print(f"分析结果已保存到: {output_file}")
        return output_file
    
    async def batch_analyze(
        self,
        video_paths: List[str],
        analysis_type: str = "summary",
        output_format: str = "text"
    ) -> List[Dict[str, Any]]:
        """
        批量分析视频
        
        Args:
            video_paths: 视频文件路径列表
            analysis_type: 分析类型
            output_format: 输出格式
            
        Returns:
            分析结果列表
        """
        results = []
        
        for i, video_path in enumerate(video_paths, 1):
            print(f"分析进度: {i}/{len(video_paths)} - {video_path}")
            
            try:
                result = await self.analyze_video_file(
                    video_path=video_path,
                    analysis_type=analysis_type,
                    output_format=output_format
                )
                results.append(result)
                
            except Exception as e:
                print(f"分析失败 {video_path}: {e}")
                results.append({
                    "success": False,
                    "video_path": video_path,
                    "error": str(e)
                })
        
        # 生成批量分析报告
        if results:
            self._generate_batch_report(results, analysis_type)
        
        return results
    
    def _generate_batch_report(self, results: List[Dict[str, Any]], analysis_type: str):
        """生成批量分析报告"""
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        report = {
            "total_videos": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "analysis_type": analysis_type,
            "timestamp": int(time.time()),
            "results": results
        }
        
        report_file = self.output_dir / f"batch_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"批量分析报告已保存到: {report_file}")
    
    def get_available_analysis_types(self) -> List[Dict[str, str]]:
        """获取可用的分析类型"""
        return [
            {"id": "summary", "name": "快速摘要", "description": "用一段话概括视频主要内容"},
            {"id": "detailed", "name": "详细分析", "description": "完整的视频分析，包括场景、事件、物体等"},
            {"id": "events", "name": "事件分析", "description": "提取视频中的关键事件时间线"},
            {"id": "technical", "name": "技术分析", "description": "分析视频的技术特征和质量"},
            {"id": "custom", "name": "自定义分析", "description": "使用自定义提示词进行分析"}
        ]
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的视频格式"""
        return [".mp4", ".avi", ".mov"]
    
    def cleanup_old_files(self, days: int = 7):
        """清理旧的分析文件"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        deleted_count = 0
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                file_time = file_path.stat().st_mtime
                if file_time < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"删除文件失败 {file_path}: {e}")
        
        print(f"清理了 {deleted_count} 个旧文件")


# OpenClaw技能注册函数
def register_skill():
    """注册技能到OpenClaw"""
    skill_config = {
        "name": "doubao-video-analyzer",
        "version": "1.0.0",
        "description": "使用豆包大模型进行视频内容分析",
        "author": "OpenClaw Community",
        "entry_point": "openclaw_integration.DoubaoVideoSkill",
        "config_schema": {
            "api_key": {"type": "string", "required": True, "description": "豆包API Key"},
            "base_url": {"type": "string", "default": "https://ark.cn-beijing.volces.com/api/v3"},
            "model": {"type": "string", "default": "doubao-seed-1-6-251015"},
            "timeout": {"type": "number", "default": 300},
            "output_dir": {"type": "string", "default": "./video_analysis_output"}
        },
        "commands": {
            "analyze": {
                "description": "分析视频文件",
                "parameters": {
                    "video_path": {"type": "string", "required": True},
                    "analysis_type": {"type": "string", "default": "detailed", "choices": ["summary", "detailed", "events", "custom"]},
                    "user_prompt": {"type": "string", "required": False},
                    "output_format": {"type": "string", "default": "markdown", "choices": ["text", "json", "markdown"]}
                }
            },
            "batch_analyze": {
                "description": "批量分析视频",
                "parameters": {
                    "video_paths": {"type": "array", "required": True},
                    "analysis_type": {"type": "string", "default": "summary"},
                    "output_format": {"type": "string", "default": "text"}
                }
            }
        }
    }
    
    return skill_config


# 命令行接口
async def main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="豆包视频分析技能 - OpenClaw集成")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--video", help="视频文件路径")
    parser.add_argument("--analysis-type", default="detailed", choices=["summary", "detailed", "events", "custom"])
    parser.add_argument("--prompt", help="自定义提示词")
    parser.add_argument("--output-format", default="markdown", choices=["text", "json", "markdown"])
    parser.add_argument("--batch", nargs="+", help="批量分析多个视频")
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)
    
    # 创建技能实例
    try:
        skill = DoubaoVideoSkill(config)
        
        if args.batch:
            # 批量分析
            results = await skill.batch_analyze(
                video_paths=args.batch,
                analysis_type=args.analysis_type,
                output_format=args.output_format
            )
            
            print(f"\n批量分析完成:")
            print(f"总计: {len(results)} 个视频")
            print(f"成功: {len([r for r in results if r.get('success')])}")
            print(f"失败: {len([r for r in results if not r.get('success')])}")
            
        elif args.video:
            # 单个视频分析
            result = await skill.analyze_video_file(
                video_path=args.video,
                analysis_type=args.analysis_type,
                user_prompt=args.prompt,
                output_format=args.output_format
            )
            
            if result["success"]:
                print(f"\n分析成功!")
                print(f"输出文件: {result.get('output_file')}")
                
                if args.output_format == "text" and "result" in result:
                    if "text" in result["result"]:
                        print(f"\n分析结果:\n{result['result']['text']}")
                    elif "summary" in result["result"]:
                        print(f"\n分析结果:\n{result['result']['summary']}")
            else:
                print(f"\n分析失败: {result.get('error')}")
        
        else:
            print("请提供视频文件路径或使用批量分析模式")
            print("可用分析类型:", [t["id"] for t in skill.get_available_analysis_types()])
            
    except Exception as e:
        print(f"技能初始化失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import time
    time = __import__('time')
    asyncio.run(main())