# 豆包视频分析技能

## 概述
使用火山引擎豆包大模型进行视频内容分析的技能。支持上传视频文件，自动分析视频内容，并返回详细的文字分析报告。

## 功能特性
- ✅ 支持多种视频格式（MP4、AVI、MOV）
- ✅ 自动视频上传和处理
- ✅ 视频内容深度分析
- ✅ 时序事件识别
- ✅ 结构化输出
- ✅ 支持流式响应

## 前置要求
1. **火山引擎账号**：需要注册火山引擎账号
2. **API Key**：获取豆包模型的API Key
3. **Python环境**：需要安装必要的Python包

## 安装依赖
```bash
pip install openai requests pillow opencv-python moviepy
```

## 配置API Key
在环境变量中设置豆包API Key：
```bash
export ARK_API_KEY="your_api_key_here"
```

或者在代码中直接配置：
```python
api_key = "your_api_key_here"
base_url = "https://ark.cn-beijing.volces.com/api/v3"
```

## 使用方法

### 基本使用
```python
from doubao_video_analyzer import analyze_video

# 分析视频文件
result = analyze_video(
    video_path="path/to/your/video.mp4",
    prompt="请分析这个视频的主要内容",
    model="doubao-seed-1-6-251015"
)

print(result)
```

### 高级使用
```python
from doubao_video_analyzer import VideoAnalyzer

# 创建分析器实例
analyzer = VideoAnalyzer(
    api_key="your_api_key",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 上传并分析视频
analysis = analyzer.analyze(
    video_path="video.mp4",
    analysis_type="detailed",  # detailed, summary, events, objects
    output_format="json"       # json, text, markdown
)

# 获取分析结果
print(analysis.get_summary())
print(analysis.get_events())
print(analysis.get_objects())
```

## 分析类型

### 1. 内容摘要分析
分析视频的主要内容、主题和关键信息。

### 2. 详细场景分析
逐帧分析视频内容，识别场景、人物、动作等。

### 3. 事件时间线分析
提取视频中的关键事件，生成时间线。

### 4. 物体识别分析
识别视频中出现的物体和元素。

## 示例分析提示词

### 通用分析
```
请分析这个视频的主要内容，包括：
1. 视频主题和核心信息
2. 主要场景和背景
3. 人物或物体的动作
4. 情感氛围和风格
5. 制作质量评价
```

### 事件分析
```
请提取视频中的关键事件，以JSON格式输出：
- 开始时间（HH:mm:ss格式）
- 结束时间
- 事件描述
- 重要性（高/中/低）
- 涉及的人物或物体
```

### 技术分析
```
请分析视频的技术特征：
1. 视频质量（分辨率、帧率、编码）
2. 视觉风格（色调、亮度、对比度）
3. 音频特征（音量、音质、背景音）
4. 制作水平评价
5. 改进建议
```

## 输出格式

### JSON格式
```json
{
  "summary": "视频内容摘要",
  "scenes": [
    {
      "start_time": "00:00:00",
      "end_time": "00:00:10",
      "description": "场景描述",
      "objects": ["物体1", "物体2"],
      "actions": ["动作1", "动作2"]
    }
  ],
  "events": [
    {
      "time": "00:01:30",
      "description": "事件描述",
      "importance": "high"
    }
  ],
  "technical_analysis": {
    "video_quality": "评价",
    "audio_quality": "评价",
    "production_level": "评价"
  }
}
```

### 文本格式
```
视频分析报告
=============

一、内容摘要
[摘要内容]

二、场景分析
1. 00:00:00-00:00:10 [场景描述]
2. 00:00:10-00:00:20 [场景描述]

三、关键事件
- 00:01:30 [事件描述]
- 00:02:45 [事件描述]

四、技术评价
[技术评价]
```

## 错误处理

### 常见错误
1. **API Key错误**：检查API Key是否正确
2. **视频格式不支持**：确保视频格式为MP4、AVI或MOV
3. **文件大小超限**：视频文件不能超过512MB
4. **网络连接问题**：检查网络连接

### 错误代码
- `ERR_API_KEY`: API Key错误
- `ERR_VIDEO_FORMAT`: 视频格式不支持
- `ERR_FILE_SIZE`: 文件大小超限
- `ERR_NETWORK`: 网络连接错误
- `ERR_PROCESSING`: 视频处理错误

## 性能优化

### 视频预处理
- 自动检测视频格式
- 优化视频分辨率（如需要）
- 提取关键帧进行分析

### 缓存机制
- 缓存已分析视频的结果
- 支持增量分析
- 结果持久化存储

## 集成到OpenClaw

### 作为技能使用
```python
# 在OpenClaw技能中调用
from skills.doubao_video_analyzer import analyze_video

async def handle_video_analysis(video_path, user_prompt):
    result = await analyze_video(video_path, user_prompt)
    return result
```

### 自动触发
配置OpenClaw自动检测视频文件并进行分析：
```yaml
# 在配置文件中添加
video_analysis:
  auto_analyze: true
  supported_formats: [".mp4", ".avi", ".mov"]
  output_format: "markdown"
```

## 注意事项

### 隐私和安全
1. 视频上传后会被火山引擎服务器处理
2. 处理完成后视频文件会被删除
3. 用户数据不会被用于模型训练

### 使用限制
1. 单个视频文件最大512MB
2. 不支持音频内容分析
3. 需要稳定的网络连接
4. API调用有频率限制

### 最佳实践
1. 先测试小视频文件
2. 使用合适的分析提示词
3. 处理大视频时显示进度
4. 保存分析结果供后续使用

## 更新日志

### v1.0.0 (初始版本)
- 支持基本视频分析功能
- 支持多种输出格式
- 集成错误处理机制
- 提供完整的API文档

## 技术支持
如有问题，请参考：
1. 火山引擎官方文档
2. GitHub Issues页面
3. 社区讨论区

## 许可证
MIT License