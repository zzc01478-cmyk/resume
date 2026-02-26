#!/usr/bin/env node
/**
 * DOM智能压缩器 - 提取网页关键内容，减少token消耗
 */

const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

class DOMCompressor {
    constructor(configPath = '../config/config.json') {
        this.config = this.loadConfig(configPath);
        this.cache = new Map();
        this.stats = {
            totalCompressions: 0,
            totalBytesSaved: 0,
            averageReduction: 0
        };
    }
    
    loadConfig(configPath) {
        const fullPath = path.join(__dirname, configPath);
        if (fs.existsSync(fullPath)) {
            return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        }
        
        // 默认配置
        return {
            compression: {
                enabled: true,
                maxTextLength: 1500,
                extractActions: true,
                removeHidden: true,
                keepLinks: true,
                keepImages: false,
                keepCode: false,
                strategies: {
                    'news': { maxTextLength: 2000, keepImages: false },
                    'ecommerce': { maxTextLength: 1000, extractPrices: true },
                    'dashboard': { maxTextLength: 500, extractCharts: true },
                    'documentation': { maxTextLength: 3000, keepCode: true }
                }
            }
        };
    }
    
    /**
     * 压缩HTML内容
     */
    async compress(html, url = '', options = {}) {
        const startTime = Date.now();
        
        // 合并配置
        const config = { ...this.config.compression, ...options };
        
        // 检查缓存
        const cacheKey = this.getCacheKey(html, config);
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        try {
            // 创建DOM
            const dom = new JSDOM(html);
            const doc = dom.window.document;
            
            // 检测页面类型
            const pageType = this.detectPageType(doc, url);
            const strategy = this.getCompressionStrategy(pageType, config);
            
            // 执行压缩
            const result = this.executeCompression(doc, url, strategy);
            
            // 计算统计
            const originalSize = Buffer.byteLength(html, 'utf8');
            const compressedSize = Buffer.byteLength(result.compressed, 'utf8');
            const reduction = ((originalSize - compressedSize) / originalSize * 100);
            
            const finalResult = {
                ...result,
                stats: {
                    originalSize,
                    compressedSize,
                    reduction: reduction.toFixed(2) + '%',
                    bytesSaved: originalSize - compressedSize,
                    processingTime: Date.now() - startTime,
                    pageType,
                    strategy: strategy.name
                }
            };
            
            // 更新全局统计
            this.updateStats(finalResult);
            
            // 缓存结果
            this.cache.set(cacheKey, finalResult);
            
            return finalResult;
            
        } catch (error) {
            console.error('DOM压缩失败:', error.message);
            
            // 压缩失败时返回原始内容摘要
            return {
                compressed: this.createFallbackOutput(html, url),
                stats: {
                    originalSize: Buffer.byteLength(html, 'utf8'),
                    compressedSize: 0,
                    reduction: '0%',
                    bytesSaved: 0,
                    processingTime: Date.now() - startTime,
                    pageType: 'unknown',
                    strategy: 'fallback',
                    error: error.message
                }
            };
        }
    }
    
    /**
     * 检测页面类型
     */
    detectPageType(doc, url) {
        const html = doc.documentElement.outerHTML.toLowerCase();
        const title = doc.title?.toLowerCase() || '';
        const urlLower = url.toLowerCase();
        
        // 检查URL模式
        if (urlLower.includes('/news/') || urlLower.includes('/article/') || title.includes('news')) {
            return 'news';
        } else if (urlLower.includes('/product/') || urlLower.includes('/shop/') || html.includes('$') || html.includes('price')) {
            return 'ecommerce';
        } else if (urlLower.includes('/docs/') || urlLower.includes('/api/') || html.includes('code') || html.includes('example')) {
            return 'documentation';
        } else if (html.includes('chart') || html.includes('graph') || html.includes('dashboard')) {
            return 'dashboard';
        } else if (html.includes('login') || html.includes('signin') || html.includes('register')) {
            return 'auth';
        }
        
        return 'general';
    }
    
    /**
     * 获取压缩策略
     */
    getCompressionStrategy(pageType, config) {
        const strategies = config.strategies || {};
        const defaultStrategy = {
            name: 'general',
            maxTextLength: config.maxTextLength || 1500,
            extractActions: config.extractActions !== false,
            removeHidden: config.removeHidden !== false,
            keepLinks: config.keepLinks !== false,
            keepImages: config.keepImages === true,
            keepCode: config.keepCode === true,
            extractPrices: false,
            extractCharts: false
        };
        
        if (strategies[pageType]) {
            return { ...defaultStrategy, ...strategies[pageType], name: pageType };
        }
        
        return defaultStrategy;
    }
    
