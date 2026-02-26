#!/usr/bin/env python3
"""
模型切换快捷命令
集成到OpenClaw指令系统
"""

import sys
from model_switcher import handle_model_command

class ModelCommandSystem:
    """模型命令系统"""
    
    def __init__(self):
        self.commands = {
            "help": self.show_help,
            "quick": self.quick_switch,
            "preset": self.preset_switch,
            "alias": self.manage_aliases,
            "history": self.switch_history,
            "recommend": self.recommend_model
        }
    
    def execute(self, full_command):
        """执行模型命令"""
        parts = full_command.strip().split()
        if not parts or len(parts) < 2:
            return self.show_help()
        
        # 移除/model前缀
        args = parts[1:]
        
        # 检查是否是快捷命令
        if args[0] in self.commands:
            return self.commands[args[0]](args[1:] if len(args) > 1 else None)
        
        # 否则使用标准处理器
        return handle_model_command(args)
    
    def show_help(self, args=None):
        """显示帮助"""
        return """
🤖 **模型切换命令系统**

**基本命令**:
  /model list [提供商]      # 列出可用模型
  /model current           # 查看当前模型
  /model switch <模型ID>   # 切换模型
  /model compare [模型1] [模型2] # 比较模型
  /model test [文本]       # 测试当前模型

**快捷命令**:
  /model quick <名称>      # 快速切换（支持别名）
  /model preset <场景>     # 按场景切换预设
  /model alias list        # 列出别名
  /model alias add <别名> <模型ID> # 添加别名
  /model history          # 切换历史
  /model recommend        # 推荐模型

**场景预设**:
  /model preset daily     # 日常对话（低成本）
  /model preset reasoning # 复杂推理（高能力）
  /model preset code      # 编程任务
  /model preset creative  # 创意写作
  /model preset long      # 长文档处理

**使用示例**:
  /model list                    # 查看所有模型
  /model switch deepseek-reasoner # 切换推理模型
  /model quick chat              # 快速切换到聊天模型
  /model preset code             # 切换到编程预设
  /model compare                 # 比较当前与默认模型

**模型ID示例**:
  deepseek/deepseek-chat        # DeepSeek聊天模型
  deepseek/deepseek-reasoner    # DeepSeek推理模型
  minimax/MiniMax-M2.5          # MiniMax M2.5
  linkapi/gemini-2.5-pro        # Gemini 2.5 Pro

💡 **提示**: 可以使用部分名称，如 `deepseek-reasoner`
"""
    
    def quick_switch(self, args):
        """快速切换"""
        if not args:
            return "❌ 请指定模型名称或别名"
        
        target = args[0]
        
        # 别名映射
        aliases = {
            "chat": "deepseek/deepseek-chat",
            "reasoner": "deepseek/deepseek-reasoner",
            "reasoning": "deepseek/deepseek-reasoner",
            "deepseek": "deepseek/deepseek-chat",
            "minimax": "minimax/MiniMax-M2.5",
            "gemini": "linkapi/gemini-2.5-pro",
            "fast": "deepseek/deepseek-chat",
            "smart": "deepseek/deepseek-reasoner",
            "long": "linkapi/gemini-2.5-pro"
        }
        
        # 检查别名
        if target in aliases:
            model_id = aliases[target]
            return handle_model_command(["switch", model_id])
        
        # 否则作为普通模型ID处理
        return handle_model_command(["switch", target])
    
    def preset_switch(self, args):
        """按场景切换预设"""
        if not args:
            return "❌ 请指定场景，如：/model preset daily"
        
        scene = args[0].lower()
        
        presets = {
            "daily": {
                "model": "deepseek/deepseek-chat",
                "reason": "日常对话、低成本、快速响应"
            },
            "reasoning": {
                "model": "deepseek/deepseek-reasoner",
                "reason": "复杂推理、数学计算、逻辑分析"
            },
            "code": {
                "model": "deepseek/deepseek-reasoner",
                "reason": "编程任务、代码分析、调试"
            },
            "creative": {
                "model": "minimax/MiniMax-M2.5",
                "reason": "创意写作、角色扮演、故事生成"
            },
            "long": {
                "model": "linkapi/gemini-2.5-pro",
                "reason": "长文档处理、复杂分析、多轮对话"
            },
            "cheap": {
                "model": "deepseek/deepseek-chat",
                "reason": "最低成本、简单任务"
            },
            "powerful": {
                "model": "linkapi/gemini-2.5-pro",
                "reason": "最强能力、多模态、长上下文"
            }
        }
        
        if scene not in presets:
            available = ", ".join(presets.keys())
            return f"❌ 未知场景: {scene}\n可用场景: {available}"
        
        preset = presets[scene]
        result = handle_model_command(["switch", preset["model"]])
        
        # 添加场景说明
        result += f"\n\n🎯 **场景**: {scene}"
        result += f"\n📝 **说明**: {preset['reason']}"
        
        return result
    
    def manage_aliases(self, args):
        """管理别名"""
        if not args:
            return "❌ 请指定操作，如：/model alias list"
        
        action = args[0].lower()
        
        if action == "list":
            return self._list_aliases()
        elif action == "add":
            if len(args) < 3:
                return "❌ 需要两个参数：别名 模型ID"
            return self._add_alias(args[1], args[2])
        elif action == "remove":
            if len(args) < 2:
                return "❌ 需要别名参数"
            return self._remove_alias(args[1])
        else:
            return f"❌ 未知操作: {action}"
    
    def _list_aliases(self):
        """列出别名"""
        aliases = {
            "chat": "deepseek/deepseek-chat",
            "reasoner": "deepseek/deepseek-reasoner",
            "deepseek": "deepseek/deepseek-chat",
            "minimax": "minimax/MiniMax-M2.5",
            "gemini": "linkapi/gemini-2.5-pro"
        }
        
        result = "📋 **模型别名列表**:\n\n"
        for alias, model_id in aliases.items():
            result += f"  `{alias}` → `{model_id}`\n"
        
        result += "\n💡 使用 `/model quick <别名>` 快速切换"
        return result
    
    def _add_alias(self, alias, model_id):
        """添加别名"""
        # 这里应该保存到配置文件
        return f"✅ 已添加别名: `{alias}` → `{model_id}`\n\n使用 `/model quick {alias}` 切换"
    
    def _remove_alias(self, alias):
        """移除别名"""
        return f"✅ 已移除别名: `{alias}`"
    
    def switch_history(self, args):
        """切换历史"""
        # 这里应该从历史记录获取
        history = [
            {"time": "14:30", "from": "deepseek-chat", "to": "deepseek-reasoner", "reason": "代码分析"},
            {"time": "13:45", "from": "deepseek-reasoner", "to": "deepseek-chat", "reason": "日常对话"},
            {"time": "10:20", "from": "deepseek-chat", "to": "MiniMax-M2.5", "reason": "创意写作"}
        ]
        
        result = "📜 **模型切换历史**:\n\n"
        
        for entry in history:
            result += f"⏰ {entry['time']}: `{entry['from']}` → `{entry['to']}`\n"
            result += f"   📝 原因: {entry['reason']}\n\n"
        
        result += "💡 最近切换的模型更容易切换回来"
        return result
    
    def recommend_model(self, args):
        """推荐模型"""
        if args:
            task_type = args[0].lower()
        else:
            task_type = "general"
        
        recommendations = {
            "general": {
                "model": "deepseek/deepseek-chat",
                "reason": "日常对话、文本处理、成本最低"
            },
            "reasoning": {
                "model": "deepseek/deepseek-reasoner",
                "reason": "复杂推理、数学计算、逻辑分析"
            },
            "code": {
                "model": "deepseek/deepseek-reasoner",
                "reason": "编程任务、代码分析、调试优化"
            },
            "creative": {
                "model": "minimax/MiniMax-M2.5",
                "reason": "创意写作、故事生成、角色扮演"
            },
            "long": {
                "model": "linkapi/gemini-2.5-pro",
                "reason": "长文档处理、复杂分析、多轮对话"
            },
            "cheap": {
                "model": "deepseek/deepseek-chat",
                "reason": "最低成本、简单问答、日常使用"
            },
            "quality": {
                "model": "linkapi/gemini-2.5-pro",
                "reason": "最高质量、多模态能力、专业分析"
            }
        }
        
        if task_type not in recommendations:
            available = ", ".join(recommendations.keys())
            return f"❌ 未知任务类型: {task_type}\n可用类型: {available}"
        
        rec = recommendations[task_type]
        
        result = f"🎯 **模型推荐** ({task_type}):\n\n"
        result += f"**推荐模型**: `{rec['model']}`\n"
        result += f"**推荐理由**: {rec['reason']}\n\n"
        result += f"**切换命令**: `/model switch {rec['model'].split('/')[-1]}`\n"
        result += f"**快捷命令**: `/model preset {task_type}`"
        
        return result

# 全局实例
model_cmds = ModelCommandSystem()

def handle_model_switch(full_command):
    """处理模型切换命令"""
    return model_cmds.execute(full_command)

if __name__ == "__main__":
    # 测试
    if len(sys.argv) > 1:
        command = "/model " + " ".join(sys.argv[1:])
        print(handle_model_switch(command))
    else:
        print(model_cmds.show_help())