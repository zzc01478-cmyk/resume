# DOM Compressor Skill (增强版)

## Description
AI Agent 专用的 DOM 压缩工具，能将网页 HTML 压缩为精简的结构化文本，大幅降低 Token 消耗（平均 60-80%）。支持连接已启动的 Chrome 调试端口（CDP）或直接传入 HTML 字符串。增强版支持图片信息提取和可配置的压缩模式。

## Capability
- **网页压缩**：将任意网页 HTML 压缩为 AI 可读的精简结构
- **Token 节省**：平均降低 60-80% 的 Token 消耗
- **图片提取**：可选择提取图片 URL、alt 文本等元数据
- **多模式支持**：纯文本模式、图片元数据模式、完整模式
- **CDP 连接**：支持通过 Chrome 调试端口（127.0.0.1:9222）直接读取当前页面

## Trigger Keywords
- "压缩网页"
- "dom压缩"
- "token优化"
- "compress html"
- "减少token"
- "网页摘要"
- "提取图片"

## 智能选择策略

根据分析需求选择合适的压缩模式：

| 需求场景 | 推荐工具 | 图片处理 | 压缩率 | Token消耗 |
|----------|----------|----------|--------|-----------|
| **纯文本分析**（内容摘要、文章提取） | `dom-compressor-modified.js` | 完全丢弃 | 70-85% | 最低 |
| **页面结构分析**（链接、表单、交互） | `dom-compressor-modified.js` | 完全丢弃 | 60-75% | 低 |
| **图片元数据提取**（知道有哪些图片） | `dom-compressor-with-images.js` | 提取URL、alt、title | 50-70% | 中 |
| **视觉元素识别**（图片是内容核心） | `dom-compressor-with-images.js` | 提取完整元数据 | 40-60% | 中高 |
| **CDP实时页面分析** | 使用CDP连接代码 | 可配置 | 依赖页面 | 依赖页面 |

### 决策流程
1. **是否需要图片信息？**
   - 否 → 使用 `dom-compressor-modified.js`（纯文本模式）
   - 是 → 继续判断

2. **需要什么级别的图片理解？**
   - 仅需知道有图片 → `dom-compressor-with-images.js`（默认参数）
   - 需要图片详细描述 → `dom-compressor-with-images.js`（`maxImages: 20`）
   - 需要分析图片内容 → 额外工具（非压缩工具职责）

3. **页面是否动态渲染？**
   - 是 → 考虑CDP连接模式
   - 否 → 直接压缩HTML

### 可用脚本
- **`dom-compressor.js`** - 原始版本（可能丢失图片，不推荐）
- **`dom-compressor-modified.js`** - 修复版（修复了交互元素提取问题，推荐用于纯文本）
- **`dom-compressor-with-images.js`** - 增强版（支持图片提取，推荐用于视觉分析）

### 压缩模式
1. **纯文本模式**：仅提取文本和交互元素，压缩率最高
2. **图片元数据模式**：提取图片URL、alt文本等元数据
3. **完整模式**：包含所有元素（开发中）

## 增强版使用示例

### 1. 使用增强版压缩HTML文件（包含图片）
```bash
# 包含图片信息
node dom-compressor-with-images.js input.html

# 不包含图片信息
node dom-compressor-with-images.js input.html --no-images

# 限制图片数量
node -e "
const { compressHTMLString } = require('./dom-compressor-with-images.js');
const fs = require('fs');
const html = fs.readFileSync('input.html', 'utf8');
const result = compressHTMLString(html, { 
  includeImages: true, 
  maxImages: 10,
  maxTextLength: 1500,
  maxActions: 20 
});
console.log(result.compressed);
"
```

### 2. 使用修复版压缩HTML文件
```bash
node dom-compressor-modified.js input.html
```

### 3. 压缩输出格式示例
```text
[TITLE] 页面标题
[SUMMARY] 主要文本内容摘要...
[IMAGES]
[IMG] alt="图片描述" title="图片标题" src="https://example.com/image.jpg" size=300x200
[IMG] alt="缩略图" src="https://example.com/thumb.jpg" [in link -> https://example.com/page]
[BG-IMG] src="https://example.com/bg.jpg"
[ACTIONS]
[LINK] 链接文本 -> https://example.com/page
[BTN] 按钮文本
[INPUT] name=username placeholder=用户名
[SELECT] country [中国,美国,日本]
[TEXTAREA] comments
```

## Action

### 1. 连接浏览器并压缩当前页面（推荐）
如果用户已启动 Chrome 调试端口（`--remote-debugging-port=9222`），使用以下代码：

