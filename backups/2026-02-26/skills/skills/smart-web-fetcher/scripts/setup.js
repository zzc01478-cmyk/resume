#!/usr/bin/env node
/**
 * 智能网络获取系统安装脚本
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class SetupScript {
    constructor() {
        this.baseDir = path.join(__dirname, '..');
        this.configDir = path.join(this.baseDir, 'config');
        this.scriptDir = path.join(this.baseDir, 'scripts');
        this.exampleDir = path.join(this.baseDir, 'examples');
    }
    
    async run() {
        console.log('🚀 智能网络获取系统安装向导\n');
        
        try {
            // 1. 检查Node.js版本
            await this.checkNodeVersion();
            
            // 2. 创建目录结构
            this.createDirectories();
            
            // 3. 复制配置文件
            this.copyConfigFiles();
            
            // 4. 安装依赖
            await this.installDependencies();
            
            // 5. 设置环境
            await this.setupEnvironment();
            
            // 6. 测试安装
            await this.testInstallation();
            
            console.log('\n🎉 安装完成！');
            this.showNextSteps();
            
        } catch (error) {
            console.error(`\n❌ 安装失败: ${error.message}`);
            process.exit(1);
        }
    }
    
    async checkNodeVersion() {
        console.log('1. 检查Node.js版本...');
        
        const { stdout } = await execAsync('node --version');
        const version = stdout.trim().replace('v', '');
        const [major] = version.split('.').map(Number);
        
        if (major < 16) {
            throw new Error(`Node.js版本过低 (${version})，需要16.0.0或更高版本`);
        }
        
        console.log(`   ✅ Node.js ${version}`);
    }
    
    createDirectories() {
        console.log('2. 创建目录结构...');
        
        const directories = [
            'config',
            'examples',
            'logs',
            'cache'
        ];
        
        directories.forEach(dir => {
            const dirPath = path.join(this.baseDir, dir);
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
                console.log(`   📁 创建: ${dir}`);
            }
        });
        
        console.log('   ✅ 目录结构创建完成');
    }
    
    copyConfigFiles() {
        console.log('3. 复制配置文件...');
        
        const configFiles = [
            { source: 'config.example.json', target: 'config.json' },
            { source: 'sites.example.json', target: 'sites.json' },
            { source: 'strategies.example.json', target: 'strategies.json' }
        ];
        
        configFiles.forEach(({ source, target }) => {
            const sourcePath = path.join(this.configDir, source);
            const targetPath = path.join(this.configDir, target);
            
            if (fs.existsSync(sourcePath) && !fs.existsSync(targetPath)) {
                fs.copyFileSync(sourcePath, targetPath);
                console.log(`   📄 复制: ${source} → ${target}`);
            }
        });
        
        console.log('   ✅ 配置文件复制完成');
    }
    
    async installDependencies() {
        console.log('4. 安装依赖...');
        
        const dependencies = [
            { name: 'crawlee', command: 'npm install crawlee' },
            { name: 'playwright', command: 'npm install playwright' },
            { name: 'jsdom', command: 'npm install jsdom' }
        ];
        
        for (const dep of dependencies) {
            console.log(`   📦 安装 ${dep.name}...`);
            
            try {
                await execAsync(dep.command, { cwd: this.baseDir });
                console.log(`     ✅ ${dep.name} 安装成功`);
            } catch (error) {
                console.warn(`     ⚠️  ${dep.name} 安装失败: ${error.message}`);
                console.warn('     你可以稍后手动安装: npm install ' + dep.name);
            }
        }
        
        console.log('   ✅ 依赖安装完成');
    }
    
    async setupEnvironment() {
        console.log('5. 设置环境...');
        
        // 检查环境变量
        const envVars = {
            TAVILY_API_KEY: 'Tavily搜索API密钥（可选）',
            CDP_URL: '浏览器CDP地址（可选，默认: http://127.0.0.1:9222）',
            TOKEN_BUDGET: 'Token预算限制（可选，默认: 5000）'
        };
        
        console.log('   环境变量检查:');
        for (const [varName, description] of Object.entries(envVars)) {
            if (process.env[varName]) {
                console.log(`     ✅ ${varName}: 已设置`);
            } else {
                console.log(`     ℹ️  ${varName}: 未设置 (${description})`);
            }
        }
        
        // 创建.env.example文件
        const envExample = Object.entries(envVars)
            .map(([key, desc]) => `# ${desc}\n${key}=`)
            .join('\n\n');
        
        const envPath = path.join(this.baseDir, '.env.example');
        fs.writeFileSync(envPath, envExample);
        console.log(`   📄 创建: .env.example`);
        
        console.log('   ✅ 环境设置完成');
    }
    
    async testInstallation() {
        console.log('6. 测试安装...');
        
        const tests = [
            { name: 'Node.js模块', test: () => require('crawlee') },
            { name: 'Playwright', test: () => require('playwright') },
            { name: 'JSDOM', test: () => require('jsdom') },
            { name: '配置文件', test: () => {
                const configPath = path.join(this.configDir, 'config.json');
                return fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : null;
            }},
            { name: '主脚本', test: () => require('./smart-fetch') }
        ];
        
        for (const test of tests) {
            try {
                const result = test.test();
                console.log(`   ✅ ${test.name}: 通过`);
            } catch (error) {
                console.log(`   ❌ ${test.name}: 失败 - ${error.message}`);
            }
        }
        
        console.log('   ✅ 安装测试完成');
    }
    
    showNextSteps() {
        console.log('\n📋 下一步操作:');
        console.log('='.repeat(50));
        console.log('1. 配置环境变量:');
        console.log('   cp .env.example .env');
        console.log('   # 编辑 .env 文件，设置你的API密钥');
        console.log('');
        console.log('2. 编辑配置文件:');
        console.log('   vim config/config.json');
        console.log('   # 根据你的需求调整配置');
        console.log('');
        console.log('3. 测试系统:');
        console.log('   npm test');
        console.log('   # 运行示例测试');
        console.log('');
        console.log('4. 基本使用:');
        console.log('   node scripts/smart-fetch.js https://example.com');
        console.log('   # 获取网页内容');
        console.log('');
        console.log('5. 高级选项:');
        console.log('   node scripts/smart-fetch.js --help');
        console.log('   # 查看所有选项');
        console.log('');
        console.log('6. 在OpenClaw中使用:');
        console.log('   # 设置别名或创建快捷命令');
        console.log('   alias smart-fetch="node /path/to/smart-fetch.js"');
        console.log('');
        console.log('💡 提示:');
        console.log('- 首次使用Crawlee可能需要安装浏览器: npx playwright install');
        console.log('- 查看详细文档: cat SKILL.md');
        console.log('- 报告问题: 查看GitHub Issues');
        console.log('='.repeat(50));
    }
}

// 运行安装脚本
if (require.main === module) {
    const setup = new SetupScript();
    setup.run().catch(error => {
        console.error('安装失败:', error);
        process.exit(1);
    });
}

module.exports = SetupScript;