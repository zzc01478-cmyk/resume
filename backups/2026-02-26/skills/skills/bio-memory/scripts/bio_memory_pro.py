#!/usr/bin/env python3
"""
Bio-Memory Pro - 集成版
整合智能检测 + 主动记忆 + 话题管理
"""

import sys
sys.path.insert(0, str(Path(__file__).parent))

from smart_snapshot_v2_1 import SmartSnapshotEngine
from proactive_memory import ProactiveMemoryAssistant
from topic_manager import TopicManager, detect_topic_switch
from pathlib import Path
from typing import Dict, List, Optional

class BioMemoryPro:
    """Bio-Memory Pro 完整版 - 智能记忆 + 话题管理"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            self.memory_dir = Path.home() / '.openclaw' / 'workspace' / 'memory'
        else:
            self.memory_dir = Path(memory_dir)
        
        # 初始化各个模块
        self.topic_manager = TopicManager(self.memory_dir)
        self.snapshot_engine = SmartSnapshotEngine(self.memory_dir)
        self.proactive_assistant = ProactiveMemoryAssistant(self.memory_dir)
    
    def process_message(self, text: str, user_id: str = 'default') -> Dict:
        """
        处理用户消息，完整流程：
        1. 检测话题切换
        2. 检测关键信息
        3. 置信度判断
        4. 更新记忆
        5. 生成回应
        """
        result = {
            'action': 'continue',
            'topic_switched': False,
            'topic_name': None,
            'findings': [],
            'updates': [],
            'response': None,
            'confidence': 0,
        }
        
        # ========== 步骤1: 检测话题切换 ==========
        topic_hint = detect_topic_switch(text)
        
        if topic_hint:
            # 切换话题
            old_topic = self.topic_manager.get_current_topic()
            new_topic = self.topic_manager.switch_topic(topic_hint)
            
            result['topic_switched'] = True
            result['topic_name'] = new_topic['name']
            result['action'] = 'topic_switch'
            
            # 生成话题切换回应
            if old_topic and old_topic['name'] != new_topic['name']:
                if new_topic['message_count'] > 0:
                    # 恢复历史话题
                    summary = new_topic.get('summary', '') or new_topic.get('last_message', '')[:50]
                    result['response'] = f"好，回到{new_topic['name']}。之前聊到{summary}..."
                else:
                    # 新话题
                    result['response'] = f"好啊！{new_topic['name']}～具体想聊什么？"
            else:
                result['response'] = f"切换到{new_topic['name']}，想聊哪方面？"
            
            # 更新话题信息
            self.topic_manager.update_topic(text)
            
            return result
        
        # ========== 步骤2: 在当前话题内处理 ==========
        
        # 检测关键信息
        findings = self.snapshot_engine.analyze_message(text)
        result['findings'] = findings
        
        # 置信度判断和处理
        if findings:
            # 取置信度最高的
            best = self.proactive_assistant.process_message(text)
            result['confidence'] = best.get('confidence', 0)
            result['action'] = best.get('action', 'ignore')
            
            # 自动记录高置信度信息
            if best['action'] == 'auto_record':
                for finding in findings:
                    self.topic_manager.update_topic(text, finding)
                result['updates'] = best.get('updates', [])
            
            result['response'] = best.get('response')
        else:
            # 无关键信息，正常对话
            self.topic_manager.update_topic(text)
        
        return result
    
    def get_status(self) -> str:
        """获取当前状态摘要"""
        topic = self.topic_manager.get_current_topic()
        if not topic:
            return "暂无活跃话题"
        
        lines = [
            f"🔥 当前话题: {topic['name']}",
            f"   消息数: {topic['message_count']}",
        ]
        
        snapshot = topic.get('snapshot', {})
        projects = snapshot.get('active_projects', [])
        if projects:
            lines.append(f"   项目: {', '.join(p['name'] for p in projects)}")
        
        todos = [t for t in snapshot.get('todos', []) if not t.get('done')]
        if todos:
            lines.append(f"   待办: {len(todos)}个")
        
        # 列出其他话题
        all_topics = self.topic_manager.list_all_topics()
        paused = [t for t in all_topics if not t.get('is_current', False)]
        if paused:
            lines.append(f"\n⏸️ 其他话题 ({len(paused)}个):")
            for t in paused[:3]:
                lines.append(f"   - {t['name']}")
        
        return '\n'.join(lines)
    
    def switch_topic(self, name: str) -> Dict:
        """手动切换话题"""
        return self.topic_manager.switch_topic(name)
    
    def list_topics(self) -> List[Dict]:
        """列出所有话题"""
        return self.topic_manager.list_all_topics()


# ========== 快捷使用 ==========

_bio_memory = None

def get_bio_memory() -> BioMemoryPro:
    """获取单例实例"""
    global _bio_memory
    if _bio_memory is None:
        _bio_memory = BioMemoryPro()
    return _bio_memory

def smart_reply(text: str) -> str:
    """智能回复 - 集成话题切换和记忆"""
    bio = get_bio_memory()
    result = bio.process_message(text)
    
    if result.get('response'):
        return result['response']
    
    # 如果没有特定回应，返回空（让上层处理）
    return ""


if __name__ == '__main__':
    print("=" * 50)
    print("Bio-Memory Pro v2.1 - 完整版测试")
    print("=" * 50)
    
    bio = BioMemoryPro()
    
    # 测试对话
    test_conversation = [
        # 话题1: 小说
        "我要开始写个新小说，叫《星际穿越》",
        "记得明天要交大纲",
        
        # 切换话题
        "我们换个话题，聊聊旅游计划",
        "我想去云南",
        
        # 回到之前的话题
        "回到刚才的小说",
        "决定用第三人称写",
    ]
    
    for msg in test_conversation:
        print(f"\n👤 用户: {msg}")
        result = bio.process_message(msg)
        
        if result.get('topic_switched'):
            print(f"🔄 [话题切换] -> {result['topic_name']}")
        
        if result.get('response'):
            print(f"🤖 AI: {result['response']}")
        
        if result.get('findings'):
            for f in result['findings']:
                print(f"   📌 检测到: {f['type']}")
    
    print("\n" + "=" * 50)
    print("最终状态:")
    print(bio.get_status())
