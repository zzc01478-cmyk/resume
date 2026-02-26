#!/usr/bin/env python3
"""
Bio-Memory Pro - 话题管理器 (Topic Manager)
管理多个对话线程，支持话题切换
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
import hashlib

class TopicManager:
    """话题管理器 - 像聊天软件一样管理多个对话"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            self.memory_dir = Path.home() / '.openclaw' / 'workspace' / 'memory'
        else:
            self.memory_dir = Path(memory_dir)
        
        self.topics_dir = self.memory_dir / 'topics'
        self.active_dir = self.topics_dir / 'active'
        self.paused_dir = self.topics_dir / 'paused'
        
        # 确保目录存在
        for d in [self.active_dir, self.paused_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 初始化当前话题
        self._ensure_topic_exists()
    
    def _ensure_topic_exists(self):
        """确保有当前话题"""
        if not self.get_current_topic():
            self._create_topic("默认话题")
    
    def _topic_id(self, name: str) -> str:
        """生成话题ID"""
        date = datetime.now().strftime('%Y%m%d')
        slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', name.lower())[:20]
        return f"{date}-{slug}"
    
    def _hash(self, text: str) -> str:
        """生成哈希"""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()[:10]
    
    def get_current_topic(self) -> Optional[Dict]:
        """获取当前活跃话题"""
        current_file = self.active_dir / 'current.json'
        if current_file.exists():
            try:
                return json.loads(current_file.read_text(encoding='utf-8'))
            except:
                return None
        return None
    
    def _create_topic(self, name: str, summary: str = "") -> Dict:
        """创建新话题"""
        topic = {
            'topic_id': self._topic_id(name),
            'name': name,
            'summary': summary,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_message': '',
            'message_count': 0,
            'keywords': self._extract_keywords(name),
            'snapshot': {
                'active_projects': [],
                'todos': [],
                'key_facts': [],
            }
        }
        self._save_topic(topic)
        return topic
    
    def _save_topic(self, topic: Dict):
        """保存话题"""
        current_file = self.active_dir / 'current.json'
        current_file.write_text(
            json.dumps(topic, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def _pause_current_topic(self):
        """暂停当前话题"""
        current = self.get_current_topic()
        if not current:
            return
        
        current['status'] = 'paused'
        current['updated_at'] = datetime.now().isoformat()
        
        # 保存到 paused/
        paused_file = self.paused_dir / f"{current['topic_id']}.json"
        paused_file.write_text(
            json.dumps(current, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        # 删除 current
        current_file = self.active_dir / 'current.json'
        if current_file.exists():
            current_file.unlink()
    
    def switch_topic(self, name: str) -> Dict:
        """
        切换话题
        - 如果有同名历史话题，恢复它
        - 否则创建新话题
        """
        # 1. 保存当前话题
        self._pause_current_topic()
        
        # 2. 查找历史话题
        existing = self._find_topic_by_name(name)
        
        if existing:
            # 恢复历史话题
            existing['status'] = 'active'
            existing['updated_at'] = datetime.now().isoformat()
            self._save_topic(existing)
            return existing
        else:
            # 创建新话题
            return self._create_topic(name)
    
    def _find_topic_by_name(self, name: str) -> Optional[Dict]:
        """根据名称查找历史话题"""
        name_hash = self._hash(name)
        
        # 搜索 paused/ 目录
        for topic_file in self.paused_dir.glob('*.json'):
            try:
                topic = json.loads(topic_file.read_text(encoding='utf-8'))
                # 检查名称相似度
                if self._hash(topic.get('name', '')) == name_hash:
                    return topic
                # 检查关键词匹配
                if any(self._hash(k) == name_hash for k in topic.get('keywords', [])):
                    return topic
            except:
                continue
        
        return None
    
    def update_topic(self, message: str, finding: Dict = None):
        """更新当前话题信息"""
        topic = self.get_current_topic()
        if not topic:
            topic = self._create_topic("新话题")
        
        topic['message_count'] += 1
        topic['updated_at'] = datetime.now().isoformat()
        topic['last_message'] = message[:80]
        
        # 更新关键词
        new_keywords = self._extract_keywords(message)
        topic['keywords'] = list(set(topic.get('keywords', []) + new_keywords))[:8]
        
        # 如果有发现，更新 snapshot
        if finding:
            self._update_topic_snapshot(topic, finding)
        
        self._save_topic(topic)
    
    def _update_topic_snapshot(self, topic: Dict, finding: Dict):
        """更新话题内的 snapshot"""
        snapshot = topic.get('snapshot', {})
        ftype = finding.get('type')
        
        if ftype == 'new_project':
            projects = snapshot.get('active_projects', [])
            if not any(p.get('name') == finding['name'] for p in projects):
                projects.append({
                    'name': finding['name'],
                    'status': '进行中'
                })
                snapshot['active_projects'] = projects[-5:]  # 保留最近5个
        
        elif ftype == 'todo':
            todos = snapshot.get('todos', [])
            content = finding.get('content', '')
            if not any(t.get('content') == content for t in todos):
                todos.append({
                    'content': content,
                    'done': False
                })
                snapshot['todos'] = todos[-8:]  # 保留最近8个
        
        elif ftype == 'preference' or ftype == 'decision':
            facts = snapshot.get('key_facts', [])
            content = finding.get('content', '')
            if content not in facts:
                facts.append(content)
                snapshot['key_facts'] = facts[-10:]  # 保留最近10个
        
        topic['snapshot'] = snapshot
    
    def get_topic_summary(self) -> str:
        """获取当前话题摘要"""
        topic = self.get_current_topic()
        if not topic:
            return "暂无话题"
        
        snapshot = topic.get('snapshot', {})
        lines = [f"当前话题: {topic['name']}"]
        
        projects = snapshot.get('active_projects', [])
        if projects:
            lines.append(f"项目: {', '.join(p['name'] for p in projects)}")
        
        todos = [t for t in snapshot.get('todos', []) if not t.get('done')]
        if todos:
            lines.append(f"待办: {len(todos)}个")
        
        return '\n'.join(lines)
    
    def list_all_topics(self) -> List[Dict]:
        """列出所有话题"""
        topics = []
        
        # 当前话题
        current = self.get_current_topic()
        if current:
            topics.append({
                **current,
                'status_icon': '🔥',
                'is_current': True
            })
        
        # 暂停的话题
        for topic_file in self.paused_dir.glob('*.json'):
            try:
                topic = json.loads(topic_file.read_text(encoding='utf-8'))
                topics.append({
                    **topic,
                    'status_icon': '⏸️',
                    'is_current': False
                })
            except:
                continue
        
        # 按更新时间排序
        topics.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return topics
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取2-8字的中文词
        words = re.findall(r'[\u4e00-\u9fff]{2,8}', text)
        return list(set(words))[:5]
    
    def delete_topic(self, topic_id: str):
        """删除话题"""
        # 从 paused/ 删除
        paused_file = self.paused_dir / f"{topic_id}.json"
        if paused_file.exists():
            paused_file.unlink()


def detect_topic_switch(text: str) -> Optional[str]:
    """
    检测用户是否要切换话题
    返回话题名称提示，或 None
    """
    # 明确切换指令
    patterns = [
        r'(?:换个|切换|转|聊)(?:个|一下)?(?:话题|主题|事情)(?:[，,]?聊?\s*)(.+?)(?:[。！]|$)',
        r'(?:说|聊)(?:点|一下)?别的(?:[，,]?(?:关于|聊聊)?)(.+?)?(?:[。！]|$)',
        r'(?:回到|继续)(?:之前|刚才|上次)(?:的|那个)?(.+?)(?:话题|讨论)?(?:[。！]|$)',
        r'(?:我们来|开始|聊聊)(?:讨论|聊|说)?(.+?)(?:吧|怎么样)?[。！]?$',
        r'(?:话题|关于)(?:[：:]\s*)(.+?)(?:[。！]|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            topic_hint = match.group(1).strip() if match.groups() else None
            if topic_hint and len(topic_hint) > 1:
                return topic_hint
            return "新话题"
    
    return None


# ========== 快捷函数 ==========

def switch_to_topic(name: str, memory_dir: str = None) -> Dict:
    """快捷切换话题"""
    manager = TopicManager(memory_dir)
    return manager.switch_topic(name)

def get_current_topic_info(memory_dir: str = None) -> str:
    """获取当前话题信息"""
    manager = TopicManager(memory_dir)
    return manager.get_topic_summary()


if __name__ == '__main__':
    # 测试
    print("测试 Topic Manager\n")
    
    manager = TopicManager()
    
    # 测试话题切换检测
    test_inputs = [
        "我们换个话题，聊聊旅游",
        "回到刚才的小说",
        "聊点别的",
        "开始讨论新功能",
        "话题：AI发展",
    ]
    
    for text in test_inputs:
        topic = detect_topic_switch(text)
        print(f"'{text}' -> 话题: {topic}")
    
    print("\n当前话题列表:")
    for t in manager.list_all_topics():
        print(f"  {t['status_icon']} {t['name']} ({t['message_count']}条)")
