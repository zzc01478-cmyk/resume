#!/usr/bin/env python3
"""
/status命令配置系统
"""

import sys
from custom_status import CustomStatus

def handle_status_command(args):
    """处理/status命令"""
    status = CustomStatus()
    
    if not args:
        # 默认显示
        return status.generate_status()
    
    command = args[0].lower()
    
    if command == "help":
        return get_help()
    
    elif command == "config":
        return handle_config(args[1:], status)
    
    elif command == "mode":
        return handle_mode(args[1:], status)
    
    elif command == "add":
        return handle_add(args[1:], status)
    
    elif command == "remove":
        return handle_remove(args[1:], status)
    
    elif command == "list":
        return handle_list(status)
    
    elif command == "reset":
        return handle_reset(status)
    
    else:
        # 尝试作为模式处理
        return status.generate_status(command)

def handle_config(args, status):
    """处理配置命令"""
    if not args:
        return "请指定配置项，如：/status config basic on"
    
    if len(args) < 2:
        return "需要两个参数：配置项和值"
    
    section = args[0]
    value = args[1].lower()
    
    if value in ["on", "true", "yes", "1"]:
        enabled = True
    elif value in ["off", "false", "no", "0"]:
        enabled = False
    else:
        return f"无效的值：{value}，请使用 on/off"
    
    if status.update_section(section, enabled):
        return f"✅ 已更新 {section} = {value}"
    else:
        return f"❌ 未知配置项：{section}"

def handle_mode(args, status):
    """处理模式命令"""
    if not args:
        return "请指定模式，如：/status mode basic"
    
    mode = args[0]
    valid_modes = ["basic", "full", "api", "services", "minimal"]
    
    if mode not in valid_modes:
        return f"❌ 无效模式：{mode}，可用：{', '.join(valid_modes)}"
    
    return status.generate_status(mode)

def handle_add(args, status):
    """处理添加命令"""
    if not args:
        return "请指定要添加的自定义部分名称"
    
    section_name = args[0]
    
    # 这里应该添加实际的函数
    # 暂时只记录名称
    if status.add_custom_section(section_name, None):
        return f"✅ 已添加自定义部分：{section_name}"
    else:
        return f"❌ 添加失败"

def handle_remove(args, status):
    """处理移除命令"""
    if not args:
        return "请指定要移除的部分名称"
    
    # 这里需要实现移除逻辑
    return f"移除功能待实现"

def handle_list(status):
    """列出所有配置"""
    sections = status.config["sections"]
    
    result = "📋 状态显示配置：\n\n"
    
    result += "**基础部分**：\n"
    for section, enabled in sections.items():
        if section != "custom":
            icon = "✅" if enabled else "❌"
            result += f"  {icon} {section}\n"
    
    result += "\n**自定义部分**：\n"
    for custom in sections.get("custom", []):
        result += f"  ✨ {custom}\n"
    
    result += f"\n**格式**：{status.config['format']}\n"
    result += f"**表情**：{'开启' if status.config['show_emoji'] else '关闭'}\n"
    result += f"**自动刷新**：{'开启' if status.config['auto_refresh'] else '关闭'}"
    
    return result

def handle_reset(status):
    """重置配置"""
    # 这里需要实现重置逻辑
    return "重置功能待实现"

def get_help():
    """获取帮助信息"""
    return """
🎯 **/status 命令配置系统**

**基本用法**：
  /status                 # 默认显示
  /status basic          # 基础信息
  /status full           # 完整信息
  /status api            # API统计
  /status services       # 服务状态
  /status minimal        # 最小信息

**配置命令**：
  /status config <部分> <on/off>  # 配置显示部分
  /status mode <模式>            # 切换显示模式
  /status add <名称>             # 添加自定义部分
  /status list                  # 列出所有配置
  /status help                  # 显示此帮助

**可配置部分**：
  basic          - 基础信息（系统、模型、目录等）
  api_stats      - API使用统计
  service_status - 服务状态（天气、语音、飞书等）
  alerts         - 告警信息
  tools          - 工具列表
  memory         - 内存使用
  network        - 网络状态
  tasks          - 任务队列

**示例**：
  /status config api_stats off    # 关闭API统计
  /status config service_status on # 开启服务状态
  /status mode full               # 切换到完整模式
"""

# 集成到OpenClaw
def integrate_with_openclaw():
    """集成到OpenClaw"""
    integration_code = '''
# 在OpenClaw的指令处理中添加：
if command.startswith("/status"):
    args = command.split()[1:] if len(command.split()) > 1 else []
    from status_config_commands import handle_status_command
    return handle_status_command(args)
'''
    
    print("集成代码：")
    print(integration_code)
    
    return integration_code

if __name__ == "__main__":
    # 测试
    if len(sys.argv) > 1:
        result = handle_status_command(sys.argv[1:])
        print(result)
    else:
        print(handle_status_command([]))