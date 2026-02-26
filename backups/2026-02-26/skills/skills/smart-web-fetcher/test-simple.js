#!/usr/bin/env node
/**
 * 简单测试脚本
 */

const SmartWebFetcher = require('./scripts/smart-fetch');

async function test() {
    console.log('🧪 测试智能网络获取系统\n');
    
    try {
        // 创建实例
        const fetcher = new SmartWebFetcher();
        
        console.log('1. 测试基本功能...');
        const result = await fetcher.fetch('https://httpbin.org/html', {
            enableCompression: true,
            verbose: true
        });
        
        if (result.success) {
            console.log('✅ 测试通过！');
            console.log(`工具: ${result.metadata.tool}`);
            console.log(`处理时间: ${result.metadata.processingTime}ms`);
            
            if (result.metadata.compression) {
                console.log(`压缩节省: ${result.metadata.compression.stats.reduction}`);
            }
            
            // 显示部分内容
            const preview = result.content.substring(0, 200) + '...';
            console.log(`\n内容预览:\n${preview}`);
        } else {
            console.log('❌ 测试失败:', result.error);
        }
        
    } catch (error) {
        console.error('❌ 测试异常:', error.message);
    }
}

if (require.main === module) {
    test();
}

module.exports = test;