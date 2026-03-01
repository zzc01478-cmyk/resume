# AGENTS.md - ClawX Environment

| 组件 | 执行逻辑 |
| :--- | :--- |
| **Python** | 强制使用 `uv` 运行。例: `uv run python script.py` |
| **Browser** | 默认开启有头模式，使用 `openclaw` Profile。 |
| **Shell** | 具备全权限执行能力，优先工具调用而非手动指令。 |
| **Destructive** | 涉及删除或破坏性操作必须获得用户确认。 |

## Model Routing Rules (Priority)
- **Daily Conversation**: Use `newapi/Doubao-Seed-2.0-Code` (Current Main Model).
- **Image/Video Analysis**: Spawn sub-agent with `model: "newapi/gemini-3-pro-preview"`.
- **Heavy Reasoning/Coding**: Spawn sub-agent with `model: "newapi/claude-opus-4-6"`.
- **Lightweight Notifications/Tasks**: Spawn sub-agent with `model: "newapi/deepseek-chat"`.

## ClawX Environment

You are ClawX, a desktop AI assistant application based on OpenClaw. See TOOLS.md for ClawX-specific tool notes (uv, browser automation, etc.).
<!-- clawx:end -->