    /**
     * 执行压缩
     */
    executeCompression(doc, url, strategy) {
        // 移除无用元素
        if (strategy.removeHidden) {
            this.removeHiddenElements(doc);
        }
        
        this.removeUnwantedElements(doc, strategy);
        
        // 提取关键信息
        const title = this.extractTitle(doc);
        const summary = this.extractSummary(doc, strategy.maxTextLength);
        const actions = strategy.extractActions ? this.extractActions(doc) : [];
        const metadata = this.extractMetadata(doc, strategy);
        
        // 构建压缩输出
        const compressed = this.buildCompressedOutput({
            url,
            title,
            summary,
            actions,
            metadata,
            strategy
        });
        
        return {
            compressed,
            structured: {
                url,
                title,
                summary,
                actions,
                metadata,
                pageType: strategy.name
            }
        };
    }
    
    /**
     * 移除隐藏元素
     */
    removeHiddenElements(doc) {
        // 移除display:none或visibility:hidden的元素
        const elements = doc.querySelectorAll('*');
        elements.forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') {
                el.remove();
            }
        });
    }
    
    /**
     * 移除不需要的元素
     */
    removeUnwantedElements(doc, strategy) {
        const selectors = [
            'script', 'style', 'noscript', 'template', 
            'iframe', 'link', 'meta', 'svg', 'canvas'
        ];
        
        if (!strategy.keepImages) {
            selectors.push('img', 'picture', 'figure');
        }
        
        if (!strategy.keepCode) {
            selectors.push('code', 'pre');
        }
        
        selectors.forEach(selector => {
            doc.querySelectorAll(selector).forEach(el => el.remove());
        });
    }
    
    /**
     * 提取标题
     */
    extractTitle(doc) {
        // 优先级：h1 > title > 其他
        const h1 = doc.querySelector('h1');
        if (h1 && h1.textContent.trim()) {
            return h1.textContent.trim();
        }
        
        const title = doc.title;
        if (title && title.trim()) {
            return title.trim();
        }
        
        // 尝试其他标题
        for (let i = 1; i <= 6; i++) {
            const heading = doc.querySelector(`h${i}`);
            if (heading && heading.textContent.trim()) {
                return heading.textContent.trim();
            }
        }
        
        return '无标题';
    }
    
    /**
     * 提取摘要
     */
    extractSummary(doc, maxLength) {
        // 尝试主要内容区域
        const mainSelectors = [
            'main', 'article', '.main', '#main', 
            '.content', '#content', '.article', '#article',
            '.post', '#post', '.entry', '#entry'
        ];
        
        for (const selector of mainSelectors) {
            const element = doc.querySelector(selector);
            if (element) {
                const text = this.getTextContent(element, maxLength);
                if (text.length > 100) {
                    return text;
                }
            }
        }
        
        // 回退到body
        const body = doc.body;
        if (body) {
            return this.getTextContent(body, maxLength);
        }
        
        return '无内容摘要';
    }
    
    /**
     * 获取文本内容（智能截断）
     */
    getTextContent(element, maxLength) {
        let text = element.textContent
            .replace(/\s+/g, ' ')
            .trim();
        
        if (text.length <= maxLength) {
            return text;
        }
        
        // 智能截断：在句子边界处截断
        const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
        let result = '';
        
        for (const sentence of sentences) {
            if ((result + sentence).length <= maxLength) {
                result += sentence;
            } else {
                break;
            }
        }
        
        // 如果一句话都没能添加，则硬截断
        if (!result) {
            result = text.substring(0, maxLength - 3) + '...';
        }
        
        return result;
    }
    
    /**
     * 提取交互元素
     */
    extractActions(doc) {
        const actions = [];
        
        // 链接
        doc.querySelectorAll('a[href]').forEach(link => {
            const href = link.getAttribute('href');
            const text = link.textContent.trim();
            
            if (href && !href.startsWith('javascript:') && !href.startsWith('#')) {
                if (text) {
                    actions.push({
                        type: 'link',
                        text: text.substring(0, 100),
                        href: href,
                        element: 'a'
                    });
                }
            }
        });
        
        // 按钮
        doc.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach(button => {
            const text = button.textContent.trim() || button.getAttribute('value') || button.getAttribute('aria-label');
            if (text) {
                actions.push({
                    type: 'button',
                    text: text.substring(0, 100),
                    element: button.tagName.toLowerCase()
                });
            }
        });
        
        // 表单输入
        doc.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea').forEach(input => {
            const name = input.getAttribute('name') || input.getAttribute('id') || '';
            const placeholder = input.getAttribute('placeholder') || '';
            
            if (name || placeholder) {
                actions.push({
                    type: 'input',
                    name: name,
                    placeholder: placeholder,
                    element: input.tagName.toLowerCase()
                });
            }
        });
        
        return actions.slice(0, 20); // 限制数量
    }
    
    /**
     * 提取元数据
     */
    extractMetadata(doc, strategy) {
        const metadata = {};
        
        // 提取价格（电商页面）
        if (strategy.extractPrices) {
            const priceElements = doc.querySelectorAll('[class*="price"], [id*="price"]');
            const prices = Array.from(priceElements)
                .map(el => el.textContent.trim())
                .filter(text => text.match(/\$/))
                .slice(0, 5);
            
            if (prices.length > 0) {
                metadata.prices = prices;
            }
        }
        
        // 提取图片
        if (strategy.keepImages) {
            const images = doc.querySelectorAll('img[src]');
            metadata.images = Array.from(images)
                .map(img => ({
                    src: img.getAttribute('src'),
                    alt: img.getAttribute('alt') || ''
                }))
                .slice(0, 5);
        }
        
        // 提取列表
        const lists = doc.querySelectorAll('ul, ol');
        if (lists.length > 0) {
            metadata.listCount = lists.length;
        }
        
        // 提取表格
        const tables = doc.querySelectorAll('table');
        if (tables.length > 0) {
            metadata.tableCount = tables.length;
        }
        
        return metadata;
    }
    
    /**
     * 构建压缩输出
     */
    buildCompressedOutput(data) {
        const lines = [];
        
        lines.push(`🌐 URL: ${data.url}`);
        lines.push(`📰 标题: ${data.title}`);
        lines.push('');
        lines.push(`📝 摘要:`);
        lines.push(data.summary);
        
        if (data.actions.length > 0) {
            lines.push('');
            lines.push(`🔗 交互元素 (${data.actions.length}个):`);
            
            data.actions.forEach((action, index) => {
                switch(action.type) {
                    case 'link':
                        lines.push(`  ${index + 1}. [链接] ${action.text} → ${action.href}`);
                        break;
                    case 'button':
                        lines.push(`  ${index + 1}. [按钮] ${action.text}`);
                        break;
                    case 'input':
                        lines.push(`  ${index + 1}. [输入] ${action.name || '未命名'} ${action.placeholder ? `(${action.placeholder})` : ''}`);
                        break;
                }
            });
        }
        
        if (Object.keys(data.metadata).length > 0) {
            lines.push('');
            lines.push(`📊 元数据:`);
            for (const [key, value] of Object.entries(data.metadata)) {
                if (Array.isArray(value)) {
                    lines.push(`  ${key}: ${value.slice(0, 3).join(', ')}${value.length > 3 ? '...' : ''}`);
                } else {
                    lines.push(`  ${key}: ${value}`);
                }
            }
        }
        
        lines.push('');
        lines.push(`⚙️ 压缩策略: ${data.strategy.name}`);
        
        return lines.join('\n');
    }
    
    /**
     * 创建回退输出
     */
    createFallbackOutput(html, url) {
        const lines = [];
        lines.push(`🌐 URL: ${url}`);
        lines.push(`⚠️ 压缩失败，返回原始内容摘要`);
        lines.push('');
        
        // 简单提取前500字符
        const text = html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
        lines.push(text.substring(0, 500) + (text.length > 500 ? '...' : ''));
        
        return lines.join('\n');
    }
    
    /**
     * 获取缓存键
     */
    getCacheKey(html, config) {
        // 使用内容和配置的哈希作为缓存键
        const content = html.substring(0, 1000) + JSON.stringify(config);
        return Buffer.from(content).toString('base64').substring(0, 50);
    }
    
    /**
     * 更新统计信息
     */
    updateStats(result) {
        this.stats.totalCompressions++;
        this.stats.totalBytesSaved += result.stats.bytesSaved;
        this.stats.averageReduction = this.stats.totalBytesSaved / this.stats.totalCompressions;
    }
    
    /**
     * 获取统计信息
     */
    getStats() {
        return {
            ...this.stats,
            cacheSize: this.cache.size
        };
    }
    
    /**
     * 清除缓存
     */
    clearCache() {
        this.cache.clear();
        console.log('DOM压缩器缓存已清除');
    }
}

