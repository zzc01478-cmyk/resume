#!/usr/bin/env node
/**
 * 使用curl测试BOSS直聘访问
 * 简单检查页面状态和内容
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs');
const path = require('path');

const execAsync = promisify(exec);

async function testBossWebsite() {
    const url = 'https://www.zhipin.com';
    
    console.log('🚀 测试BOSS直聘网站访问');
    console.log('='.repeat(40));
    
    try {
        // 1. 测试网络连接
        console.log('🌐 测试网络连接...');
        const pingResult = await execAsync(`curl -s -o /dev/null -w "%{http_code}" -I ${url}`, { timeout: 10000 });
        console.log(`✅ HTTP状态码: ${pingResult.stdout.trim()}`);
        
        // 2. 获取页面内容
        console.log('📄 获取页面内容...');
        const curlResult = await execAsync(`curl -s -L "${url}" --max-time 15`, { timeout: 20000 });
        
        const content = curlResult.stdout;
        const size = Buffer.byteLength(content, 'utf8');
        
        console.log(`✅ 获取成功，大小: ${size} 字节`);
        
        // 3. 分析内容
        console.log('🔍 分析页面内容...');
        
        // 检查是否重定向
        const finalUrlMatch = content.match(/<meta[^>]*http-equiv="refresh"[^>]*url=([^"'>]+)/i);
        if (finalUrlMatch) {
            console.log(`🔄 检测到页面重定向: ${finalUrlMatch[1]}`);
        }
        
        // 检查登录相关关键词
        const loginKeywords = ['登录', 'sign in', 'log in', '手机验证', '二维码登录', '扫码登录'];
        const foundKeywords = loginKeywords.filter(keyword => 
            content.toLowerCase().includes(keyword.toLowerCase())
        );
        
        console.log(`🔐 找到登录关键词: ${foundKeywords.length > 0 ? foundKeywords.join(', ') : '无'}`);
        
        // 检查二维码相关元素
        const qrKeywords = ['qrcode', 'qr-code', '二维码', '扫码'];
        const foundQrKeywords = qrKeywords.filter(keyword =>
            content.toLowerCase().includes(keyword.toLowerCase())
        );
        
        console.log(`📱 找到二维码关键词: ${foundQrKeywords.length > 0 ? foundQrKeywords.join(', ') : '无'}`);
        
        // 提取标题
        const titleMatch = content.match(/<title[^>]*>([^<]+)<\/title>/i);
        const title = titleMatch ? titleMatch[1].trim() : '未找到标题';
        
        console.log(`📰 页面标题: ${title}`);
        
        // 检查是否需要登录
        const requiresLogin = foundKeywords.length > 0 || 
                             content.includes('login') || 
                             content.includes('signin');
        
        // 4. 保存结果
        const resultDir = path.join(__dirname, 'boss_results');
        if (!fs.existsSync(resultDir)) {
            fs.mkdirSync(resultDir, { recursive: true });
        }
        
        const timestamp = new Date().getTime();
        const contentFile = path.join(resultDir, `boss_content_${timestamp}.html`);
        const summaryFile = path.join(resultDir, `boss_summary_${timestamp}.txt`);
        
        // 保存原始内容
        fs.writeFileSync(contentFile, content);
        
        // 保存摘要
        const summary = `
BOSS直聘访问测试结果
===================
时间: ${new Date().toISOString()}
URL: ${url}
标题: ${title}
HTTP状态码: ${pingResult.stdout.trim()}
内容大小: ${size} 字节
需要登录: ${requiresLogin ? '是' : '否'}
找到登录关键词: ${foundKeywords.join(', ') || '无'}
找到二维码关键词: ${foundQrKeywords.join(', ') || '无'}
检测到重定向: ${finalUrlMatch ? '是' : '否'}
内容文件: ${contentFile}
        `.trim();
        
        fs.writeFileSync(summaryFile, summary);
        
        console.log('\n💾 结果已保存:');
        console.log(`   📄 原始内容: ${contentFile}`);
        console.log(`   📋 摘要: ${summaryFile}`);
        
        // 5. 显示关键信息
        console.log('\n' + '='.repeat(40));
        console.log('📊 关键发现:');
        console.log('='.repeat(40));
        
        if (requiresLogin) {
            console.log('🔐 需要登录才能访问');
            
            if (foundQrKeywords.length > 0) {
                console.log('📱 页面可能包含二维码登录');
                console.log('💡 建议: 使用浏览器工具进行完整交互和截图');
            } else {
                console.log('📝 可能是普通登录页面（用户名/密码）');
            }
        } else {
            console.log('🎉 可以直接访问，不需要登录');
        }
        
        // 提取页面预览
        console.log('\n📄 页面预览（前500字符）:');
        const preview = content
            .replace(/<[^>]*>/g, ' ') // 移除HTML标签
            .replace(/\s+/g, ' ')     // 合并空格
            .trim()
            .substring(0, 500);
        
        console.log(preview + '...');
        
        return {
            success: true,
            url: url,
            title: title,
            requiresLogin: requiresLogin,
            hasQrCodeKeywords: foundQrKeywords.length > 0,
            httpStatus: pingResult.stdout.trim(),
            contentSize: size,
            contentFile: contentFile,
            summaryFile: summaryFile,
            preview: preview
        };
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
        
        return {
            success: false,
            error: error.message,
            url: url
        };
    }
}

// 运行测试
if (require.main === module) {
    testBossWebsite()
        .then(result => {
            console.log('\n' + '='.repeat(40));
            console.log('🎯 测试完成');
            console.log('='.repeat(40));
            
            if (result.success) {
                console.log(`✅ 访问成功`);
                console.log(`📰 标题: ${result.title}`);
                console.log(`🔐 需要登录: ${result.requiresLogin ? '是' : '否'}`);
                console.log(`📱 二维码关键词: ${result.hasQrCodeKeywords ? '找到' : '未找到'}`);
                
                console.log('\n💡 下一步建议:');
                if (result.requiresLogin) {
                    console.log('1. 使用浏览器工具进行完整交互');
                    console.log('2. 可能需要处理登录页面');
                    console.log('3. 如果使用二维码登录，需要截图功能');
                } else {
                    console.log('1. 可以直接使用web_fetch获取内容');
                    console.log('2. 使用smart-web-fetcher进行智能获取');
                }
            } else {
                console.log(`❌ 访问失败: ${result.error}`);
                console.log('\n💡 可能的原因:');
                console.log('1. 网络连接问题');
                console.log('2. 网站屏蔽了curl请求');
                console.log('3. 需要处理反爬虫机制');
            }
        })
        .catch(error => {
            console.error('❌ 执行错误:', error);
            process.exit(1);
        });
}

module.exports = testBossWebsite;