const fs = require('fs');
const { JSDOM } = require('jsdom');

// 读取简单测试文件
const html = fs.readFileSync('/tmp/simple_test.html', 'utf8');
console.log('HTML 长度:', html.length, '字符');

const dom = new JSDOM(html);
const doc = dom.window.document;

// 检查元素
console.log('\n=== 检查元素 ===');
const elements = doc.querySelectorAll('a, button, input, select, textarea');
console.log('找到', elements.length, '个交互元素');

elements.forEach((el, i) => {
    const tag = el.tagName.toLowerCase();
    const text = el.textContent?.trim().slice(0, 50) || '';
    const placeholder = el.getAttribute('placeholder')?.slice(0, 50) || '';
    const href = el.getAttribute('href');
    const name = el.getAttribute('name') || el.getAttribute('id') || '';
    
    console.log(`[${i}] ${tag.toUpperCase()}:`, {
        text,
        placeholder,
        href,
        name,
        offsetParent: el.offsetParent,
        parentNode: el.parentNode?.tagName
    });
});

// 现在测试完整的压缩函数
console.log('\n=== 测试完整压缩函数 ===');
const { compressHTMLString } = require('./dom-compressor.js');
const result = compressHTMLString(html, { maxTextLength: 500, maxActions: 10 });
console.log('压缩结果:', result.stats);
console.log('压缩输出:');
console.log(result.compressed);