// 命令行接口
if (require.main === module) {
    const compressor = new DOMCompressor();
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('使用方法:');
        console.log('  node dom-compressor.js <HTML文件或URL>');
        console.log('  node dom-compressor.js --stats');
        console.log('  node dom-compressor.js --clear-cache');
        process.exit(1);
    }
    
    const input = args[0];
    
    if (input === '--stats') {
        console.log(JSON.stringify(compressor.getStats(), null, 2));
        process.exit(0);
    }
    
    if (input === '--clear-cache') {
        compressor.clearCache();
        process.exit(0);
    }
    
    // 读取输入
    let html;
    if (fs.existsSync(input)) {
        // 从文件读取
        html = fs.readFileSync(input, 'utf8');
    } else if (input.startsWith('http')) {
        // 从URL获取（简单实现）
        const { exec } = require('child_process');
        exec(`curl -s -L "${input}"`, (error, stdout) => {
            if (error) {
                console.error('获取URL失败:', error.message);
                process.exit(1);
            }
            
            html = stdout;
            processHtml();
        });
    } else {
        // 直接作为HTML字符串
        html = input;
        processHtml();
    }
    
    function processHtml() {
        const url = input.startsWith('http') ? input : 'file://' + path.resolve(input);
        
        compressor.compress(html, url)
            .then(result => {
                console.log(result.compressed);
                console.log('\n📊 压缩统计:');
                console.log(JSON.stringify(result.stats, null, 2));
            })
            .catch(error => {
                console.error('压缩失败:', error.message);
                process.exit(1);
            });
    }
}

module.exports = DOMCompressor;