```javascript
const { chromium } = require('playwright');

async function compressCurrentPage(cdpUrl = 'http://127.0.0.1:9222') {
    const browser = await chromium.connectOverCDP(cdpUrl);
    const page = browser.contexts()[0].pages()[0];
    
    const html = await page.content();
    const title = await page.title();
    const url = page.url();
    
    // 获取可见文本
    let mainText = '';
    try {
        mainText = await page.innerText('body', { timeout: 3000 });
    } catch (e) {
        mainText = await page.evaluate(() => document.body.innerText);
    }
    const cleanText = mainText.slice(0, 1200).replace(/\s+/g, ' ').trim();
    
    // 获取交互元素
    const interactive = [];
    
    // 链接
    const links = await page.$$eval('a[href]', els => 
        els.filter(e => e.href && !e.href.startsWith('javascript') && !e.href.startsWith('#'))
           .slice(0, 15)
           .map(e => '[LINK] ' + (e.textContent?.trim().slice(0,40) || 'unnamed') + ' -> ' + e.href)
    );
    interactive.push(...links);
    
    // 按钮
    const buttons = await page.$$eval('button, input[type=submit]', els => 
        els.slice(0, 10).map(e => '[BTN] ' + (e.textContent?.trim().slice(0,40) || e.value || 'unnamed'))
    );
    interactive.push(...buttons);
    
    // 输入框
    const inputs = await page.$$eval('input[placeholder], input[name]', els => 
        els.slice(0, 10).map(e => '[INPUT] ' + (e.name||e.id||'') + ' placeholder="' + (e.placeholder||'') + '"')
    );
    interactive.push(...inputs);
    
    const output = '[PAGE] ' + url + '\n[TITLE] ' + title + '\n[SUMMARY] ' + cleanText + '\n[ACTIONS]\n' + interactive.join('\n');
    
    const originalSize = Buffer.byteLength(html, 'utf8');
    const compressedSize = Buffer.byteLength(output, 'utf8');
    
    console.log('=== Compression Result ===');
    console.log('Original:', originalSize, 'bytes');
    console.log('Compressed:', compressedSize, 'bytes');
    console.log('Reduction:', ((originalSize - compressedSize) / originalSize * 100).toFixed(2) + '%');
    console.log('\n=== Compressed Output ===');
    console.log(output);
    
    await browser.close();
    return output;
}

compressCurrentPage();
```

### 2. 直接压缩 HTML 字符串
如果已有 HTML 内容，使用以下代码：

```javascript
const { JSDOM } = require('jsdom');

function compressHTML(html) {
    const dom = new JSDOM(html);
    const doc = dom.window.document;
    
    // 移除脚本和样式
    doc.querySelectorAll('script, style, noscript, template, svg, canvas, iframe, link').forEach(el => el.remove());
    
    const title = doc.title || '';
    
    // 获取主要文本内容
    let mainContent = '';
    const mainSelectors = ['main', 'article', '.main', '#main', '.content', '#content', '.container'];
    for (const sel of mainSelectors) {
        const el = doc.querySelector(sel);
        if (el && el.textContent?.trim().length > 100) {
            mainContent = el.textContent.replace(/\s+/g, ' ').trim().slice(0, 1500);
            break;
        }
    }
    if (!mainContent) {
        mainContent = doc.body?.textContent?.replace(/\s+/g, ' ').trim().slice(0, 1500) || '';
    }
    
    // 提取交互元素
    const interactive = [];
    doc.querySelectorAll('a, button, input, select').forEach(el => {
        if (el.offsetParent === null) return; // 跳过隐藏元素
        const tag = el.tagName.toLowerCase();
        const text = el.textContent?.trim().slice(0, 50);
        const placeholder = el.getAttribute('placeholder')?.slice(0, 50);
        const href = el.getAttribute('href');
        const name = el.getAttribute('name') || el.getAttribute('id') || '';
        
        if (tag === 'a' && href && !href.startsWith('javascript')) {
            interactive.push('[LINK] ' + (text || 'unnamed') + ' -> ' + href);
        } else if (tag === 'button' && text) {
            interactive.push('[BTN] ' + text);
        } else if (tag === 'input' && (placeholder || name)) {
            interactive.push('[INPUT] name=' + name + ' placeholder=' + (placeholder || ''));
        }
    });
    
    const output = '[TITLE] ' + title + '\n[SUMMARY] ' + mainContent + '\n[ACTIONS]\n' + interactive.join('\n');
    
    const originalSize = Buffer.byteLength(html, 'utf8');
    const compressedSize = Buffer.byteLength(output, 'utf8');
    
    return {
        compressed: output,
        stats: {
            originalSize,
            compressedSize,
            reduction: ((originalSize - compressedSize) / originalSize * 100).toFixed(2) + '%'
        }
    };
}

// 使用示例
// const result = compressHTML('<html>...</html>');
// console.log(result.stats);
// console.log(result.compressed);
```

## Notes
- **依赖安装**：需要先安装依赖：`npm install playwright jsdom`
- **Chrome调试模式**：Chrome 需以调试模式启动：`chrome.exe --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome-debug"`
- **压缩参数**：
  - 推荐压缩后保留 1200-1500 字符的主要内容，过多会影响 AI 理解
  - 交互元素建议保留 15-20 个
  - 图片建议保留 10-15 个（如启用图片提取）
- **增强版注意事项**：
  - `dom-compressor-with-images.js` 支持图片元数据提取
  - 原始版本可能因 `offsetParent` 检查而丢失交互元素（在jsdom环境中无效）
  - 修复版（modified）移除了 `offsetParent` 检查，确保提取所有交互元素
  - 图片提取会增加 Token 消耗，根据需求选择是否启用
- **图片理解层次**：
  - **层级1：知道有图片** - 提取图片URL、alt文本、title（当前工具支持）
  - **层级2：理解图片内容** - 需要额外工具下载并分析图片（超出压缩工具范围）
  - **层级3：完全不压缩图片** - 保留原始图片标签和属性（可定制开发）
- **Token节省效果**：
  - 纯文本模式：压缩率 70-85%，Token节省显著
  - 图片元数据模式：压缩率 50-70%，保留视觉元素信息
  - 大型页面压缩效果更明显（100KB → 1-3KB）
- **已知限制**：
  - SVG 和 Canvas 元素会被过滤（被视为非文本元素）
  - 动态渲染页面可能需要CDP连接模式
  - 隐藏元素可能被提取（需进一步优化可见性检查）
  - 图片像素内容无法通过压缩工具获取（需要专门的图像分析工具）
