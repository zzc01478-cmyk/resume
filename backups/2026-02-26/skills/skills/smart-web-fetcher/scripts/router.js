#!/usr/bin/env node
/**
 * 智能路由器 - 自动选择最佳网页获取工具
 */

const fs = require('fs');
const path = require('path');
const { URL } = require('url');

class SmartRouter {
    constructor(configPath = '../config/config.json') {
        this.config = this.loadConfig(configPath);
        this.siteCache = new Map();
        this.initPatterns();
    }
    
    loadConfig(configPath) {
        const fullPath = path.join(__dirname, configPath);
        if (fs.existsSync(fullPath)) {
            return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        }
        
        // 默认配置
        return {
            routing: {
                defaultTool: 'auto',
                dynamicSites: ['shop.com', 'app.', 'spa.', 'dashboard.', 'admin.'],
                apiPatterns: ['/api/', '.json$', '.xml$', '.yaml$', '.yml$'],
                staticSites: ['docs.', 'blog.', 'news.', 'article.', 'readme.'],
                forceCrawlee: ['twitter.com', 'youtube.com', 'instagram.com'],
                forceWebFetch: ['github.com', 'gitlab.com', 'stackoverflow.com']
            },
            compression: {
                enabled: true,
                maxTextLength: 1500,
                extractActions: true
            }
        };
    }
    
    initPatterns() {
        // 编译正则表达式模式
        this.apiPatterns = this.config.routing.apiPatterns.map(pattern => 
            new RegExp(pattern.replace(/\$/g, '\\$').replace(/\./g, '\\.'))
        );
    }
    
    /**
     * 分析URL并选择最佳工具
     */
    async analyze(url, options = {}) {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname;
        const pathname = urlObj.pathname;
        
        // 检查缓存
        const cacheKey = `${hostname}${pathname}`;
        if (this.siteCache.has(cacheKey) && !options.forceRefresh) {
            return this.siteCache.get(cacheKey);
        }
        
        const analysis = {
            url,
            hostname,
            tool: 'web_fetch', // 默认
            compress: this.config.compression.enabled,
            reason: '默认选择',
            confidence: 0.7,
            estimatedTokens: 1000,
            metadata: {}
        };
        
        // 1. 检查强制规则
        if (this.isForcedTool(url, 'crawlee')) {
            analysis.tool = 'crawlee';
            analysis.reason = '强制使用Crawlee';
            analysis.confidence = 1.0;
        } else if (this.isForcedTool(url, 'web_fetch')) {
            analysis.tool = 'web_fetch';
            analysis.reason = '强制使用web_fetch';
            analysis.confidence = 1.0;
        }
        
        // 2. 检查API模式
        else if (this.isApiUrl(url)) {
            analysis.tool = 'curl';
            analysis.compress = false;
            analysis.reason = 'API接口';
            analysis.confidence = 0.9;
        }
        
        // 3. 检查动态网站模式
        else if (this.isDynamicSite(url)) {
            analysis.tool = 'crawlee';
            analysis.reason = '动态网站模式';
            analysis.confidence = 0.8;
        }
        
        // 4. 检查静态网站模式
        else if (this.isStaticSite(url)) {
            analysis.tool = 'web_fetch';
            analysis.reason = '静态网站模式';
            analysis.confidence = 0.85;
        }
        
        // 5. 预检测（如果需要）
        else if (options.preDetect !== false) {
            const preDetection = await this.preDetect(url);
            analysis.tool = preDetection.tool;
            analysis.reason = `预检测: ${preDetection.reason}`;
            analysis.confidence = preDetection.confidence;
            analysis.metadata.preDetection = preDetection;
        }
        
        // 6. 用户覆盖
        if (options.forceTool) {
            analysis.tool = options.forceTool;
            analysis.reason = `用户指定: ${options.forceTool}`;
            analysis.confidence = 1.0;
        }
        
        // 7. 估算token消耗
        analysis.estimatedTokens = this.estimateTokenConsumption(analysis);
        
        // 缓存结果
        this.siteCache.set(cacheKey, analysis);
        
        return analysis;
    }
    
