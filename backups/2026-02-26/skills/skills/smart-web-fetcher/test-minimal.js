#!/usr/bin/env node
/**
 * 最小化测试 - 不依赖外部模块
 */

console.log('🧪 智能网络获取系统 - 结构测试\n');

// 检查文件结构
const fs = require('fs');
const path = require('path');

const files = [
    'SKILL.md',
    'README.md',
    'package.json',
    'scripts/smart-fetch.js',
    'scripts/router.js',
    'scripts/dom-compressor.js',
    'config/config.example.json',
    'examples/basic-usage.js'
];

console.log('📁 文件结构检查:');
let allFilesExist = true;

files.forEach(file => {
    const fullPath = path.join(__dirname, file);
    const exists = fs.existsSync(fullPath);
    console.log(`  ${exists ? '✅' : '❌'} ${file}`);
    if (!exists) allFilesExist = false;
});

console.log(`\n${allFilesExist ? '✅ 所有文件都存在' : '❌ 部分文件缺失'}`);

// 检查配置文件
console.log('\n⚙️ 配置文件检查:');
try {
    const configExample = path.join(__dirname, 'config/config.example.json');
    if (fs.existsSync(configExample)) {
        const config = JSON.parse(fs.readFileSync(configExample, 'utf8'));
        console.log('✅ 配置文件格式正确');
        console.log(`   路由规则: ${config.routing?.dynamicSites?.length || 0} 个动态网站模式`);
        console.log(`   压缩策略: ${Object.keys(config.compression?.strategies || {}).length} 种策略`);
    }
} catch (error) {
    console.log(`❌ 配置文件错误: ${error.message}`);
}

// 检查脚本可执行性
console.log('\n📜 脚本可执行性检查:');
const scripts = [
    'scripts/smart-fetch.js',
    'scripts/router.js',
    'scripts/dom-compressor.js'
];

scripts.forEach(script => {
    const fullPath = path.join(__dirname, script);
    if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf8');
        const hasShebang = content.startsWith('#!/usr/bin/env node');
        console.log(`  ${hasShebang ? '✅' : '⚠️'} ${script} ${hasShebang ? '有正确的shebang' : '缺少shebang'}`);
    }
});

// 显示技能信息
console.log('\n📋 技能信息:');
try {
    const skillPath = path.join(__dirname, 'SKILL.md');
    const skillContent = fs.readFileSync(skillPath, 'utf8');
    
    // 提取YAML frontmatter
    const match = skillContent.match(/^---\n([\s\S]*?)\n---/);
    if (match) {
        const frontmatter = match[1];
        const lines = frontmatter.split('\n');
        
        lines.forEach(line => {
            if (line.includes(':')) {
                const [key, value] = line.split(':').map(s => s.trim());
                console.log(`  ${key}: ${value}`);
            }
        });
    }
} catch (error) {
    console.log(`❌ 无法读取技能信息: ${error.message}`);
}

// 使用说明
console.log('\n🚀 使用说明:');
console.log('='.repeat(50));
console.log('1. 安装依赖:');
console.log('   cd ~/.openclaw/workspace/skills/smart-web-fetcher');
console.log('   npm install jsdom');
console.log('');
console.log('2. 测试基本功能:');
console.log('   node test-simple.js');
console.log('');
console.log('3. 运行示例:');
console.log('   node examples/basic-usage.js');
console.log('');
console.log('4. 获取帮助:');
console.log('   node scripts/smart-fetch.js --help');
console.log('='.repeat(50));

console.log('\n🎉 结构测试完成！');
console.log('💡 提示: 这是一个完整的技能包，需要安装依赖后才能完全运行。');