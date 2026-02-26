/**
 * 修改版 DOM Compressor - 禁用 offsetParent 检查
 */
const fs = require('fs');
const { chromium } = require('playwright');
const { JSDOM } = require('jsdom');

const CDP_URL = process.env.CDP_URL || 'http://127.0.0.1:9222';

/**
 * 压缩 HTML 字符串（修改版：禁用 offsetParent 检查）
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
    
    // 提取交互元素（修改：移除 offsetParent 检查）
    const interactive = [];
    doc.querySelectorAll('a, button, input, select, textarea').forEach(el => {
        // 移除 offsetParent 检查：if (el.offsetParent === null) return;
        
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
 * 主入口
 */
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('请提供HTML文件路径');
        process.exit(1);
    } else {
        // 压缩指定文件
        const inputFile = args[0];
        if (!fs.existsSync(inputFile)) {
            console.error('文件未找到:', inputFile);
            process.exit(1);
        }
        const html = fs.readFileSync(inputFile, 'utf8');
        const result = compressHTMLString(html);
        console.log('=== 压缩结果（修改版）===');
        console.log('原始大小:', result.stats.originalSize, '字节');
        console.log('压缩大小:', result.stats.compressedSize, '字节');
        console.log('压缩率:', result.stats.reduction);
        console.log('\n=== 压缩输出 ===');
        console.log(result.compressed);
    }
}

module.exports = { compressHTMLString };

if (require.main === module) {
    main().catch(console.error);
}