#!/usr/bin/env python3
"""
Bio-Memory Pro - 主动记忆助手
智能判断何时记录、何时询问、何时沉默
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from smart_snapshot import SmartSnapshotEngine

class ProactiveMemoryAssistant:
    """主动记忆助手 - 让AI更智能地管理记忆"""
    
    def __init__(self, memory_dir: str = None):
        self.engine = SmartSnapshotEngine(memory_dir)
        self.confidence_threshold = {
            'high': 0.8,    # 直接记录，事后提一句
            'medium': 0.5,  # 自然确认
            'low': 0.3,     # 不确定，轻松询问
        }
    
    def calculate_confidence(self, text: str, finding: Dict) -> Tuple[float, str]:
        """
        计算置信度，返回 (score, reason)
        高分：直接记录
        中分：自然确认
        低分：询问用户
        """
        ftype = finding.get('type')
        score = 0.5  # 基础分
        reasons = []
        
        # ========== 新项目检测 ==========
        if ftype == 'new_project':
            # 强信号词
            strong_signals = ['开始', '启动', '创建', '写个', '做个', '搞个']
            if any(s in text for s in strong_signals):
                score += 0.3
                reasons.append('强信号词')
            
            # 明确的时间/计划
            if any(w in text for w in ['明天', '下周', '计划', '准备']):
                score += 0.2
                reasons.append('有时间规划')
            
            # 详细的描述（更可能是认真的）
            if len(text) > 20:
                score += 0.1
                reasons.append('详细描述')
            
            # 降低置信度的情况
            if any(w in text for w in ['可能', '也许', '考虑一下', '？']):
                score -= 0.3
                reasons.append('不确定语气')
        
        # ========== 待办检测 ==========
        elif ftype == 'todo':
            # 明确的时间
            time_words = ['明天', '后天', '下周', '周末', '周一', '周二']
            if any(w in text for w in time_words):
                score += 0.3
                reasons.append('明确时间')
            
            # 具体的动词
            action_words = ['交', '发', '写', '做', '准备', '完成']
            if any(w in finding.get('content', '') for w in action_words):
                score += 0.2
                reasons.append('具体动作')
            
            # 降低置信度
            if any(w in text for w in ['也许', '可能', '如果']):
                score -= 0.2
                reasons.append('条件语气')
        
        # ========== 偏好检测 ==========
        elif ftype == 'preference':
            # 强烈的情感词
            strong_prefs = ['特别喜欢', '非常讨厌', '绝对不要', '必须']
            if any(s in text for s in strong_prefs):
                score += 0.3
                reasons.append('强烈情感')
            
            # 长期的表述
            if any(w in text for w in ['一直', '从来', '总是', '永远']):
                score += 0.2
                reasons.append('长期表述')
            
            # 降低置信度（随口一提）
            if any(w in text for w in ['今天', '这次', '暂时', '现在']):
                score -= 0.3
                reasons.append('可能是临时的')
            
            if '？' in text or '吗' in text:
                score -= 0.4
                reasons.append('疑问语气')
        
        # ========== 决定检测 ==========
        elif ftype == 'decision':
            # 确定性词汇
            sure_words = ['决定', '确定', '说好了', '定了', '就这个']
            if any(w in text for w in sure_words):
                score += 0.3
                reasons.append('确定性表述')
            
            # 最终结果
            if any(w in text for w in ['最终', '最后', '结论']):
                score += 0.2
                reasons.append('最终结果')
        
        # ========== 联系人检测 ==========
        elif ftype == 'contact':
            # 亲密关系（通常是长期有效的）
            close_rel = ['妈', '爸', '老婆', '老公', '孩子', '妹妹', '弟弟']
            if any(r in finding.get('relationship', '') for r in close_rel):
                score += 0.2
                reasons.append('亲密关系')
            
            # 随口一提的判断
            if len(text) < 15 and '。' not in text:
                score -= 0.2
                reasons.append('简短提及')
        
        # 最终分数限制在 0-1
        score = max(0.0, min(1.0, score))
        
        return score, ', '.join(reasons) if reasons else '基础匹配'
    
    def generate_response(self, text: str, finding: Dict, confidence: float) -> Optional[str]:
        """
        根据置信度生成自然的回应
        高分：记录后自然提及
        中分：确认但不问"要不要记"
        低分：轻松询问
        """
        ftype = finding.get('type')
        
        # ===== 高置信度：记录 + 自然提及 =====
        if confidence >= self.confidence_threshold['high']:
            if ftype == 'new_project':
                return f"好嘞！{finding['name']}，我记下了。"
            
            elif ftype == 'todo':
                return f"记下了，{finding['content'][:30]}..."
            
            elif ftype == 'preference':
                return f"收到～"
            
            elif ftype == 'decision':
                return f"行，就这么定了。"
            
            elif ftype == 'contact':
                return f"{finding['name']}是吧，记住了。"
        
        # ===== 中置信度：自然确认 =====
        elif confidence >= self.confidence_threshold['medium']:
            if ftype == 'new_project':
                return f"{finding['name']}？什么时候开始弄？"
            
            elif ftype == 'todo':
                return f"{finding['content'][:20]}... 需要我提醒你吗？"
            
            elif ftype == 'preference':
                return f"哦？{finding['content'][:20]}... 是一直这样还是最近？"
            
            elif ftype == 'decision':
                return f"确定了？不改了？"
        
        # ===== 低置信度：轻松询问 =====
        else:
            if ftype == 'new_project':
                return f"{finding['name']}？认真的还是随口说说？"
            
            elif ftype == 'todo':
                return f"这个需要我记着吗？"
            
            elif ftype == 'preference':
                return f"这是你长期偏好的，还是就这次？"
            
            elif ftype == 'contact':
                return f"{finding['name']}是你亲戚？需要长期记住吗？"
        
        return None
    
    def process_message(self, text: str) -> Dict:
        """
        处理用户消息，返回处理结果
        {
            'action': 'auto_record' | 'confirm' | 'ask' | 'ignore',
            'finding': {...},  # 检测到的信息
            'confidence': 0.8,
            'response': '...',  # 给用户的回应
            'updates': ['...']  # snapshot更新摘要
        }
        """
        # 检测关键信息
        findings = self.engine.analyze_message(text)
        
        if not findings:
            return {'action': 'ignore', 'finding': None}
        
        # 取置信度最高的
        best_finding = None
        best_confidence = 0
        best_reason = ''
        
        for finding in findings:
            conf, reason = self.calculate_confidence(text, finding)
            if conf > best_confidence:
                best_confidence = conf
                best_finding = finding
                best_reason = reason
        
        # 根据置信度决定行动
        if best_confidence >= self.confidence_threshold['high']:
            # 自动记录
            updates = self.engine.update_with_findings([best_finding])
            response = self.generate_response(text, best_finding, best_confidence)
            
            return {
                'action': 'auto_record',
                'finding': best_finding,
                'confidence': best_confidence,
                'reason': best_reason,
                'response': response,
                'updates': updates
            }
        
        elif best_confidence >= self.confidence_threshold['medium']:
            # 自然确认（不自动记录，等用户回应）
            response = self.generate_response(text, best_finding, best_confidence)
            
            return {
                'action': 'confirm',
                'finding': best_finding,
                'confidence': best_confidence,
                'reason': best_reason,
                'response': response,
                'updates': []
            }
        
        else:
            # 询问用户
            response = self.generate_response(text, best_finding, best_confidence)
            
            return {
                'action': 'ask',
                'finding': best_finding,
                'confidence': best_confidence,
                'reason': best_reason,
                'response': response,
                'updates': []
            }
    
    def handle_confirmation(self, user_response: str, pending_finding: Dict) -> bool:
        """
        处理用户的确认/否认回应
        返回是否应该记录
        """
        positive = ['对', '是的', '没错', '记吧', '好', '行', '要']
        negative = ['不用', '别', '不', '算了', '随口', '临时']
        
        # 检查积极回应
        if any(p in user_response for p in positive):
            self.engine.update_with_findings([pending_finding])
            return True
        
        # 检查消极回应
        if any(n in user_response for n in negative):
            return False
        
        # 不确定，默认不记录（避免误记）
        return False


# ========== 快捷函数 ==========

def analyze_message_smart(text: str) -> Dict:
    """智能分析消息，返回处理结果"""
    assistant = ProactiveMemoryAssistant()
    return assistant.process_message(text)


if __name__ == '__main__':
    # 测试用例
    test_cases = [
        # 高置信度
        "我要开始写个新小说，叫《代码觉醒》",
        "明天要交报告，记得提醒我",
        "我特别喜欢科幻题材",
        "决定用第一人称写了",
        "我表妹叫小红",
        
        # 中置信度
        "可能写个小说吧",
        "下周也许要开会",
        "今天喜欢这个游戏",
        
        # 低置信度
        "写个小说？",
        "可能喜欢吧",
        "我表哥... 算了不重要",
    ]
    
    assistant = ProactiveMemoryAssistant()
    
    print("=" * 60)
    print("Bio-Memory Pro - 主动记忆助手测试")
    print("=" * 60)
    
    for text in test_cases:
        result = assistant.process_message(text)
        print(f"\n📝 用户: {text}")
        print(f"   动作: {result['action']}")
        print(f"   置信度: {result.get('confidence', 0):.2f}")
        print(f"   原因: {result.get('reason', 'N/A')}")
        if result.get('response'):
            print(f"   AI回应: {result['response']}")
        if result.get('updates'):
            print(f"   更新: {result['updates']}")
