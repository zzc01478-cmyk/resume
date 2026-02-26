#!/usr/bin/env node
/**
 * 智能网络获取基础使用示例
 */

const path = require('path');
const SmartWebFetcher = require('../scripts/smart-fetch');

async function runExamples() {
    console.log('🚀 智能网络获取系统 - 使用示例\n');
    
    // 创建获取器实例
    const fetcher = new SmartWebFetcher();
    
    // 示例1: 基本获取
    console.log('📋 示例1: 基本获取');
    console.log('='.repeat(50));
    
    try {
        const result1 = await fetcher.fetch('https://httpbin.org/html');
        console.log(`✅ 获取成功: ${result1.success ? '是' : '否'}`);
        console.log(`📏 内容大小: ${result1.metadata?.fetchResult?.size || 0} 字节`);
        console.log(`🔧 使用工具: ${result1.metadata?.tool}`);
        console.log(`⏱️ 处理时间: ${result1.metadata?.processingTime}ms`);
        console.log();
    } catch (error) {
        console.error(`❌ 示例1失败: ${error.message}`);
    }
    
    // 示例2: 强制使用特定工具
    console.log('📋 示例2: 强制使用Crawlee');
    console.log('='.repeat(50));
    
    try {
        const result2 = await fetcher.fetch('https://httpbin.org/html', {
            forceTool: 'crawlee',
            verbose: true
        });
        
        console.log(`✅ 获取成功: ${result2.success ? '是' : '否'}`);
        console.log(`🔧 使用工具: ${result2.metadata?.tool} (强制)`);
        console.log();
    } catch (error) {
        console.error(`❌ 示例2失败: ${error.message}`);
    }
    
    // 示例3: 禁用压缩
    console.log('📋 示例3: 禁用压缩');
    console.log('='.repeat(50));
    
    try {
        const result3 = await fetcher.fetch('https://httpbin.org/html', {
            enableCompression: false
        });
        
        console.log(`✅ 获取成功: ${result3.success ? '是' : '否'}`);
        console.log(`📦 压缩: ${result3.metadata?.compression ? '启用' : '禁用'}`);
        console.log();
    } catch (error) {
        console.error(`❌ 示例3失败: ${error.message}`);
    }
    
    // 示例4: 批量获取
    console.log('📋 示例4: 批量获取演示');
    console.log('='.repeat(50));
    
    const testUrls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://httpbin.org/xml'
    ];
    
    try {
        console.log(`🔄 批量获取 ${testUrls.length} 个URL`);
        const results = await fetcher.batchFetch(testUrls, {
            concurrency: 2,
            batchDelay: 1000
        });
        
        let successCount = 0;
        results.forEach((result, index) => {
            if (result.success) {
                successCount++;
                console.log(`  ${index + 1}. ${testUrls[index]} ✅`);
            } else {
                console.log(`  ${index + 1}. ${testUrls[index]} ❌ ${result.error}`);
            }
        });
        
        console.log(`\n📊 批量结果: ${successCount}/${testUrls.length} 成功`);
        console.log();
    } catch (error) {
        console.error(`❌ 示例4失败: ${error.message}`);
    }
    
    // 示例5: 获取统计信息
    console.log('📋 示例5: 系统统计');
    console.log('='.repeat(50));
    
    const stats = fetcher.getStats();
    console.log(JSON.stringify(stats, null, 2));
    console.log();
    
    // 示例6: 测试所有服务
    console.log('📋 示例6: 服务测试');
    console.log('='.repeat(50));
    
    try {
        const serviceResults = await fetcher.testServices();
        console.log(JSON.stringify(serviceResults, null, 2));
    } catch (error) {
        console.error(`❌ 示例6失败: ${error.message}`);
    }
    
    console.log('\n🎉 所有示例完成！');
}

// 运行示例
if (require.main === module) {
    runExamples().catch(error => {
        console.error('❌ 示例运行失败:', error);
        process.exit(1);
    });
}

module.exports = { runExamples };