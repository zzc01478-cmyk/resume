/**
 * DOM Compressor for AI Agents
 * 
 * 使用方法:
 *   node dom-compressor.js                           # 压缩当前浏览器页面
 *   node dom-compressor.js input.html               # 压缩指定HTML文件
 *   node dom-compressor.js -- CDP_URL=http://127.0.0.1:9222  # 指定CDP地址
 * 
 * 输出格式:
 *   [PAGE] https://example.com
 *   [TITLE] Page Title
 *   [SUMMARY] Main visible text content...
 *   [ACTIONS]
 *   [LINK] Link Text -> https://...
 *   [BTN] Button Text
 *   [INPUT] name=xxx placeholder=xxx
 */

const fs = require('fs');
const { chromium } = require('playwright');
const { JSDOM } = require('jsdom');

const CDP_URL = process.env.CDP_URL || 'http://127.0.0.1:9222';

/**
 * 压缩 HTML 字符串
 */
function compressHTMLString(html, options = {}) {
    const { maxTextLength = 1500, maxActions = 20 } = options;
    
    const dom = new JSDOM(html);
    const doc = dom.window.document;
    
    // 移除无用标签
    doc.querySelectorAll('script, style, noscript, template, svg, canvas, iframe, link, meta').forEach(el => el.remove());
    
    const title = doc.title || '';
    
    // 获取主要文本内容
    let mainContent = '';
    const mainSelectors = ['main', 'article', '.main', '#main', '.content', '#content', '.container', '#container', '.page'];
    for (const sel of mainSelectors) {
        const el = doc.querySelector(sel);
        if (el && el.textContent?.trim().length > 100) {
            mainContent = el.textContent.replace(/\s+/g, ' ').trim().slice(0, maxTextLength);
            break;
        }
    }
    if (!mainContent) {
        mainContent = doc.body?.textContent?.replace(/\s+/g, ' ').trim().slice(0, maxTextLength) || '';
    }
    
    // 提取交互元素
    const interactive = [];
    doc.querySelectorAll('a, button, input, select, textarea').forEach(el => {
        if (el.offsetParent === null) return; // 跳过隐藏元素
        
        const tag = el.tagName.toLowerCase();
        const text = el.textContent?.trim().slice(0, 50) || '';
        const placeholder = el.getAttribute('placeholder')?.slice(0, 50) || '';
        const href = el.getAttribute('href');
        const name = el.getAttribute('name') || el.getAttribute('id') || '';
        
        if (tag === 'a' && href && !href.startsWith('javascript') && !href.startsWith('#')) {
            interactive.push('[LINK] ' + (text || 'unnamed') + ' -> ' + href);
        } else if (tag === 'button' && text) {
            interactive.push('[BTN] ' + text);
        } else if (tag === 'input' && (placeholder || name)) {
            interactive.push('[INPUT] name=' + name + ' placeholder=' + (placeholder || ''));
        } else if (tag === 'select' && name) {
            const opts = Array.from(el.querySelectorAll('option')).slice(0, 5).map(o => o.textContent?.trim()).join(',');
            interactive.push('[SELECT] ' + name + ' [' + opts + ']');
        } else if (tag === 'textarea' && name) {
            interactive.push('[TEXTAREA] ' + name);
        }
    });
    
    const output = '[TITLE] ' + title + '\n[SUMMARY] ' + mainContent + '\n[ACTIONS]\n' + interactive.slice(0, maxActions).join('\n');
    
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

/**
 * 连接浏览器并压缩当前页面
 */
async function compressCurrentPage(cdpUrl = CDP_URL) {
    console.log('Connecting to browser at:', cdpUrl);
    
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

/**
 * 主入口
 */
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        // 压缩当前浏览器页面
        await compressCurrentPage();
    } else if (args[0].startsWith('http')) {
        // 作为 CDP URL
        await compressCurrentPage(args[0]);
    } else {
        // 压缩指定文件
        const inputFile = args[0];
        if (!fs.existsSync(inputFile)) {
            console.error('File not found:', inputFile);
            process.exit(1);
        }
        const html = fs.readFileSync(inputFile, 'utf8');
        const result = compressHTMLString(html);
        console.log('=== Compression Result ===');
        console.log(result.stats);
        console.log('\n=== Compressed Output ===');
        console.log(result.compressed);
    }
}

module.exports = { compressHTMLString, compressCurrentPage };

if (require.main === module) {
    main().catch(console.error);
}
