# 豆包视频分析技能

基于火山引擎豆包大模型的视频内容分析技能，专为OpenClaw设计。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install openai requests pillow opencv-python moviepy
```

### 2. 配置API Key
```bash
# 设置环境变量
export ARK_API_KEY="your_api_key_here"

# 或者创建配置文件
cp config.example.json config.json
# 编辑config.json，填入你的API Key
```

### 3. 基本使用
```python
from analyze_video import analyze_video

# 快速分析
result = analyze_video("your_video.mp4")
print(result)

# 详细分析
from analyze_video import VideoAnalyzer
analyzer = VideoAnalyzer()
detailed_result = analyzer.analyze_detailed("your_video.mp4")
print(detailed_result.to_markdown())
```

### 4. 命令行使用
```bash
# 快速分析
python analyze_video.py your_video.mp4

# 详细分析
python analyze_video.py your_video.mp4 --detailed

# 自定义提示词
python analyze_video.py your_video.mp4 --prompt "请分析视频中的动作"

# 输出JSON格式
python analyze_video.py your_video.mp4 --output-format json
```

## 📋 功能特性

### 支持的分析类型
1. **快速摘要** - 用一段话概括视频主要内容
2. **详细分析** - 完整的视频分析（场景、事件、物体、技术评价）
3. **事件分析** - 提取关键事件时间线
4. **技术分析** - 分析视频技术特征和质量
5. **自定义分析** - 使用自定义提示词

### 支持的视频格式
- MP4 (.mp4)
- AVI (.avi) 
- MOV (.mov)

### 输出格式
- 纯文本 (text)
- JSON格式 (json)
- Markdown报告 (markdown)

## 🔧 集成到OpenClaw

### 作为独立技能使用
```python
from skills.doubao_video_analyzer.openclaw_integration import DoubaoVideoSkill

# 初始化技能
skill = DoubaoVideoSkill(config={
    "api_key": "your_api_key",
    "output_dir": "./analysis_results"
})

# 分析视频
result = await skill.analyze_video_file(
    video_path="video.mp4",
    analysis_type="detailed",
    output_format="markdown"
)
```

### 自动触发分析
在OpenClaw配置中添加：
```yaml
skills:
  doubao_video_analyzer:
    enabled: true
    auto_analyze: true
    watch_directories:
      - /path/to/videos
    analysis_type: detailed
    output_format: markdown
```

### 处理飞书上传的视频
```python
async def handle_feishu_video(file_key, file_path):
    """处理从飞书上传的视频"""
    skill = DoubaoVideoSkill()
    
    # 分析视频
    result = await skill.analyze_video_file(
        video_path=file_path,
        analysis_type="detailed"
    )
    
    if result["success"]:
        # 将分析结果发送回飞书
        await send_to_feishu(
            message=result["result"]["markdown"],
            file_key=file_key
        )
    else:
        await send_to_feishu(
            message=f"视频分析失败: {result['error']}",
            file_key=file_key
        )
```

## 📊 分析报告示例

### Markdown报告
```markdown
# 视频分析报告

## 内容摘要
[视频内容摘要...]

## 场景分析
1. **00:00:00 - 00:00:10**
   - 描述: [场景描述]
   - 物体: [物体列表]
   - 动作: [动作列表]

2. **00:00:10 - 00:00:20**
   - 描述: [场景描述]
   - 物体: [物体列表]
   - 动作: [动作列表]

## 关键事件
- **00:01:30**: [事件描述] (重要性: 高)
- **00:02:45**: [事件描述] (重要性: 中)

## 识别物体
[物体1], [物体2], [物体3]

## 技术分析
- **画面质量**: [评价]
- **音频质量**: [评价]
- **制作水平**: [评价]
- **改进建议**: [建议]

## 元数据
- **视频文件**: video.mp4
- **分辨率**: 1920x1080
- **时长**: 120秒
- **文件大小**: 50.2MB
- **分析时间**: 2024-01-01T12:00:00
- **使用模型**: doubao-seed-1-6-251015
```

## ⚙️ 配置选项

### 主要配置
```json
{
  "api_key": "your_api_key",
  "base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "model": "doubao-seed-1-6-251015",
  "timeout": 300,
  "output_dir": "./video_analysis_output"
}
```

### 环境变量
```bash
export ARK_API_KEY="your_api_key"
export DOUBAO_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
export DOUBAO_MODEL="doubao-seed-1-6-251015"
export DOUBAO_TIMEOUT="300"
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python test_analyzer.py

# 创建示例视频并测试
python test_analyzer.py --create-sample
```

### 测试内容
1. 视频信息提取测试
2. 快速分析测试
3. 详细分析测试
4. 事件分析测试
5. 自定义提示词测试

## 📁 文件结构
```
doubao-video-analyzer/
├── SKILL.md                    # 技能说明文档
├── analyze_video.py           # 主分析脚本
├── openclaw_integration.py    # OpenClaw集成
├── test_analyzer.py           # 测试脚本
├── config.example.json        # 配置示例
├── README.md                  # 使用说明
└── requirements.txt           # 依赖列表
```

## ⚠️ 注意事项

### 限制
1. 单个视频文件最大 **512MB**
2. 不支持音频内容分析（豆包模型限制）
3. 需要稳定的网络连接
4. API调用有频率限制

### 隐私和安全
1. 视频上传后会被火山引擎服务器处理
2. 处理完成后视频文件会被删除
3. 用户数据不会被用于模型训练

### 最佳实践
1. 先测试小视频文件
2. 使用合适的分析提示词
3. 处理大视频时显示进度
4. 保存分析结果供后续使用

## 🔍 故障排除

### 常见问题
1. **API Key错误**：检查API Key是否正确，是否有访问权限
2. **视频格式不支持**：确保视频格式为MP4、AVI或MOV
3. **文件大小超限**：压缩视频或分割大文件
4. **网络连接问题**：检查网络连接，尝试使用代理

### 错误代码
- `ERR_API_KEY`: API Key错误
- `ERR_VIDEO_FORMAT`: 视频格式不支持
- `ERR_FILE_SIZE`: 文件大小超限
- `ERR_NETWORK`: 网络连接错误
- `ERR_PROCESSING`: 视频处理错误

## 📈 性能优化

### 视频预处理
- 自动检测视频格式
- 优化视频分辨率（如需要）
- 提取关键帧进行分析

### 缓存机制
- 缓存已分析视频的结果
- 支持增量分析
- 结果持久化存储

## 🤝 贡献

### 开发指南
1. Fork本仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试
- 更新文档

## 📄 许可证

MIT License

## 📞 支持

如有问题，请：
1. 查看[火山引擎官方文档](https://www.volcengine.com/docs/82379)
2. 提交GitHub Issue
3. 联系OpenClaw社区

## 🎯 使用场景

### 内容创作
- 自动生成视频描述
- 提取视频关键帧
- 分析视频质量

### 媒体管理
- 自动分类视频
- 提取元数据
- 生成缩略图描述

### 教育培训
- 分析教学视频内容
- 提取知识点
- 生成学习摘要

### 安防监控
- 分析监控视频
- 检测异常事件
- 生成事件报告