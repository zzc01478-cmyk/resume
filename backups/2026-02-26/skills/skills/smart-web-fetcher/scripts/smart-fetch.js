#!/usr/bin/env node
/**
 * 智能网络内容获取主脚本
 * 集成智能路由、Crawlee、DOM压缩的统一接口
 */

const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// 导入模块
const SmartRouter = require('./router');
const DOMCompressor = require('./dom-compressor');

class SmartWebFetcher {
    constructor(configPath = '../config/config.json') {
        this.config = this.loadConfig(configPath);
        this.router = new SmartRouter(configPath);
        this.compressor = new DOMCompressor(configPath);
        this.cache = new Map();
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            totalTokenSavings: 0,
            averageProcessingTime: 0
        };
        
        this.initServices();
    }
    
    loadConfig(configPath) {
        const fullPath = path.join(__dirname, configPath);
        if (fs.existsSync(fullPath)) {
            return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        }
        
        // 默认配置
        return {
            fetcher: {
                defaultTimeout: 30000,
                maxRetries: 2,
                cacheEnabled: true,
                cacheTTL: 3600,
                tokenBudget: 5000,
                enableCompression: true
            },
            services: {
                webFetch: {
                    maxChars: 10000,
                    timeout: 10000
                },
                crawlee: {
                    headless: true,
                    timeout: 30000,
                    maxConcurrency: 3
                },
                curl: {
                    timeout: 5000,
                    followRedirects: true
                }
            }
        };
    }
    
    initServices() {
        // 初始化各服务
        this.services = {
            webFetch: this.createWebFetchService(),
            crawlee: this.createCrawleeService(),
            curl: this.createCurlService()
        };
    }
    
    createWebFetchService() {
        return {
            name: 'web_fetch',
            description: 'OpenClaw内置web_fetch工具',
            
            async fetch(url, options = {}) {
                const maxChars = options.maxChars || this.config.services.webFetch.maxChars;
                
                // 构建命令
                const cmd = `openclaw tool web_fetch --url "${url}" --maxChars ${maxChars}`;
                
                try {
                    const { stdout } = await execAsync(cmd);
                    const result = JSON.parse(stdout);
                    
                    if (result.status === 200) {
                        return {
                            success: true,
                            content: result.text || result.content,
                            contentType: result.contentType,
                            size: result.length || 0,
                            raw: result
                        };
                    } else {
                        return {
                            success: false,
                            error: `HTTP ${result.status}`,
                            raw: result
                        };
                    }
                } catch (error) {
                    return {
                        success: false,
                        error: error.message,
                        raw: null
                    };
                }
            }
        };
    }
    
    createCrawleeService() {
        return {
            name: 'crawlee',
            description: 'Crawlee浏览器自动化',
            
            async fetch(url, options = {}) {
                // 创建临时脚本文件
                const scriptContent = `
const { PlaywrightCrawler } = require('crawlee');

const crawler = new PlaywrightCrawler({
    maxRequestsPerCrawl: 1,
    requestHandlerTimeoutSecs: ${options.timeout || 30},
    headless: ${options.headless !== false},
    
    async requestHandler({ request, page, log }) {
        try {
            // 导航到页面
            await page.goto(request.url, { waitUntil: 'networkidle' });
            
            // 获取页面内容
            const content = await page.content();
            const title = await page.title();
            
            // 提取关键信息
            const data = {
                url: request.url,
                title: title,
                content: content,
                timestamp: new Date().toISOString()
            };
            
            // 输出JSON结果
            console.log(JSON.stringify({ success: true, data: data }));
            
        } catch (error) {
            console.log(JSON.stringify({ 
                success: false, 
                error: error.message 
            }));
        }
    }
});

// 启动爬取
await crawler.run([\`${url}\`]);
                `;
                
                const scriptPath = path.join(__dirname, 'temp_crawlee_script.js');
                fs.writeFileSync(scriptPath, scriptContent);
                
                try {
                    const { stdout } = await execAsync(`node ${scriptPath}`);
                    
                    // 清理临时文件
                    fs.unlinkSync(scriptPath);
                    
                    const result = JSON.parse(stdout);
                    
                    if (result.success) {
                        return {
                            success: true,
                            content: result.data.content,
                            title: result.data.title,
                            size: Buffer.byteLength(result.data.content, 'utf8'),
                            raw: result.data
                        };
                    } else {
                        return {
                            success: false,
                            error: result.error,
                            raw: null
                        };
                    }
                } catch (error) {
                    // 清理临时文件
                    if (fs.existsSync(scriptPath)) {
                        fs.unlinkSync(scriptPath);
                    }
                    
                    return {
                        success: false,
                        error: error.message,
                        raw: null
                    };
                }
            }
        };
    }
    
    createCurlService() {
        return {
            name: 'curl',
            description: 'cURL命令行工具',
            
            async fetch(url, options = {}) {
                const timeout = options.timeout || this.config.services.curl.timeout;
                const followRedirects = options.followRedirects !== false;
                
                const cmd = `curl -s -L ${followRedirects ? '-L' : ''} --max-time ${timeout} "${url}"`;
                
                try {
                    const { stdout, stderr } = await execAsync(cmd);
                    
                    if (stderr && !stdout) {
                        return {
                            success: false,
                            error: stderr,
                            raw: null
                        };
                    }
                    
                    return {
                        success: true,
                        content: stdout,
                        size: Buffer.byteLength(stdout, 'utf8'),
                        raw: stdout
                    };
                } catch (error) {
                    return {
                        success: false,
                        error: error.message,
                        raw: null
                    };
                }
            }
        };
    }
    
    /**
     * 智能获取网页内容
     */
    async fetch(url, userOptions = {}) {
        const startTime = Date.now();
        this.stats.totalRequests++;
        
        // 合并选项
        const options = {
            ...this.config.fetcher,
            ...userOptions
        };
        
        // 检查缓存
        const cacheKey = this.getCacheKey(url, options);
        if (options.cacheEnabled && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < (options.cacheTTL * 1000)) {
                console.log('📦 使用缓存结果');
                return cached.result;
            }
        }
        
        try {
            // 1. 智能路由分析
            console.log('🔍 分析URL...');
            const routeAnalysis = await this.router.analyze(url, {
                forceTool: options.forceTool,
                preDetect: options.preDetect !== false
            });
            
            console.log(this.router.getRoutingSuggestion(routeAnalysis));
            
            // 2. 检查token预算
            if (options.tokenBudget && routeAnalysis.estimatedTokens > options.tokenBudget) {
                console.log(`⚠️ 预估token消耗(${routeAnalysis.estimatedTokens})超出预算(${options.tokenBudget})`);
                
                // 尝试使用更节省的方法
                if (routeAnalysis.tool === 'crawlee') {
                    console.log('🔄 尝试使用web_fetch替代...');
                    routeAnalysis.tool = 'web_fetch';
                    routeAnalysis.reason = '超出token预算，使用轻量方法';
                    routeAnalysis.confidence = 0.6;
                }
            }
            
            // 3. 执行获取
            console.log(`🚀 使用 ${routeAnalysis.tool.toUpperCase()} 获取内容...`);
            const fetchResult = await this.executeFetch(routeAnalysis.tool, url, options);
            
            if (!fetchResult.success) {
                throw new Error(`获取失败: ${fetchResult.error}`);
            }
            
            // 4. 智能压缩
            let finalContent = fetchResult.content;
            let compressionResult = null;
            
            if (options.enableCompression && routeAnalysis.compress) {
                console.log('📦 智能压缩内容...');
                compressionResult = await this.compressor.compress(
                    finalContent, 
                    url, 
                    { maxTextLength: routeAnalysis.estimatedTokens * 4 } // 估算字符数
                );
                
                finalContent = compressionResult.compressed;
                
                console.log(`✅ 压缩完成: ${compressionResult.stats.reduction} 节省`);
            }
            
            // 5. 构建最终结果
            const result = {
                success: true,
                url: url,
                content: finalContent,
                metadata: {
                    tool: routeAnalysis.tool,
                    routeAnalysis: routeAnalysis,
                    fetchResult: {
                        size: fetchResult.size,
                        title: fetchResult.title,
                        contentType: fetchResult.contentType
                    },
                    compression: compressionResult ? {
                        stats: compressionResult.stats,
                        structured: compressionResult.structured
                    } : null,
                    processingTime: Date.now() - startTime,
                    timestamp: new Date().toISOString()
                }
            };
            
            // 6. 更新统计
            this.stats.successfulRequests++;
            if (compressionResult) {
                this.stats.totalTokenSavings += compressionResult.stats.bytesSaved / 4; // 估算token节省
            }
            this.stats.averageProcessingTime = 
                (this.stats.averageProcessingTime * (this.stats.successfulRequests - 1) + 
                 result.metadata.processingTime) / this.stats.successfulRequests;
            
            // 7. 缓存结果
            if (options.cacheEnabled) {
                this.cache.set(cacheKey, {
                    result: result,
                    timestamp: Date.now()
                });
            }
            
            return result;
            
        } catch (error) {
            console.error('❌ 获取失败:', error.message);
            
            // 更新失败统计
            const failureRate = (this.stats.totalRequests - this.stats.successfulRequests) / this.stats.totalRequests;
            
            return {
                success: false,
                url: url,
                error: error.message,
                metadata: {
                    processingTime: Date.now() - startTime,
                    failureRate: failureRate.toFixed(2),
                    timestamp: new Date().toISOString()
                }
            };
        }
    }
    
    /**
     * 执行获取
     */
    async executeFetch(tool, url, options) {
        const service = this.services[tool];
        
        if (!service) {
            throw new Error(`未知的工具: ${tool}`);
        }
        
        // 添加超时控制
        const timeout = options.defaultTimeout || 30000;
        
        return Promise.race([
            service.fetch(url, options),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error(`获取超时 (${timeout}ms)`)), timeout)
            )
        ]);
    }
    
    /**
     * 获取缓存键
     */
    getCacheKey(url, options) {
        // 基于URL和关键选项生成缓存键
        const keyData = {
            url: url,
            tool: options.forceTool || 'auto',
            compress: options.enableCompression,
            maxChars: options.maxChars
        };
        
        return Buffer.from(JSON.stringify(keyData)).toString('base64');
    }
    
    /**
     * 清除缓存
     */
    clearCache() {
        this.cache.clear();
        this.router.clearCache();
        this.compressor.clearCache();
        console.log('✅ 所有缓存已清除');
    }
    
    /**
     * 获取统计信息
     */
    getStats() {
        return {
            ...this.stats,
            cacheSize: this.cache.size,
            successRate: this.stats.totalRequests > 0 
                ? (this.stats.successfulRequests / this.stats.totalRequests * 100).toFixed(2) + '%'
                : '0%',
            averageTokenSavings: this.stats.successfulRequests > 0
                ? Math.round(this.stats.totalTokenSavings / this.stats.successfulRequests)
                : 0
        };
    }
    
    /**
     * 批量获取
     */
    async batchFetch(urls, options = {}) {
        const results = [];
        const concurrency = options.concurrency || 3;
        
        console.log(`🔄 批量获取 ${urls.length} 个URL，并发数: ${concurrency}`);
        
        // 分批处理
        for (let i = 0; i < urls.length; i += concurrency) {
            const batch = urls.slice(i, i + concurrency);
            console.log(`📦 处理批次 ${Math.floor(i/concurrency) + 1}/${Math.ceil(urls.length/concurrency)}`);
            
            const batchPromises = batch.map(url => 
                this.fetch(url, options).catch(error => ({
                    success: false,
                    url: url,
                    error: error.message
                }))
            );
            
            const batchResults = await Promise.all(batchPromises);
            results.push(...batchResults);
            
            // 批次间延迟
            if (i + concurrency < urls.length && options.batchDelay) {
                await new Promise(resolve => setTimeout(resolve, options.batchDelay));
            }
        }
        
        return results;
    }
    
    /**
     * 测试所有服务
     */
    async testServices() {
        const testUrl = 'https://httpbin.org/html';
        const results = {};
        
        console.log('🧪 测试所有服务...');
        
        for (const [name, service] of Object.entries(this.services)) {
            console.log(`测试 ${name}...`);
            
            try {
                const startTime = Date.now();
                const result = await service.fetch(testUrl, { timeout: 10000 });
                const time = Date.now() - startTime;
                
                results[name] = {
                    success: result.success,
                    time: time + 'ms',
                    size: result.size || 0,
                    error: result.error
                };
                
                console.log(`  ${result.success ? '✅' : '❌'} ${time}ms`);
            } catch (error) {
                results[name] = {
                    success: false,
                    error: error.message
                };
                console.log(`  ❌ ${error.message}`);
            }
        }
        
        return results;
    }
}

