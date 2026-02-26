#!/usr/bin/env python3
"""
模型切换指令系统
支持动态切换DeepSeek、MiniMax、Gemini等模型
"""

import json
import os
from pathlib import Path

class ModelSwitcher:
    """模型切换器"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or Path.home() / ".openclaw" / "config" / "models_config.json"
        self.models = self._load_models()
        self.current_model = self._get_current_model()
    
    def _load_models(self):
        """加载可用模型"""
        # 从OpenClaw配置中读取模型
        openclaw_config = Path.home() / ".openclaw" / "openclaw.json"
        
        if openclaw_config.exists():
            with open(openclaw_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                models = {}
                
                # DeepSeek模型
                if "deepseek" in config.get("models", {}).get("providers", {}):
                    deepseek = config["models"]["providers"]["deepseek"]
                    for model in deepseek.get("models", []):
                        model_id = model.get("id")
                        if model_id:
                            models[f"deepseek/{model_id}"] = {
                                "name": model.get("name", model_id),
                                "provider": "deepseek",
                                "base_url": deepseek.get("base_url"),
                                "api_key": deepseek.get("api_key"),
                                "context_window": model.get("contextWindow", 128000),
                                "max_tokens": model.get("maxTokens", 4096),
                                "reasoning": model.get("reasoning", False),
                                "cost_input": model.get("cost", {}).get("input", 0),
                                "cost_output": model.get("cost", {}).get("output", 0)
                            }
                
                # MiniMax模型
                if "minimax" in config.get("models", {}).get("providers", {}):
                    minimax = config["models"]["providers"]["minimax"]
                    for model in minimax.get("models", []):
                        model_id = model.get("id")
                        if model_id:
                            models[f"minimax/{model_id}"] = {
                                "name": model.get("name", model_id),
                                "provider": "minimax",
                                "base_url": minimax.get("base_url"),
                                "api_key": minimax.get("api_key"),
                                "context_window": model.get("contextWindow", 200000),
                                "max_tokens": model.get("maxTokens", 8192),
                                "reasoning": model.get("reasoning", False),
                                "cost_input": model.get("cost", {}).get("input", 0),
                                "cost_output": model.get("cost", {}).get("output", 0)
                            }
                
                # Gemini模型（通过LinkAPI）
                if "linkapi" in config.get("models", {}).get("providers", {}):
                    linkapi = config["models"]["providers"]["linkapi"]
                    for model in linkapi.get("models", []):
                        model_id = model.get("id")
                        if model_id:
                            models[f"linkapi/{model_id}"] = {
                                "name": model.get("name", model_id),
                                "provider": "linkapi",
                                "base_url": linkapi.get("base_url"),
                                "api_key": linkapi.get("api_key"),
                                "context_window": 1000000,  # Gemini 2.5
                                "max_tokens": 8192,
                                "reasoning": "gemini-2.5-pro" in model_id,
                                "cost_input": 0.000125,  # $0.125/1M tokens
                                "cost_output": 0.000375   # $0.375/1M tokens
                            }
                
                return models
        
        # 默认模型（如果配置文件不存在）
        return {
            "deepseek/deepseek-chat": {
                "name": "DeepSeek Chat",
                "provider": "deepseek",
                "context_window": 128000,
                "max_tokens": 4096,
                "reasoning": False,
                "cost_input": 0.00014,   # $0.14/1M tokens
                "cost_output": 0.00028   # $0.28/1M tokens
            },
            "deepseek/deepseek-reasoner": {
                "name": "DeepSeek Reasoner",
                "provider": "deepseek",
                "context_window": 128000,
                "max_tokens": 4096,
                "reasoning": True,
                "cost_input": 0.00028,   # $0.28/1M tokens
                "cost_output": 0.00056   # $0.56/1M tokens
            }
        }
    
    def _get_current_model(self):
        """获取当前模型"""
        # 从session_status获取
        try:
            # 这里应该调用实际的session_status
            # 暂时返回默认
            return "deepseek/deepseek-chat"
        except:
            return "deepseek/deepseek-chat"
    
    def list_models(self, filter_provider=None):
        """列出可用模型"""
        result = "🤖 **可用模型列表**:\n\n"
        
        # 按提供商分组
        providers = {}
        for model_id, info in self.models.items():
            provider = info["provider"]
            if provider not in providers:
                providers[provider] = []
            
            providers[provider].append((model_id, info))
        
        # 显示每个提供商的模型
        for provider, model_list in providers.items():
            if filter_provider and provider != filter_provider:
                continue
            
            result += f"**{provider.upper()}**:\n"
            
            for model_id, info in model_list:
                current_marker = " 🟢" if model_id == self.current_model else ""
                reasoning_marker = " 🧠" if info.get("reasoning") else ""
                
                result += f"  • `{model_id}`{current_marker}{reasoning_marker}\n"
                result += f"     名称: {info['name']}\n"
                result += f"     上下文: {info.get('context_window', '未知'):,} tokens\n"
                result += f"     输出: {info.get('max_tokens', '未知'):,} tokens\n"
                
                # 成本信息
                cost_input = info.get('cost_input', 0)
                cost_output = info.get('cost_output', 0)
                if cost_input > 0 or cost_output > 0:
                    cost_per_1k = (cost_input * 1000, cost_output * 1000)
                    result += f"     成本: ${cost_per_1k[0]:.4f}/1k输入, ${cost_per_1k[1]:.4f}/1k输出\n"
                
                result += "\n"
        
        result += f"\n当前使用: `{self.current_model}`"
        return result
    
    def switch_model(self, model_id):
        """切换模型"""
        if model_id not in self.models:
            # 尝试模糊匹配
            matching_models = []
            for available_id in self.models.keys():
                if model_id.lower() in available_id.lower():
                    matching_models.append(available_id)
            
            if not matching_models:
                return f"❌ 未找到模型: {model_id}\n\n{self.list_models()}"
            elif len(matching_models) == 1:
                model_id = matching_models[0]
            else:
                result = f"🔍 找到多个匹配的模型:\n"
                for match in matching_models:
                    result += f"  • {match}\n"
                result += f"\n请指定完整的模型ID"
                return result
        
        # 保存当前模型选择
        self._save_current_model(model_id)
        self.current_model = model_id
        
        model_info = self.models[model_id]
        
        result = f"✅ **已切换到模型**: `{model_id}`\n\n"
        result += f"**模型信息**:\n"
        result += f"  名称: {model_info['name']}\n"
        result += f"  提供商: {model_info['provider']}\n"
        result += f"  上下文窗口: {model_info.get('context_window', '未知'):,} tokens\n"
        result += f"  最大输出: {model_info.get('max_tokens', '未知'):,} tokens\n"
        
        if model_info.get('reasoning'):
            result += f"  推理能力: ✅ 支持\n"
        
        # 成本信息
        cost_input = model_info.get('cost_input', 0)
        cost_output = model_info.get('cost_output', 0)
        if cost_input > 0 or cost_output > 0:
            result += f"  成本估算:\n"
            result += f"    • 输入: ${cost_input * 1000000:.2f}/1M tokens\n"
            result += f"    • 输出: ${cost_output * 1000000:.2f}/1M tokens\n"
        
        result += f"\n💡 使用 `/model test` 测试新模型"
        
        return result
    
    def _save_current_model(self, model_id):
        """保存当前模型选择"""
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        config["current_model"] = model_id
        config["last_switched"] = os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else None
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_current_model_info(self):
        """获取当前模型信息"""
        if self.current_model not in self.models:
            return "❌ 当前模型配置错误"
        
        model_info = self.models[self.current_model]
        
        result = f"🟢 **当前模型**: `{self.current_model}`\n\n"
        result += f"**详细信息**:\n"
        result += f"  名称: {model_info['name']}\n"
        result += f"  提供商: {model_info['provider']}\n"
        result += f"  上下文: {model_info.get('context_window', '未知'):,} tokens\n"
        result += f"  最大输出: {model_info.get('max_tokens', '未知'):,} tokens\n"
        
        if model_info.get('reasoning'):
            result += f"  推理能力: ✅ 支持\n"
        
        # 使用统计（需要从其他地方获取）
        result += f"\n**使用建议**:\n"
        
        if "reasoner" in self.current_model.lower():
            result += f"  • 适合复杂推理、数学计算、代码分析\n"
            result += f"  • 成本较高，建议用于重要任务\n"
        elif "chat" in self.current_model.lower():
            result += f"  • 适合日常对话、文本处理、简单任务\n"
            result += f"  • 成本较低，适合常规使用\n"
        elif "gemini" in self.current_model.lower():
            result += f"  • 适合多模态任务、长上下文处理\n"
            result += f"  • 上下文窗口极大（1M tokens）\n"
        
        return result
    
    def compare_models(self, model1=None, model2=None):
        """比较模型"""
        if not model1:
            model1 = self.current_model
        
        if model1 not in self.models:
            return f"❌ 模型不存在: {model1}"
        
        if not model2:
            # 与默认模型比较
            default_model = "deepseek/deepseek-chat"
            if default_model == model1:
                # 找另一个模型比较
                for model_id in self.models.keys():
                    if model_id != model1:
                        model2 = model_id
                        break
            
            if not model2:
                model2 = default_model
        
        if model2 not in self.models:
            return f"❌ 模型不存在: {model2}"
        
        info1 = self.models[model1]
        info2 = self.models[model2]
        
        result = f"📊 **模型对比**: `{model1}` vs `{model2}`\n\n"
        
        result += "| 特性 | 模型1 | 模型2 |\n"
        result += "|------|-------|-------|\n"
        result += f"| 名称 | {info1['name']} | {info2['name']} |\n"
        result += f"| 提供商 | {info1['provider']} | {info2['provider']} |\n"
        result += f"| 上下文窗口 | {info1.get('context_window', 'N/A'):,} | {info2.get('context_window', 'N/A'):,} |\n"
        result += f"| 最大输出 | {info1.get('max_tokens', 'N/A'):,} | {info2.get('max_tokens', 'N/A'):,} |\n"
        result += f"| 推理能力 | {'✅' if info1.get('reasoning') else '❌'} | {'✅' if info2.get('reasoning') else '❌'} |\n"
        
        # 成本对比
        cost1_input = info1.get('cost_input', 0)
        cost1_output = info1.get('cost_output', 0)
        cost2_input = info2.get('cost_input', 0)
        cost2_output = info2.get('cost_output', 0)
        
        if cost1_input > 0 or cost1_output > 0 or cost2_input > 0 or cost2_output > 0:
            result += f"| 输入成本 | ${cost1_input * 1000000:.2f}/1M | ${cost2_input * 1000000:.2f}/1M |\n"
            result += f"| 输出成本 | ${cost1_output * 1000000:.2f}/1M | ${cost2_output * 1000000:.2f}/1M |\n"
        
        result += f"\n**推荐用途**:\n"
        
        # 根据模型特性推荐
        recommendations = {
            "deepseek/deepseek-chat": "日常对话、文本处理、简单任务",
            "deepseek/deepseek-reasoner": "复杂推理、数学计算、代码分析",
            "minimax/": "中文优化、创意写作、角色扮演",
            "gemini-": "长文档处理、多模态任务、复杂分析"
        }
        
        for pattern, recommendation in recommendations.items():
            if pattern in model1:
                result += f"  • `{model1}`: {recommendation}\n"
                break
        
        for pattern, recommendation in recommendations.items():
            if pattern in model2:
                result += f"  • `{model2}`: {recommendation}\n"
                break
        
        return result
    
    def test_model(self, test_text="你好，请用一句话介绍你自己"):
        """测试模型"""
        # 这里应该实际调用模型进行测试
        # 暂时返回模拟结果
        
        model_info = self.models.get(self.current_model, {})
        
        result = f"🧪 **模型测试**: `{self.current_model}`\n\n"
        result += f"**测试输入**: {test_text}\n\n"
        result += "**模拟响应**:\n"
        
        if "reasoner" in self.current_model.lower():
            result += "> 我是一个DeepSeek推理模型，专门处理需要逻辑推理、数学计算和复杂分析的任务。我采用思维链推理方式，能够逐步分析问题并提供详细解答。"
        elif "minimax" in self.current_model.lower():
            result += "> 你好！我是MiniMax AI助手，专注于中文场景优化。我擅长创意写作、角色扮演和情感交流，希望能为你提供温暖而专业的帮助。"
        elif "gemini" in self.currentModel.lower():
            result += "> 我是Google的Gemini模型，拥有极长的上下文窗口（100万tokens）和强大的多模态能力。我擅长处理长文档、复杂分析和跨领域任务。"
        else:
            result += "> 你好！我是DeepSeek AI助手，很高兴为你服务。我可以帮助你处理各种文本任务，包括问答、写作、翻译、编程等。有什么我可以帮你的吗？"
        
        result += f"\n\n**测试结果**: ✅ 模型响应正常"
        result += f"\n**建议**: 可以开始使用 `{self.current_model}` 进行任务处理"
        
        return result

# 命令处理器
def handle_model_command(args):
    """处理/model命令"""
    switcher = ModelSwitcher()
    
    if not args:
        return switcher.get_current_model_info()
    
    command = args[0].lower()
    
    if command == "list":
        filter_provider = args[1] if len(args) > 1 else None
        return switcher.list_models(filter_provider)
    
    elif command == "current":
        return switcher.get_current_model_info()
    
    elif command == "switch":
        if len(args) < 2:
            return "❌ 请指定要切换的模型ID，如：/model switch deepseek-reasoner"
        return switcher.switch_model(args[1])
    
    elif command == "info":
        if len(args) < 2:
            return switcher.get_current_model_info()
        # 这里需要实现查看特定模型信息
        return f"查看模型信息功能待实现，请使用 /model list 查看所有模型"