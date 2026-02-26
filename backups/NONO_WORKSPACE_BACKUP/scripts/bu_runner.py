import asyncio
import sys

# 修复 Pydantic 在 Python 3.14+ 上的警告/错误
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from browser_use import Agent, Browser
from langchain_openai import ChatOpenAI

async def run_task(task_str):
    # 配置中转站大脑
    llm = ChatOpenAI(
        model="custom/gemini-3-flash-preview", 
        openai_api_key="sk-592vE7E0F2h1f0I5D2X1H7e0C0C8I5B1B2A1C0D2F4I5lIJxps",
        base_url="https://api.vllm.icu/v1"
    )

    # 核心：使用 Browser 类，不依赖 CLI 包装器
    browser = Browser()
    
    agent = Agent(
        task=task_str,
        llm=llm,
        browser=browser
    )

    try:
        await agent.run()
    finally:
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        task = "打开 https://www.baidu.com 并搜索 OpenClaw"
    
    # 修复 Python 3.14 异步循环问题
    asyncio.run(run_task(task))