// 命令行接口
if (require.main === module) {
    const fetcher = new SmartWebFetcher();
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log(`
🤖 智能网络内容获取系统

使用方法:
  node smart-fetch.js <URL> [选项]
  node smart-fetch.js --batch <文件> [选项]
  node smart-fetch.js --test [选项]
  node smart-fetch.js --stats
  node smart-fetch.js --clear-cache

选项:
  --tool=<tool>      强制使用特定工具 (web_fetch, crawlee, curl)
  --no-compress      禁用压缩
  --max-chars=<n>    最大字符数
  --token-budget=<n> Token预算限制
  --explain          显示详细路由决策
  --verbose          显示详细日志
  --output=<文件>     输出到文件
  --format=<格式>     输出格式 (json, text, summary)

示例:
  node smart-fetch.js https://example.com
  node smart-fetch.js https://shop.com --tool=crawlee --explain
  node smart-fetch.js --batch urls.txt --concurrency=3
  node smart-fetch.js --test
        `);
        process.exit(1);
    }
    
    const command = args[0];
    const options = {};
    
    // 解析选项
    args.slice(1).forEach(arg => {
        if (arg.startsWith('--tool=')) {
            options.forceTool = arg.split('=')[1];
        } else if (arg === '--no-compress') {
            options.enableCompression = false;
        } else if (arg.startsWith('--max-chars=')) {
            options.maxChars = parseInt(arg.split('=')[1]);
        } else if (arg.startsWith('--token-budget=')) {
            options.tokenBudget = parseInt(arg.split('=')[1]);
        } else if (arg === '--explain') {
            options.verbose = true;
        } else if (arg === '--verbose') {
            options.verbose = true;
        } else if (arg.startsWith('--output=')) {
            options.outputFile = arg.split('=')[1];
        } else if (arg.startsWith('--format=')) {
            options.format = arg.split('=')[1];
        } else if (arg.startsWith('--concurrency=')) {
            options.concurrency = parseInt(arg.split('=')[1]);
        } else if (arg.startsWith('--batch-delay=')) {
            options.batchDelay = parseInt(arg.split('=')[1]);
        }
    });
    
    async function run() {
        try {
            let result;
            
            if (command === '--batch') {
                const file = args[1];
                if (!file) {
                    console.error('请指定包含URL的文件');
                    process.exit(1);
                }
                
                const urls = fs.readFileSync(file, 'utf8')
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line && !line.startsWith('#'));
                
                console.log(`📋 批量处理 ${urls.length} 个URL`);
                result = await fetcher.batchFetch(urls, options);
                
            } else if (command === '--test') {
                result = await fetcher.testServices();
                
            } else if (command === '--stats') {
                console.log(JSON.stringify(fetcher.getStats(), null, 2));
                process.exit(0);
                
            } else if (command === '--clear-cache') {
                fetcher.clearCache();
                process.exit(0);
                
            } else if (command.startsWith('http')) {
                // 单个URL获取
                console.log(`🎯 获取: ${command}`);
                result = await fetcher.fetch(command, options);
                
            } else {
                console.error(`未知命令: ${command}`);
                process.exit(1);
            }
            
            // 输出结果
            if (options.outputFile) {
                const output = options.format === 'json' 
                    ? JSON.stringify(result, null, 2)
                    : result.success ? result.content : result.error;
                
                fs.writeFileSync(options.outputFile, output);
                console.log(`✅ 结果已保存到: ${options.outputFile}`);
            } else {
                if (options.format === 'json') {
                    console.log(JSON.stringify(result, null, 2));
                } else if (result.success) {
                    console.log('\n' + '='.repeat(50));
                    console.log('✅ 获取成功');
                    console.log('='.repeat(50) + '\n');
                    console.log(result.content);
                    
                    if (options.verbose && result.metadata) {
                        console.log('\n' + '='.repeat(50));
                        console.log('📊 元数据:');
                        console.log(JSON.stringify(result.metadata, null, 2));
                    }
                } else {
                    console.error('❌ 获取失败:', result.error);
                }
            }
            
        } catch (error) {
            console.error('❌ 执行失败:', error.message);
            process.exit(1);
        }
    }
    
    run();
}

module.exports = SmartWebFetcher;