    /**
     * 检查是否强制使用特定工具
     */
    isForcedTool(url, tool) {
        const hostname = new URL(url).hostname;
        const forceList = this.config.routing[`force${tool.charAt(0).toUpperCase() + tool.slice(1)}`] || [];
        
        return forceList.some(pattern => {
            if (pattern.startsWith('*.')) {
                return hostname.endsWith(pattern.slice(2));
            }
            return hostname.includes(pattern);
        });
    }
    
    /**
     * 检查是否为API URL
     */
    isApiUrl(url) {
        const pathname = new URL(url).pathname;
        return this.apiPatterns.some(pattern => pattern.test(pathname));
    }
    
    /**
     * 检查是否为动态网站
     */
    isDynamicSite(url) {
        const hostname = new URL(url).hostname;
        return this.config.routing.dynamicSites.some(pattern => {
            if (pattern.endsWith('.')) {
                return hostname.includes(pattern.slice(0, -1));
            }
            return hostname.includes(pattern);
        });
    }
    
    /**
     * 检查是否为静态网站
     */
    isStaticSite(url) {
        const hostname = new URL(url).hostname;
        return this.config.routing.staticSites.some(pattern => {
            if (pattern.endsWith('.')) {
                return hostname.includes(pattern.slice(0, -1));
            }
            return hostname.includes(pattern);
        });
    }
    
    /**
     * 预检测URL类型
     */
    async preDetect(url) {
        try {
            // 快速HEAD请求检测
            const headers = await this.fetchHeaders(url);
            
            if (headers['content-type']?.includes('application/json')) {
                return {
                    tool: 'curl',
                    reason: 'JSON API',
                    confidence: 0.95
                };
            }
            
            // 获取少量HTML样本
            const sample = await this.fetchSampleHtml(url, 5000);
            
            // 分析HTML特征
            const features = this.analyzeHtmlFeatures(sample);
            
            if (features.isSpa || features.hasDynamicContent) {
                return {
                    tool: 'crawlee',
                    reason: 'SPA或动态内容',
                    confidence: 0.85
                };
            }
            
            return {
                tool: 'web_fetch',
                reason: '静态HTML',
                confidence: 0.8
            };
            
        } catch (error) {
            // 预检测失败，使用保守策略
            return {
                tool: 'web_fetch',
                reason: '预检测失败，使用保守策略',
                confidence: 0.5
            };
        }
    }
    
    /**
     * 获取HTTP头信息
     */
    async fetchHeaders(url) {
        const { exec } = require('child_process');
        return new Promise((resolve, reject) => {
            exec(`curl -s -I "${url}"`, (error, stdout) => {
                if (error) reject(error);
                
                const headers = {};
                stdout.split('\n').forEach(line => {
                    const match = line.match(/^([^:]+):\s*(.+)$/);
                    if (match) {
                        headers[match[1].toLowerCase()] = match[2];
                    }
                });
                
                resolve(headers);
            });
        });
    }
    
    /**
     * 获取HTML样本
     */
    async fetchSampleHtml(url, maxSize = 5000) {
        const { exec } = require('child_process');
        return new Promise((resolve, reject) => {
            exec(`curl -s -L "${url}" | head -c ${maxSize}`, (error, stdout) => {
                if (error) reject(error);
                resolve(stdout);
            });
        });
    }
    
