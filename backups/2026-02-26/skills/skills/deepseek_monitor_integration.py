#!/usr/bin/env python3
"""
DeepSeek监控集成到OpenClaw
自动从session_status获取数据并监控
"""

import json
import os
from datetime import datetime
from deepseek_monitor import DeepSeekMonitor

def parse_session_status(status_text):
    """
    解析session_status输出
    
    示例输入：
    🦞 OpenClaw 2026.2.21-2 (35a57bc)
    🕒 Time: Wednesday, February 25th, 2026 — 2:39 PM (UTC)
    🧠 Model: deepseek/deepseek-chat · 🔑 api-key sk-cdb…fe7f82 (models.json)
    🧮 Tokens: 208 in / 786 out · 💵 Cost: $0.0000
    🗄️ Cache: 100% hit · 102k cached, 0 new
    📚 Context: 102k/200k (51%) · 🧹 Compactions: 2
    """
    lines = status_text.strip().split('\n')
    data = {}
    
    for line in lines:
        line = line.strip()
        
        # 解析token使用
        if "🧮 Tokens:" in line:
            parts = line.split("·")
            token_part = parts[0].replace("🧮 Tokens:", "").strip()
            cost_part = parts[1].replace("💵 Cost:", "").strip() if len(parts) > 1 else "$0.0000"
            
            # 提取输入输出token
            if "in /" in token_part:
                in_out = token_part.split("in /")
                data["input_tokens"] = int(in_out[0].strip())
                data["output_tokens"] = int(in_out[1].split("out")[0].strip())
        
        # 解析成本
        if "💵 Cost:" in line:
            cost_str = line.split("💵 Cost:")[1].split("·")[0].strip()
            data["cost"] = float(cost_str.replace("$", ""))
        
        # 解析模型
        if "🧠 Model:" in line:
            model_part = line.split("🧠 Model:")[1].split("·")[0].strip()
            data["model"] = model_part.split("/")[-1] if "/" in model_part else model_part
    
    # 设置默认值
    data.setdefault("input_tokens", 0)
    data.setdefault("output_tokens", 0)
    data.setdefault("cost", 0.0)
    data.setdefault("model", "deepseek-chat")
    
    return data

def auto_monitor_deepseek():
    """自动监控DeepSeek使用"""
    monitor = DeepSeekMonitor()
    
    # 这里需要实际调用session_status工具
    # 由于在脚本中无法直接调用，这里提供接口
    
    print("DeepSeek监控系统已启动")
    print("=" * 50)
    
    # 显示当前状态
    summary = monitor.get_summary()
    
    print(f"📊 总使用: {summary['total']['tokens']:,} tokens")
    print(f"💰 总成本: ${summary['total']['cost']:.4f}")
    print(f"📅 今日使用: {summary['today'].get('tokens', 0):,} tokens")
    
    # 检查阈值
    thresholds = {
        "daily_tokens": 100000,  # 10万/天
        "daily_cost": 1.0,       # 1美元/天
        "warning_percent": 80
    }
    
    alerts = monitor.check_thresholds(thresholds)
    if alerts:
        print("\n⚠️ 告警:")
        for alert in alerts:
            print(f"  {alert['level']}: {alert['message']}")
    else:
        print("\n✅ 使用情况正常")
    
    # 模型使用分布
    print("\n🤖 模型使用分布:")
    for model, usage in summary["models"].items():
        print(f"  {model}: {usage['tokens']:,} tokens ({usage['requests']}次调用)")
    
    return summary

def setup_cron_monitoring():
    """设置定时监控"""
    cron_script = """#!/bin/bash
# DeepSeek API使用监控cron任务
# 每10分钟运行一次

cd /root/.openclaw/workspace/skills
python3 deepseek_monitor_integration.py >> /root/.openclaw/logs/deepseek_monitor.log 2>&1

# 如果超过阈值，发送通知
ALERTS=$(python3 -c "
from deepseek_monitor_integration import auto_monitor_deepseek
result = auto_monitor_deepseek()
if 'alerts' in result and result['alerts']:
    for alert in result['alerts']:
        print(f'{alert[\"level\"]}: {alert[\"message\"]}')
")

if [ ! -z "$ALERTS" ]; then
    # 这里可以添加飞书通知
    echo "$(date): 发现告警: $ALERTS" >> /root/.openclaw/logs/deepseek_alerts.log
fi
"""
    
    cron_file = "/root/.openclaw/workspace/skills/deepseek_monitor_cron.sh"
    with open(cron_file, 'w') as f:
        f.write(cron_script)
    
    os.chmod(cron_file, 0o755)
    
    print(f"\n📅 Cron脚本已创建: {cron_file}")
    print("添加cron任务:")
    print(f"*/10 * * * * {cron_file}")
    
    return cron_file

def quick_commands():
    """快速命令"""
    return {
        "/deepseek_status": "查看DeepSeek使用状态",
        "/deepseek_report": "生成使用报告",
        "/deepseek_alerts": "检查告警",
        "/deepseek_thresholds": "设置阈值"
    }

if __name__ == "__main__":
    # 运行自动监控
    summary = auto_monitor_deepseek()
    
    # 设置cron监控
    setup_cron_monitoring()
    
    print("\n" + "=" * 50)
    print("🚀 DeepSeek监控系统部署完成")
    print("\n可用命令:")
    for cmd, desc in quick_commands().items():
        print(f"  {cmd}: {desc}")
    
    print("\n监控文件位置:")
    print(f"  日志目录: /root/.openclaw/logs/")
    print(f"  使用记录: /root/.openclaw/logs/deepseek_usage.json")
    print(f"  每日日志: /root/.openclaw/logs/deepseek_daily_YYYYMMDD.json")