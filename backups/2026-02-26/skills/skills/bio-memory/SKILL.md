---
name: bio-memory
description: "Bio-Memory Pro - 智能仿生记忆系统。自动检测关键信息、主动管理记忆、三层按需加载。Use when: (1) AI需要自动记录项目和待办, (2) 优化记忆加载性能, (3) 实现智能记忆管理, (4) 减少token消耗和卡死风险, (5) 让AI更主动、更自然地处理记忆"
---

# Bio-Memory Pro - 智能仿生记忆系统

让AI像人类一样思考：自动感知 → 智能分层 → 主动记忆

## 核心升级（v2.0）

### 🧠 智能检测引擎
不再等用户说"记住"，自动识别：
- **新项目**："我要开始写小说" → 自动记录
- **待办**："明天要开会" → 自动添加提醒
- **偏好**："我喜欢科幻" → 自动保存
- **决定**："确定用第一人称" → 自动归档
- **人物**："我表妹叫小红" → 自动记录

### 🎯 置信度分层
根据信息确定性，智能选择回应方式：
- **高置信度（>0.8）**：直接记录，事后自然提及
- **中置信度（0.5-0.8）**：自然确认，不给压力
- **低置信度（<0.5）**：轻松询问，避免误记

### ⚡ 三层记忆轨道
按需加载，最大化算力效率：

| 模式 | 标记 | 加载内容 | Token | 时间 |
|------|------|---------|-------|------|
| **瞬时** | `[q]` | 不读文件 | ~200 | 1-2秒 |
| **标准** | `[s]`/默认 | .snapshot | ~500 | 3-5秒 |
| **深度** | `[d]` | snapshot+按需 | 按需 | 5-10秒 |

---

## 快速开始

### 1. 安装

```bash
git clone https://github.com/yourname/bio-memory.git
cd bio-memory
python3 install.py
```

### 2. 初始化

```bash
# 自动创建目录结构和初始snapshot
python3 scripts/smart_snapshot.py --init
```

### 3. 使用

**对用户**：正常对话即可，AI会自动记录重要信息

**对AI开发者**：
```python
from bio_memory import ProactiveMemoryAssistant

assistant = ProactiveMemoryAssistant()

# 处理用户消息
result = assistant.process_message("我要开始写小说")
# 返回: {action: 'auto_record', confidence: 0.9, ...}

# 根据结果自然回应
if result['action'] == 'auto_record':
    print(f"好嘞！{result['finding']['name']}，我记下了。")
elif result['action'] == 'confirm':
    print(result['response'])  # "什么时候开始弄？"
```

---

## 智能检测规则

### 自动记录（高置信度）

```
用户: 我要开始写个新小说，叫《代码觉醒》
AI: 好嘞！《代码觉醒》，我记下了。
     [后台自动记录到 snapshot]

用户: 明天要交报告，记得提醒我
AI: 记下了，明天交报告。
     [后台自动添加待办]

用户: 我特别喜欢科幻题材
AI: 收到～
     [后台自动记录偏好]
```

### 自然确认（中置信度）

```
用户: 可能写个小说吧
AI: 写小说？什么时候开始弄？
     [等待用户确认后再记录]

用户: 下周也许要开会
AI: 下周开会？需要我提醒你吗？
     [根据用户回应决定是否记录]
```

### 轻松询问（低置信度）

```
用户: 写个小说？
AI: 写小说？认真的还是随口说说？
     [不确定，先问清楚]

用户: 我表哥... 算了不重要
AI: （不记录，用户说算了）
```

---

## 文件结构

```
memory/
├── .snapshot.md          # 🔥 核心快照（自动维护）
├── quick-ref.md          # 快速参考（可选）
├── active/               # 活跃项目
│   ├── novel/            # 小说项目
│   ├── project-a/        # 项目A
│   └── ...
├── people/               # 人物信息
├── archive/              # 归档（自动整理）
└── daily/                # 每日日志（自动生成）
    └── YYYY-MM-DD.md
```

---

## 配置选项

### 调整置信度阈值

编辑 `config.yaml`：

```yaml
confidence_thresholds:
  high: 0.8      # 直接记录
  medium: 0.5    # 自然确认
  low: 0.3       # 询问用户

auto_record:     # 自动记录设置
  enabled: true
  show_confirmation: false  # 是否显示"已记录"提示

projects:
  auto_archive_days: 30     # 30天无活动自动归档
```

### 自定义检测规则

编辑 `scripts/smart_snapshot.py` 中的检测器：

```python
def detect_custom_type(self, text: str) -> Optional[Dict]:
    """添加你的自定义检测规则"""
    if '你的关键词' in text:
        return {
            'type': 'custom_type',
            'data': ...
        }
    return None
```

---

## 与 OpenClaw 集成

### Hook 安装

复制 hook 到 OpenClaw hooks 目录：

```bash
cp hooks/bio-memory-hook.ts ~/.openclaw/hooks/
openclaw hooks enable bio-memory
```

### Hook 功能

- **对话开始时**：预加载 `.snapshot.md`
- **对话结束后**：自动分析并更新记忆
- **每日定时**：归档旧项目、生成周报

---

## 高级用法

### 手动更新 Snapshot

```bash
# 分析当前对话并更新
python3 scripts/smart_snapshot.py --analyze "我要开始新项目"

# 处理整个会话文件
python3 scripts/smart_snapshot.py --session session.json

# 查看当前 snapshot
python3 scripts/smart_snapshot.py --show
```

### 语义搜索（需要 embedding）

```bash
# 安装依赖
pip3 install sentence-transformers

# 启用语义搜索
python3 scripts/semantic_search.py --index

# 搜索
python3 scripts/semantic_search.py "小说项目"
```

### 生命周期管理

```bash
# 检查休眠项目
python3 scripts/lifecycle_manager.py --check

# 自动归档
python3 scripts/lifecycle_manager.py --auto-archive

# 生成周报
python3 scripts/weekly_report.py
```

---

## 性能指标

| 指标 | 传统系统 | Bio-Memory Pro |
|------|---------|----------------|
| 启动时间 | 5-10秒 | 1-4秒 |
| Token消耗 | 2000+ | 200-1500 |
| 卡死风险 | 高 | 低（分层保护）|
| 记忆连续性 | 依赖重读 | 自动维护 |
| 用户负担 | 需说"记住" | 自动检测 |

---

## 故障排除

### 记录太敏感/太迟钝

调整 `config.yaml` 中的置信度阈值：
- 太敏感（什么都记）→ 提高 `high` 阈值到 0.85
- 太迟钝（该记的不记）→ 降低 `high` 阈值到 0.75

### Snapshot 太大

```bash
# 手动清理
python3 scripts/lifecycle_manager.py --cleanup

# 或者编辑 .snapshot.md，删除旧项目
```

### 想禁用自动记录

```bash
# 临时禁用（单次对话）
用户: [disable-auto-memory]

# 永久禁用
编辑 config.yaml: auto_record.enabled: false
```

---

## 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

### 开发环境

```bash
git clone https://github.com/yourname/bio-memory.git
cd bio-memory
pip3 install -r requirements-dev.txt
python3 -m pytest tests/
```

---

## 版本历史

- **v2.0.0** - 智能检测 + 主动记忆 + 置信度分层
- **v1.0.0** - 基础三层轨道 + Snapshot机制

---

## License

MIT License - 自由使用和修改

---

**让AI像人类一样记忆，而不是像数据库一样查询。**
