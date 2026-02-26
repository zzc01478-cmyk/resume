/**
 * 增强版 DOM Compressor - 支持图片提取
 */
const fs = require('fs');
const { chromium } = require('playwright');
const { JSDOM } = require('jsdom');

const CDP_URL = process.env.CDP_URL || 'http://127.0.0.1:9222';

/**
 * 压缩 HTML 字符串（增强版：支持图片提取）
 */
function compressHTMLString(html, options = {}) {
    const { 
        maxTextLength = 1500, 
        maxActions = 20,
        maxImages = 10,
        includeImages = true  // 是否包含图片信息
    } = options;
    
    const dom = new JSDOM(html);
    const doc = dom.window.document;
    
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
    
    // 提取图片信息（如果启用）
    const images = [];
    if (includeImages) {
        doc.querySelectorAll('img').forEach((img, index) => {
            if (index >= maxImages) return;
            
            const src = img.getAttribute('src') || '';
            const alt = img.getAttribute('alt') || '';
            const titleAttr = img.getAttribute('title') || '';
            const width = img.getAttribute('width') || '';
            const height = img.getAttribute('height') || '';
            
            if (src) {
                let imgInfo = '[IMG]';
                if (alt) imgInfo += ' alt="' + alt + '"';
                if (titleAttr) imgInfo += ' title="' + titleAttr + '"';
                imgInfo += ' src="' + src + '"';
                if (width || height) imgInfo += ' size=' + width + 'x' + height;
                
                // 检查图片是否在链接内
                const parentLink = img.closest('a');
                if (parentLink && parentLink.href) {
                    imgInfo += ' [in link -> ' + parentLink.href + ']';
                }
                
                images.push(imgInfo);
            }
        });
        
        // 提取背景图片
        const elementsWithBg = doc.querySelectorAll('*');
        elementsWithBg.forEach((el, index) => {
            if (index >= 20) return; // 限制检查数量
            
            const style = el.getAttribute('style') || '';
            const bgMatch = style.match(/background-image:\s*url\(['"]?([^'"()]+)['"]?\)/i);
            if (bgMatch && bgMatch[1]) {
                images.push('[BG-IMG] src="' + bgMatch[1] + '"');
            }
        });
    }
    
    // 构建输出
    let output = '[TITLE] ' + title + '\n[SUMMARY] ' + mainContent;
    
    if (images.length > 0) {
        output += '\n[IMAGES]\n' + images.slice(0, maxImages).join('\n');
    }
    
    if (interactive.length > 0) {
        output += '\n[ACTIONS]\n' + interactive.slice(0, maxActions).join('\n');
    }
    
    const originalSize = Buffer.byteLength(html, 'utf8');
    const compressedSize = Buffer.byteLength(output, 'utf8');
    
    return {
        compressed: output,
        stats: {
            originalSize,
            compressedSize,
            reduction: ((originalSize - compressedSize) / originalSize * 100).toFixed(2) + '%',
            imagesFound: images.length,
            interactiveFound: interactive.length
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
        console.error('用法: node dom-compressor-with-images.js <html文件> [--no-images]');
        process.exit(1);
    }
    
    const inputFile = args[0];
    const includeImages = !args.includes('--no-images');
    
    if (!fs.existsSync(inputFile)) {
        console.error('文件未找到:', inputFile);
        process.exit(1);
    }
    
    const html = fs.readFileSync(inputFile, 'utf8');
    const result = compressHTMLString(html, { includeImages });
    
    console.log('=== 增强版压缩结果 ===');
    console.log('原始大小:', result.stats.originalSize, '字节');
    console.log('压缩大小:', result.stats.compressedSize, '字节');
    console.log('压缩率:', result.stats.reduction);
    console.log('发现图片:', result.stats.imagesFound, '个');
    console.log('交互元素:', result.stats.interactiveFound, '个');
    console.log('\n=== 压缩输出 ===');
    console.log(result.compressed);
}

module.exports = { compressHTMLString };

if (require.main === module) {
    main().catch(console.error);
}