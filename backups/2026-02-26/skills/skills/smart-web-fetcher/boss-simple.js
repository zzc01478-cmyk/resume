#!/usr/bin/env node
/**
 * 简单的BOSS直聘访问工具 - 直接使用Playwright
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class BossScanner {
    constructor() {
        this.screenshotDir = path.join(__dirname, 'screenshots');
        this.ensureScreenshotDir();
    }
    
    ensureScreenshotDir() {
        if (!fs.existsSync(this.screenshotDir)) {
            fs.mkdirSync(this.screenshotDir, { recursive: true });
        }
    }
    
    async scanBossWebsite(url = 'https://www.zhipin.com') {
        console.log('🚀 开始访问BOSS直聘...');
        console.log(`🌐 目标URL: ${url}`);
        
        let browser = null;
        let page = null;
        
        try {
            // 启动浏览器
            console.log('🖥️ 启动浏览器...');
            browser = await chromium.launch({ 
                headless: true, // 无头模式，服务器没有图形界面
                timeout: 30000
            });
            
            // 创建页面
            page = await browser.newPage();
            
            // 设置用户代理
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
            
            // 导航到页面
            console.log('🌐 导航到页面...');
            await page.goto(url, { 
                waitUntil: 'networkidle',
                timeout: 30000
            });
            
            // 等待页面加载
            await page.waitForTimeout(2000);
            
            // 获取页面信息
            const title = await page.title();
            const currentUrl = page.url();
            
            console.log(`📰 页面标题: ${title}`);
            console.log(`🔗 当前URL: ${currentUrl}`);
            
            // 检查是否需要登录
            const loginCheck = await this.checkLoginPage(page);
            console.log(`🔐 登录页面: ${loginCheck.isLoginPage ? '是' : '否'}`);
            
            let result = {
                success: true,
                url: currentUrl,
                title: title,
                isLoginPage: loginCheck.isLoginPage,
                requiresLogin: loginCheck.isLoginPage,
                qrCodeFound: false,
                qrCodeImage: null,
                pageScreenshot: null,
                loginCheck: loginCheck
            };
            
            // 如果需要登录，查找二维码
            if (loginCheck.isLoginPage) {
                console.log('🔍 查找二维码...');
                const qrCodeInfo = await this.findQRCode(page);
                result.qrCodeFound = qrCodeInfo.found;
                
                if (qrCodeInfo.found) {
                    console.log(`✅ 找到二维码: ${qrCodeInfo.description}`);
                    
                    // 截图二维码
                    const qrScreenshot = await this.screenshotQRCode(page, qrCodeInfo);
                    result.qrCodeImage = qrScreenshot;
                } else {
                    console.log('❌ 未找到二维码');
                }
            }
            
            // 截图整个页面
            console.log('📸 截图页面...');
            const pageScreenshot = await this.screenshotPage(page);
            result.pageScreenshot = pageScreenshot;
            
            // 保存截图
            this.saveScreenshots(result);
            
            return result;
            
        } catch (error) {
            console.error('❌ 访问失败:', error.message);
            return {
                success: false,
                error: error.message,
                stack: error.stack
            };
        } finally {
            // 关闭浏览器
            if (browser) {
                await browser.close();
                console.log('🖥️ 浏览器已关闭');
            }
        }
    }
    
    async checkLoginPage(page) {
        try {
            // 方法1: 检查URL
            const url = page.url();
            const urlChecks = [
                url.includes('/login'),
                url.includes('/signin'),
                url.includes('auth'),
                url.includes('passport')
            ];
            
            if (urlChecks.some(check => check)) {
                return { isLoginPage: true, reason: 'URL包含登录关键词' };
            }
            
            // 方法2: 检查页面元素
            const loginSelectors = [
                '[class*="login"]',
                '[class*="signin"]',
                '#loginForm',
                '.login-container',
                '.signin-box',
                'input[type="password"]',
                'button:has-text("登录")',
                'button:has-text("Sign in")',
                'button:has-text("Log in")'
            ];
            
            for (const selector of loginSelectors) {
                try {
                    const element = await page.$(selector);
                    if (element) {
                        const isVisible = await element.isVisible();
                        if (isVisible) {
                            return { isLoginPage: true, reason: `找到登录元素: ${selector}` };
                        }
                    }
                } catch (e) {
                    // 忽略选择器错误
                }
            }
            
            // 方法3: 检查页面文本
            const content = await page.content();
            const loginKeywords = [
                '登录', 'sign in', 'log in', '手机验证', '二维码登录',
                '扫码登录', '微信登录', '密码登录', '验证码登录'
            ];
            
            for (const keyword of loginKeywords) {
                if (content.toLowerCase().includes(keyword.toLowerCase())) {
                    return { isLoginPage: true, reason: `找到登录关键词: ${keyword}` };
                }
            }
            
            return { isLoginPage: false, reason: '未检测到登录页面特征' };
            
        } catch (error) {
            console.error('检查登录页面时出错:', error);
            return { isLoginPage: false, reason: `检查出错: ${error.message}` };
        }
    }
    
    async findQRCode(page) {
        try {
            // 查找二维码元素
            const qrCodeSelectors = [
                '[class*="qrcode"]',
                '[class*="qr-code"]',
                '[class*="qrcode-login"]',
                '.qrcode-box',
                '.qrcode-container',
                'canvas[class*="qrcode"]',
                'img[src*="qrcode"]',
                'img[alt*="二维码"]',
                'img[alt*="QR"]',
                'div:has-text("扫码登录")',
                'div:has-text("二维码登录")'
            ];
            
            for (const selector of qrCodeSelectors) {
                try {
                    const element = await page.$(selector);
                    if (element) {
                        const isVisible = await element.isVisible();
                        if (isVisible) {
                            const boundingBox = await element.boundingBox();
                            if (boundingBox) {
                                // 获取元素描述
                                let description = '二维码元素';
                                try {
                                    const text = await element.textContent();
                                    if (text && text.trim()) {
                                        description = text.trim().substring(0, 50);
                                    }
                                } catch (e) {
                                    // 忽略错误
                                }
                                
                                return {
                                    found: true,
                                    selector: selector,
                                    description: description,
                                    boundingBox: boundingBox
                                };
                            }
                        }
                    }
                } catch (e) {
                    // 忽略选择器错误
                }
            }
            
            // 查找二维码图片
            const images = await page.$$('img');
            for (const img of images) {
                try {
                    const src = await img.getAttribute('src');
                    const alt = await img.getAttribute('alt') || '';
                    
                    if (src && (src.includes('qrcode') || alt.includes('二维码') || alt.includes('QR'))) {
                        const isVisible = await img.isVisible();
                        if (isVisible) {
                            const boundingBox = await img.boundingBox();
                            if (boundingBox) {
                                return {
                                    found: true,
                                    selector: 'img',
                                    description: `二维码图片: ${alt || src.substring(0, 50)}`,
                                    boundingBox: boundingBox
                                };
                            }
                        }
                    }
                } catch (e) {
                    // 忽略错误
                }
            }
            
            return {
                found: false,
                description: '未找到二维码'
            };
            
        } catch (error) {
            console.error('查找二维码时出错:', error);
            return {
                found: false,
                description: `查找错误: ${error.message}`
            };
        }
    }
    
    async screenshotQRCode(page, qrCodeInfo) {
        try {
            const timestamp = new Date().getTime();
            const filename = `boss_qrcode_${timestamp}.png`;
            const filepath = path.join(this.screenshotDir, filename);
            
            // 截图二维码区域（扩大范围）
            const padding = 20;
            const clip = {
                x: Math.max(0, qrCodeInfo.boundingBox.x - padding),
                y: Math.max(0, qrCodeInfo.boundingBox.y - padding),
                width: qrCodeInfo.boundingBox.width + (padding * 2),
                height: qrCodeInfo.boundingBox.height + (padding * 2)
            };
            
            await page.screenshot({
                path: filepath,
                clip: clip
            });
            
            // 读取图片
            const imageBuffer = fs.readFileSync(filepath);
            
            return {
                path: filepath,
                base64: imageBuffer.toString('base64'),
                clip: clip,
                timestamp: timestamp
            };
            
        } catch (error) {
            console.error('截图二维码时出错:', error);
            return null;
        }
    }
    
    async screenshotPage(page) {
        try {
            const timestamp = new Date().getTime();
            const filename = `boss_page_${timestamp}.png`;
            const filepath = path.join(this.screenshotDir, filename);
            
            await page.screenshot({
                path: filepath,
                fullPage: false // 只截图可视区域
            });
            
            const imageBuffer = fs.readFileSync(filepath);
            
            return {
                path: filepath,
                base64: imageBuffer.toString('base64'),
                timestamp: timestamp
            };
            
        } catch (error) {
            console.error('截图页面时出错:', error);
            return null;
        }
    }
    
    saveScreenshots(result) {
        console.log('\n💾 保存截图...');
        
        if (result.qrCodeImage) {
            console.log(`✅ 二维码截图: ${result.qrCodeImage.path}`);
        }
        
        if (result.pageScreenshot) {
            console.log(`✅ 页面截图: ${result.pageScreenshot.path}`);
        }
        
        console.log(`📁 所有截图保存在: ${this.screenshotDir}`);
    }
    
    displayResult(result) {
        console.log('\n' + '='.repeat(60));
        console.log('📊 BOSS直聘访问结果');
        console.log('='.repeat(60));
        
        if (!result.success) {
            console.log(`❌ 失败: ${result.error}`);
            return;
        }
        
        console.log(`✅ 访问成功`);
        console.log(`🌐 URL: ${result.url}`);
        console.log(`📰 标题: ${result.title}`);
        console.log(`🔐 需要登录: ${result.requiresLogin ? '是' : '否'}`);
        
        if (result.loginCheck) {
            console.log(`🔍 登录检查: ${result.loginCheck.reason}`);
        }
        
        if (result.requiresLogin) {
            console.log(`📱 找到二维码: ${result.qrCodeFound ? '是' : '否'}`);
            
            if (result.qrCodeFound) {
                console.log(`🖼️ 二维码描述: ${result.qrCodeImage?.description || '无描述'}`);
                console.log(`💾 二维码文件: ${result.qrCodeImage?.path || '未保存'}`);
                
                if (result.qrCodeImage?.path) {
                    console.log(`📎 二维码路径: ${result.qrCodeImage.path}`);
                }
            }
        }
        
        if (result.pageScreenshot?.path) {
            console.log(`📸 页面截图: ${result.pageScreenshot.path}`);
        }
        
        console.log('='.repeat(60));
        
        return result;
    }
}

// 命令行接口
if (require.main === module) {
    const scanner = new BossScanner();
    const args = process.argv.slice(2);
    
    const url = args[0] || 'https://www.zhipin.com';
    
    console.log('🚀 BOSS直聘访问工具');
    console.log('='.repeat(40));
    
    scanner.scanBossWebsite(url)
        .then(result => {
            const finalResult = scanner.displayResult(result);
            
            // 如果需要二维码，提供下一步建议
            if (finalResult && finalResult.requiresLogin && finalResult.qrCodeFound) {
                console.log('\n📱 检测到登录二维码');
                console.log('💡 下一步:');
                console.log('  1. 使用微信扫描二维码登录');
                console.log('  2. 登录成功后页面会自动跳转');
                console.log('  3. 二维码截图已保存，可以发送给你');
                
                // 这里可以添加发送截图的逻辑
                if (finalResult.qrCodeImage?.path) {
                    console.log(`\n📎 二维码文件: ${finalResult.qrCodeImage.path}`);
                }
            } else if (finalResult && !finalResult.requiresLogin) {
                console.log('\n🎉 不需要登录，可以直接访问！');
                console.log(`📎 页面截图: ${finalResult.pageScreenshot?.path}`);
            }
        })
        .catch(error => {
            console.error('❌ 执行失败:', error);
            process.exit(1);
        });
}

module.exports = BossScanner;