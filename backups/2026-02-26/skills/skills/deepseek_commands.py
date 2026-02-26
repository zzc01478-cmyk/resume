#!/usr/bin/env python3
"""
DeepSeek监控快捷命令
集成到OpenClaw的快捷指令系统
"""

import json
from datetime import datetime
from deepseek_monitor import DeepSeekMonitor

class DeepSeekCommands:
    """DeepSeek监控命令"""
    
    def __init__(self):
        self.monitor = DeepSeekMonitor()
        self.commands = {
            "status": self.status,
            "report": self.report,
            "alerts": self.alerts,
            "thresholds": self.thresholds,
            "summary": self.summary,
            "help": self.help
        }
    
    def execute(self, command, args=None):
        """执行命令"""
        if command in self.commands:
            return self.commands[command](args)
        else:
            return self.help()
    
    def status(self, args=None):
        """查看当前状态"""
        summary = self.monitor.get_summary()
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_usage = summary["today"]
        
        # 估算成本（DeepSeek定价）
        # 假设: $0.14/1M tokens输入, $0.28/1M tokens输出
        input_cost = (today_usage.get("tokens", 0) * 0.5) * 0.14 / 1000000  # 假设50%输入
        output_cost = (today_usage.get("tokens", 0) * 0.5) * 0.28 / 1000000  # 假设50%输出
        estimated_cost = input_cost + output_cost
        
        result = f"""
📊 **DeepSeek API使用状态** ({today})

**今日使用**:
  Tokens: {today_usage.get('tokens', 0):,}
  请求数: {today_usage.get('requests', 0)}
  估算成本: ${estimated_cost:.6f}

**总计使用**:
  Tokens: {summary['total']['tokens']:,}
  总成本: ${summary['total']['cost']:.4f}
  总请求: {summary['total']['requests']}

**模型分布**:
"""
        
        for model, usage in summary["models"].items():
            result += f"  {model}: {usage['tokens']:,} tokens\n"
        
        # 检查告警
        alerts = self.monitor.check_thresholds()
        if alerts:
            result += "\n⚠️ **告警**:\n"
            for alert in alerts:
                result += f"  {alert['level']}: {alert['message']}\n"
        
        return result
    
    def report(self, args=None):
        """生成使用报告"""
        days = 7
        if args and len(args) > 0:
            try:
                days = int(args[0])
            except:
                pass
        
        report = self.monitor.generate_report(days=days)
        
        result = f"""
📈 **DeepSeek API使用报告** ({days}天)

**统计期间**: {report['period']['start']} 至 {report['period']['end']}

**总计**:
  Tokens: {report['total']['tokens']:,}
  成本: ${report['total']['cost']:.4f}

**每日使用**:
"""
        
        for day in report["daily_summary"]:
            result += f"  {day['date']}: {day['tokens']:,} tokens (${day['cost']:.4f})\n"
        
        result += "\n**模型使用**:\n"
        for model, usage in report["model_summary"].items():
            percentage = (usage["tokens"] / report["total"]["tokens"] * 100) if report["total"]["tokens"] > 0 else 0
            result += f"  {model}: {usage['tokens']:,} tokens ({percentage:.1f}%)\n"
        
        return result
    
    def alerts(self, args=None):
        """检查告警"""
        # 自定义阈值
        thresholds = {
            "daily_tokens": 100000,  # 10万/天
            "daily_cost": 1.0,       # 1美元/天
            "warning_percent": 80
        }
        
        # 如果提供了参数，更新阈值
        if args and len(args) >= 2:
            if args[0] == "tokens":
                thresholds["daily_tokens"] = int(args[1])
            elif args[0] == "cost":
                thresholds["daily_cost"] = float(args[1])
        
        alerts = self.monitor.check_thresholds(thresholds)
        
        if not alerts:
            return "✅ 当前无告警，使用情况正常。"
        
        result = "⚠️ **DeepSeek API使用告警**:\n\n"
        for alert in alerts:
            result += f"{alert['level']}: {alert['message']}\n"
        
        result += f"\n当前阈值:"
        result += f"\n  每日Token上限: {thresholds['daily_tokens']:,}"
        result += f"\n  每日成本上限: ${thresholds['daily_cost']:.2f}"
        result += f"\n  警告百分比: {thresholds['warning_percent']}%"
        
        return result
    
    def thresholds(self, args=None):
        """设置或查看阈值"""
        if args and len(args) >= 2:
            # 设置阈值
            threshold_type = args[0].lower()
            value = args[1]
            
            # 这里应该保存到配置文件
            config_file = "/root/.openclaw/logs/deepseek_thresholds.json"
            config = {}
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            if threshold_type == "tokens":
                config["daily_tokens"] = int(value)
            elif threshold_type == "cost":
                config["daily_cost"] = float(value)
            elif threshold_type == "warning":
                config["warning_percent"] = int(value)
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return f"✅ 已更新阈值: {threshold_type} = {value}"
        
        else:
            # 查看当前阈值
            default_thresholds = {
                "daily_tokens": 100000,
                "daily_cost": 1.0,
                "warning_percent": 80
            }
            
            config_file = "/root/.openclaw/logs/deepseek_thresholds.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    current_thresholds = json.load(f)
            else:
                current_thresholds = default_thresholds
            
            result = "📏 **当前阈值设置**:\n\n"
            result += f"每日Token上限: {current_thresholds.get('daily_tokens', 100000):,}\n"
            result += f"每日成本上限: ${current_thresholds.get('daily_cost', 1.0):.2f}\n"
            result += f"警告百分比: {current_thresholds.get('warning_percent', 80)}%\n\n"
            result += "设置示例: /deepseek_thresholds tokens 50000"
            
            return result
    
    def summary(self, args=None):
        """使用摘要"""
        summary = self.monitor.get_summary()
        
        # 计算效率指标
        total_requests = summary["total"]["requests"]
        avg_tokens_per_request = summary["total"]["tokens"] / total_requests if total_requests > 0 else 0
        
        result = f"""
📋 **DeepSeek API使用摘要**

**总体统计**:
  总Tokens: {summary['total']['tokens']:,}
  总成本: ${summary['total']['cost']:.6f}
  总请求数: {total_requests}
  平均Tokens/请求: {avg_tokens_per_request:.0f}

**今日统计** ({datetime.now().strftime('%Y-%m-%d')}):
  Tokens: {summary['today'].get('tokens', 0):,}
  请求数: {summary['today'].get('requests', 0)}
  成本: ${summary['today'].get('cost', 0):.6f}

**模型使用排名**:
"""
        
        # 按使用量排序
        sorted_models = sorted(
            summary["models"].items(),
            key=lambda x: x[1]["tokens"],
            reverse=True
        )
        
        for i, (model, usage) in enumerate(sorted_models[:5], 1):
            percentage = (usage["tokens"] / summary["total"]["tokens"] * 100) if summary["total"]["tokens"] > 0 else 0
            result += f"  {i}. {model}: {usage['tokens']:,} tokens ({percentage:.1f}%)\n"
        
        return result
    
    def help(self, args=None):
        """帮助信息"""
        return """
🤖 **DeepSeek监控命令帮助**

**可用命令**:
  /deepseek_status      - 查看当前使用状态
  /deepseek_report [天数] - 生成使用报告（默认7天）
  /deepseek_alerts      - 检查使用告警
  /deepseek_thresholds  - 查看或设置阈值
  /deepseek_summary     - 使用摘要
  /deepseek_help        - 显示此帮助

**阈值设置示例**:
  /deepseek_thresholds tokens 50000   # 设置每日token上限
  /deepseek_thresholds cost 0.5       # 设置每日成本上限
  /deepseek_thresholds warning 70     # 设置警告百分比

**监控功能**:
  • 实时token使用跟踪
  • 成本估算和告警
  • 模型使用分析
  • 每日/每周报告
"""

# 全局实例
deepseek_cmds = DeepSeekCommands()

def handle_deepseek_command(full_command):
    """处理DeepSeek命令"""
    parts = full_command.strip().split()
    if not parts:
        return deepseek_cmds.help()
    
    command = parts[0].replace("/deepseek_", "")
    args = parts[1:] if len(parts) > 1 else None
    
    return deepseek_cmds.execute(command, args)

if __name__ == "__main__":
    # 测试命令
    print(handle_deepseek_command("/deepseek_status"))
    print("\n" + "="*50 + "\n")
    print(handle_deepseek_command("/deepseek_report 3"))