    /**
     * 分析HTML特征
     */
    analyzeHtmlFeatures(html) {
        const features = {
            isSpa: false,
            hasDynamicContent: false,
            hasJavaScript: false,
            hasReact: false,
            hasVue: false,
            hasAngular: false
        };
        
        const lowerHtml = html.toLowerCase();
        
        features.hasJavaScript = lowerHtml.includes('<script');
        features.isSpa = features.hasJavaScript && 
                        (lowerHtml.includes('react') || 
                         lowerHtml.includes('vue') || 
                         lowerHtml.includes('angular'));
        features.hasReact = lowerHtml.includes('react');
        features.hasVue = lowerHtml.includes('vue');
        features.hasAngular = lowerHtml.includes('angular');
        features.hasDynamicContent = lowerHtml.includes('dynamic') || 
                                   lowerHtml.includes('async') || 
                                   lowerHtml.includes('fetch');
        
        return features;
    }
    
    /**
     * 估算token消耗
     */
    estimateTokenConsumption(analysis) {
        // 基础估算：每字符约0.25 tokens（英文）
        const baseEstimate = 1000; // 基础消耗
        
        let multiplier = 1.0;
        
        switch(analysis.tool) {
            case 'crawlee':
                multiplier = 2.5; // Crawlee消耗更多
                break;
            case 'curl':
                multiplier = 0.8; // API通常较小
                break;
            case 'web_fetch':
                multiplier = 1.0; // 基准
                break;
        }
        
        if (analysis.compress) {
            multiplier *= 0.2; // 压缩后减少80%
        }
        
        return Math.round(baseEstimate * multiplier);
    }
    
    /**
     * 获取路由建议（人类可读）
     */
    getRoutingSuggestion(analysis) {
        const suggestions = [];
        
        suggestions.push(`🌐 URL: ${analysis.url}`);
        suggestions.push(`🔧 推荐工具: ${analysis.tool.toUpperCase()}`);
        suggestions.push(`📝 原因: ${analysis.reason}`);
        suggestions.push(`🎯 置信度: ${(analysis.confidence * 100).toFixed(0)}%`);
        suggestions.push(`💰 预估Token消耗: ${analysis.estimatedTokens}`);
        suggestions.push(`📦 压缩: ${analysis.compress ? '✅ 启用' : '❌ 禁用'}`);
        
        if (analysis.metadata.preDetection) {
            suggestions.push(`🔍 预检测结果: ${JSON.stringify(analysis.metadata.preDetection, null, 2)}`);
        }
        
        return suggestions.join('\n');
    }
    
    /**
     * 清除缓存
     */
    clearCache() {
        this.siteCache.clear();
        console.log('路由器缓存已清除');
    }
    
    /**
     * 获取缓存统计
     */
    getCacheStats() {
        return {
            size: this.siteCache.size,
            entries: Array.from(this.siteCache.entries()).map(([key, value]) => ({
                key,
                tool: value.tool,
                confidence: value.confidence
            }))
        };
    }
}

// 命令行接口
if (require.main === module) {
    const router = new SmartRouter();
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('使用方法: node router.js <URL> [--explain] [--force-tool=<tool>]');
        console.log('示例:');
        console.log('  node router.js https://example.com');
        console.log('  node router.js https://example.com --explain');
        console.log('  node router.js https://shop.com --force-tool=crawlee');
        process.exit(1);
    }
    
    const url = args[0];
    const options = {};
    
    args.slice(1).forEach(arg => {
        if (arg === '--explain') {
            options.verbose = true;
        } else if (arg.startsWith('--force-tool=')) {
            options.forceTool = arg.split('=')[1];
        } else if (arg === '--clear-cache') {
            router.clearCache();
            process.exit(0);
        } else if (arg === '--cache-stats') {
            console.log(JSON.stringify(router.getCacheStats(), null, 2));
            process.exit(0);
        }
    });
    
    router.analyze(url, options)
        .then(analysis => {
            if (options.verbose) {
                console.log(router.getRoutingSuggestion(analysis));
            } else {
                console.log(analysis.tool);
            }
        })
        .catch(error => {
            console.error('路由分析失败:', error.message);
            process.exit(1);
        });
}

module.exports = SmartRouter;