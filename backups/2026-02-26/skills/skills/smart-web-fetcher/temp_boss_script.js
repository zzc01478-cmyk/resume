
const { PlaywrightCrawler } = require('crawlee');
const path = require('path');
const fs = require('fs');

// 确保截图目录存在
const screenshotDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
}

const crawler = new PlaywrightCrawler({
    maxRequestsPerCrawl: 1,
    requestHandlerTimeoutSecs: 30,
    headless: false, // 使用有头模式以便截图
    
    async requestHandler({ request, page, log }) {
        try {
            log.info(`导航到: ${request.url}`);
            
            // 设置用户代理，模拟真实浏览器
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
            
            // 导航到页面
            await page.goto(request.url, { 
                waitUntil: 'networkidle',
                timeout: 30000
            });
            
            // 等待页面加载
            await page.waitForTimeout(2000);
            
            // 获取页面信息
            const title = await page.title();
            const url = await page.url();
            const hasLoginPage = await this.checkLoginPage(page);
            
            log.info(`页面标题: ${title}`);
            log.info(`当前URL: ${url}`);
            log.info(`登录页面: ${hasLoginPage ? '是' : '否'}`);
            
            let result = {
                success: true,
                url: url,
                title: title,
                hasLoginPage: hasLoginPage,
                requiresLogin: false,
                qrCodeFound: false,
                qrCodeImage: null,
                pageContent: null,
                screenshot: null
            };
            
            // 检查是否需要登录
            if (hasLoginPage) {
                log.info('检测到登录页面，检查二维码...');
                
                // 查找二维码
                const qrCodeInfo = await this.findQRCode(page);
                result.qrCodeFound = qrCodeInfo.found;
                result.requiresLogin = true;
                
                if (qrCodeInfo.found) {
                    log.info(`找到二维码: ${qrCodeInfo.description}`);
                    
                    // 截图二维码区域
                    const qrScreenshot = await this.screenshotQRCode(page, qrCodeInfo);
                    result.qrCodeImage = qrScreenshot;
                    
                    // 截图整个页面
                    const fullScreenshot = await page.screenshot({
                        path: path.join(screenshotDir, 'boss_full_page.png'),
                        fullPage: false
                    });
                    result.screenshot = fullScreenshot.toString('base64');
                }
            } else {
                // 不需要登录，获取页面内容
                result.pageContent = await page.content();
                
                // 截图页面
                const screenshot = await page.screenshot({
                    path: path.join(screenshotDir, 'boss_page.png'),
                    fullPage: false
                });
                result.screenshot = screenshot.toString('base64');
            }
            
            // 输出结果
            console.log(JSON.stringify(result));
            
        } catch (error) {
            console.log(JSON.stringify({
                success: false,
                error: error.message,
                stack: error.stack
            }));
        }
    },
    
    async checkLoginPage(page) {
        try {
            // 检查常见的登录页面特征
            const checks = [
                // 检查URL
                () => page.url().includes('/login') || page.url().includes('/signin'),
                
                // 检查页面元素
                async () => {
                    const selectors = [
                        '[class*="login"]',
                        '[class*="signin"]',
                        '#loginForm',
                        '.login-container',
                        '.signin-box',
                        'input[type="password"]',
                        'button:has-text("登录")',
                        'button:has-text("Sign in")'
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const element = await page.$(selector);
                            if (element) return true;
                        } catch (e) {
                            // 忽略选择器错误
                        }
                    }
                    return false;
                },
                
                // 检查页面文本
                async () => {
                    const content = await page.content();
                    const loginKeywords = ['登录', 'sign in', 'log in', '手机验证', '二维码登录'];
                    return loginKeywords.some(keyword => content.toLowerCase().includes(keyword.toLowerCase()));
                }
            ];
            
            for (const check of checks) {
                if (await check()) {
                    return true;
                }
            }
            
            return false;
            
        } catch (error) {
            console.error('检查登录页面时出错:', error);
            return false;
        }
    },
    
    async findQRCode(page) {
        try {
            // 常见的二维码选择器
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
                        const boundingBox = await element.boundingBox();
                        if (boundingBox) {
                            return {
                                found: true,
                                selector: selector,
                                description: await this.getElementDescription(page, element),
                                boundingBox: boundingBox
                            };
                        }
                    }
                } catch (e) {
                    // 忽略选择器错误
                }
            }
            
            // 如果没有找到明确的二维码元素，检查页面中是否有二维码图片
            const images = await page.$$('img');
            for (const img of images) {
                try {
                    const src = await img.getAttribute('src');
                    const alt = await img.getAttribute('alt') || '';
                    
                    if (src && (src.includes('qrcode') || alt.includes('二维码') || alt.includes('QR'))) {
                        const boundingBox = await img.boundingBox();
                        if (boundingBox) {
                            return {
                                found: true,
                                selector: 'img',
                                description: `二维码图片: ${alt || src}`,
                                boundingBox: boundingBox
                            };
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
    },
    
    async getElementDescription(page, element) {
        try {
            // 获取元素的文本内容
            const text = await element.textContent();
            if (text && text.trim().length > 0) {
                return text.trim().substring(0, 100);
            }
            
            // 获取alt或title属性
            const alt = await element.getAttribute('alt');
            if (alt) return alt;
            
            const title = await element.getAttribute('title');
            if (title) return title;
            
            // 获取class名称
            const className = await element.getAttribute('class');
            if (className) return `class: ${className}`;
            
            return '未知元素';
            
        } catch (error) {
            return '无法获取描述';
        }
    },
    
    async screenshotQRCode(page, qrCodeInfo) {
        try {
            const timestamp = new Date().getTime();
            const screenshotPath = path.join(screenshotDir, `boss_qrcode_${timestamp}.png`);
            
            // 截图二维码区域（稍微扩大一点范围）
            const padding = 20;
            const clip = {
                x: Math.max(0, qrCodeInfo.boundingBox.x - padding),
                y: Math.max(0, qrCodeInfo.boundingBox.y - padding),
                width: qrCodeInfo.boundingBox.width + (padding * 2),
                height: qrCodeInfo.boundingBox.height + (padding * 2)
            };
            
            await page.screenshot({
                path: screenshotPath,
                clip: clip
            });
            
            // 读取图片并转换为base64
            const imageBuffer = fs.readFileSync(screenshotPath);
            
            return {
                path: screenshotPath,
                base64: imageBuffer.toString('base64'),
                clip: clip,
                timestamp: timestamp
            };
            
        } catch (error) {
            console.error('截图二维码时出错:', error);
            return null;
        }
    }
});

// 启动爬取
(async () => {
    await crawler.run(['https://www.zhipin.com']);
})();
            