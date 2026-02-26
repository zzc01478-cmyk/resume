#!/usr/bin/env python3
"""
DeepSeek API使用监控
监控token使用、成本、频率等
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class DeepSeekMonitor:
    """DeepSeek API监控器"""
    
    def __init__(self, log_dir=None):
        self.log_dir = log_dir or Path.home() / ".openclaw" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 监控文件
        self.usage_file = self.log_dir / "deepseek_usage.json"
        self.daily_file = self.log_dir / f"deepseek_daily_{datetime.now().strftime('%Y%m%d')}.json"
        
        # 初始化使用记录
        self._init_usage()
    
    def _init_usage(self):
        """初始化使用记录"""
        if not self.usage_file.exists():
            self.usage_data = {
                "total_tokens": 0,
                "total_cost": 0.0,
                "daily_usage": {},
                "model_usage": {},
                "last_update": datetime.now().isoformat()
            }
            self._save_usage()
        else:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                self.usage_data = json.load(f)
    
    def _save_usage(self):
        """保存使用记录"""
        self.usage_data["last_update"] = datetime.now().isoformat()
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
    
    def record_usage(self, input_tokens, output_tokens, model="deepseek-chat", cost=0.0):
        """
        记录API使用
        
        Args:
            input_tokens: 输入token数
            output_tokens: 输出token数
            model: 模型名称
            cost: 成本（美元）
        """
        today = datetime.now().strftime("%Y%m%d")
        total_tokens = input_tokens + output_tokens
        
        # 更新总使用
        self.usage_data["total_tokens"] += total_tokens
        self.usage_data["total_cost"] += cost
        
        # 更新每日使用
        if today not in self.usage_data["daily_usage"]:
            self.usage_data["daily_usage"][today] = {
                "tokens": 0,
                "cost": 0.0,
                "requests": 0
            }
        
        self.usage_data["daily_usage"][today]["tokens"] += total_tokens
        self.usage_data["daily_usage"][today]["cost"] += cost
        self.usage_data["daily_usage"][today]["requests"] += 1
        
        # 更新模型使用
        if model not in self.usage_data["model_usage"]:
            self.usage_data["model_usage"][model] = {
                "tokens": 0,
                "cost": 0.0,
                "requests": 0
            }
        
        self.usage_data["model_usage"][model]["tokens"] += total_tokens
        self.usage_data["model_usage"][model]["cost"] += cost
        self.usage_data["model_usage"][model]["requests"] += 1
        
        # 保存
        self._save_usage()
        
        # 记录详细日志
        self._log_detailed(input_tokens, output_tokens, model, cost)
        
        return True
    
    def _log_detailed(self, input_tokens, output_tokens, model, cost):
        """记录详细日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "cost_per_token": cost / (input_tokens + output_tokens) if (input_tokens + output_tokens) > 0 else 0
        }
        
        # 追加到每日文件
        with open(self.daily_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_summary(self):
        """获取使用摘要"""
        today = datetime.now().strftime("%Y%m%d")
        today_usage = self.usage_data["daily_usage"].get(today, {})
        
        # 计算趋势
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        yesterday_usage = self.usage_data["daily_usage"].get(yesterday, {})
        
        return {
            "total": {
                "tokens": self.usage_data["total_tokens"],
                "cost": self.usage_data["total_cost"],
                "requests": sum(day["requests"] for day in self.usage_data["daily_usage"].values())
            },
            "today": today_usage,
            "yesterday": yesterday_usage,
            "models": self.usage_data["model_usage"],
            "last_update": self.usage_data["last_update"]
        }
    
    def check_thresholds(self, thresholds=None):
        """
        检查使用阈值
        
        Args:
            thresholds: 阈值配置
                daily_tokens: 每日token上限
                daily_cost: 每日成本上限
                warning_percent: 警告百分比
        """
        if thresholds is None:
            thresholds = {
                "daily_tokens": 100000,  # 10万token/天
                "daily_cost": 1.0,       # 1美元/天
                "warning_percent": 80    # 80%时警告
            }
        
        today = datetime.now().strftime("%Y%m%d")
        today_usage = self.usage_data["daily_usage"].get(today, {})
        
        alerts = []
        
        # 检查token使用
        if today_usage.get("tokens", 0) > thresholds["daily_tokens"]:
            alerts.append({
                "level": "ERROR",
                "message": f"今日token使用超过上限: {today_usage['tokens']}/{thresholds['daily_tokens']}"
            })
        elif today_usage.get("tokens", 0) > thresholds["daily_tokens"] * thresholds["warning_percent"] / 100:
            alerts.append({
                "level": "WARNING",
                "message": f"今日token使用接近上限: {today_usage['tokens']}/{thresholds['daily_tokens']}"
            })
        
        # 检查成本
        if today_usage.get("cost", 0) > thresholds["daily_cost"]:
            alerts.append({
                "level": "ERROR",
                "message": f"今日成本超过上限: ${today_usage['cost']:.4f}/${thresholds['daily_cost']}"
            })
        elif today_usage.get("cost", 0) > thresholds["daily_cost"] * thresholds["warning_percent"] / 100:
            alerts.append({
                "level": "WARNING",
                "message": f"今日成本接近上限: ${today_usage['cost']:.4f}/${thresholds['daily_cost']}"
            })
        
        return alerts
    
    def generate_report(self, days=7):
        """生成使用报告"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        report = {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "daily_summary": [],
            "model_summary": self.usage_data["model_usage"],
            "total": {
                "tokens": self.usage_data["total_tokens"],
                "cost": self.usage_data["total_cost"]
            }
        }
        
        # 按日汇总
        for date_str, usage in self.usage_data["daily_usage"].items():
            date = datetime.strptime(date_str, "%Y%m%d")
            if start_date <= date <= end_date:
                report["daily_summary"].append({
                    "date": date.strftime("%Y-%m-%d"),
                    "tokens": usage["tokens"],
                    "cost": usage["cost"],
                    "requests": usage["requests"]
                })
        
        return report

# 使用示例
if __name__ == "__main__":
    monitor = DeepSeekMonitor()
    
    # 模拟记录使用
    monitor.record_usage(
        input_tokens=208,
        output_tokens=786,
        model="deepseek-chat",
        cost=0.0000  # 假设免费
    )
    
    # 获取摘要
    summary = monitor.get_summary()
    print("使用摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # 检查阈值
    alerts = monitor.check_thresholds()
    if alerts:
        print("\n告警:")
        for alert in alerts:
            print(f"{alert['level']}: {alert['message']}")
    
    # 生成报告
    report = monitor.generate_report(days=7)
    print("\n7天报告已生成")