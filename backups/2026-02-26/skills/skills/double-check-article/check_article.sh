#!/bin/bash
# 中文文章检查脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 常见错别字库
TYPO_DICT=(
  "的得地:的用于形容词，得用于补语，地用于状语"
  "在再:在表示位置，再表示重复"
  "做作:做表示动作，作表示作品或作为"
  "象像:象表示大象或形象，像表示相似"
  "那哪:那表示远指，哪表示疑问"
  "他她它:他男性，她女性，它动物或事物"
  "已以:已表示已经，以表示用或按照"
  "即既:即表示就是，既表示已经"
  "须需:须表示必须，需表示需要"
  "至致:至表示到，致表示导致"
)

# 检查函数
check_article() {
    local article="$1"
    local filename="$2"
    
    echo -e "${BLUE}📊 文章检查开始${NC}"
    echo "================================"
    
    # 基本信息统计
    local char_count=$(echo "$article" | wc -m)
    local line_count=$(echo "$article" | wc -l)
    local word_count=$(echo "$article" | wc -w)
    
    echo -e "${GREEN}📈 基本信息：${NC}"
    echo "- 字符数: $char_count"
    echo "- 行数: $line_count"
    echo "- 词数: $word_count"
    echo ""
    
    # 检查常见错别字
    echo -e "${YELLOW}🔍 错别字检查：${NC}"
    local found_typos=0
    for typo_pair in "${TYPO_DICT[@]}"; do
        local typo=$(echo "$typo_pair" | cut -d':' -f1)
        local explanation=$(echo "$typo_pair" | cut -d':' -f2)
        
        # 检查每个可能的错别字
        for ((i=0; i<${#typo}; i++)); do
            local char="${typo:$i:1}"
            if echo "$article" | grep -q "$char"; then
                echo -e "  - 注意 '$char': $explanation"
                found_typos=1
            fi
        done
    done
    
    if [ $found_typos -eq 0 ]; then
        echo -e "  ${GREEN}✅ 未发现常见错别字${NC}"
    fi
    echo ""
    
    # 检查标点符号
    echo -e "${YELLOW}🔤 标点符号检查：${NC}"
    local punctuation_errors=0
    
    # 检查连续标点
    if echo "$article" | grep -q "[，。！？；：][，。！？；：]"; then
        echo -e "  ${RED}⚠️ 发现连续标点符号${NC}"
        punctuation_errors=1
    fi
    
    # 检查缺少标点
    local long_lines=$(echo "$article" | awk 'length($0) > 50 && $0 !~ /[。！？]$/')
    if [ -n "$long_lines" ]; then
        echo -e "  ${YELLOW}📏 发现长句可能缺少结束标点${NC}"
        punctuation_errors=1
    fi
    
    if [ $punctuation_errors -eq 0 ]; then
        echo -e "  ${GREEN}✅ 标点符号使用基本规范${NC}"
    fi
    echo ""
    
    # 检查表达清晰度
    echo -e "${YELLOW}💬 表达清晰度检查：${NC}"
    
    # 检查过长句子
    local long_sentences=$(echo "$article" | tr '。！？' '\n' | awk 'length($0) > 50')
    if [ -n "$long_sentences" ]; then
        echo -e "  ${YELLOW}📏 发现长句，建议拆分：${NC}"
        echo "$long_sentences" | head -3 | while read sentence; do
            echo "    - \"$sentence\""
        done
    else
        echo -e "  ${GREEN}✅ 句子长度适中${NC}"
    fi
    
    # 检查重复词汇
    local common_words=("的" "了" "在" "是" "和" "有")
    for word in "${common_words[@]}"; do
        local count=$(echo "$article" | grep -o "$word" | wc -l)
        local total_words=$(echo "$article" | wc -w)
        local percentage=$((count * 100 / total_words))
        
        if [ $percentage -gt 5 ]; then
            echo -e "  ${YELLOW}🔄 \"$word\" 使用频率较高 ($percentage%)${NC}"
        fi
    done
    echo ""
    
    # 整体评估
    echo -e "${BLUE}🎯 整体评估：${NC}"
    
    local score=10
    
    # 扣分规则
    if [ $found_typos -eq 1 ]; then
        score=$((score - 2))
    fi
    
    if [ $punctuation_errors -eq 1 ]; then
        score=$((score - 1))
    fi
    
    if [ -n "$long_sentences" ]; then
        score=$((score - 1))
    fi
    
    # 确保分数在1-10之间
    if [ $score -lt 1 ]; then
        score=1
    fi
    
    echo -e "  文章质量评分: ${GREEN}$score/10${NC}"
    
    # 给出建议
    echo ""
    echo -e "${BLUE}💡 改进建议：${NC}"
    if [ $score -ge 8 ]; then
        echo "  ✅ 文章质量很好，继续保持！"
    elif [ $score -ge 6 ]; then
        echo "  📝 文章质量中等，建议："
        echo "    - 检查可能存在的错别字"
        echo "    - 优化过长的句子"
        echo "    - 注意标点符号使用"
    else
        echo "  ⚠️ 文章需要较大改进，建议："
        echo "    - 仔细检查错别字"
        echo "    - 重新组织句子结构"
        echo "    - 请他人帮忙校对"
    fi
    
    echo ""
    echo "================================"
    echo -e "${BLUE}✅ 检查完成${NC}"
}

# 主程序
main() {
    if [ $# -eq 0 ]; then
        echo -e "${RED}错误：请提供文章内容或文件路径${NC}"
        echo "使用方法："
        echo "  $0 \"文章内容\""
        echo "  $0 -f 文件名"
        exit 1
    fi
    
    local article=""
    local filename=""
    
    if [ "$1" = "-f" ] && [ $# -eq 2 ]; then
        filename="$2"
        if [ ! -f "$filename" ]; then
            echo -e "${RED}错误：文件不存在 '$filename'${NC}"
            exit 1
        fi
        article=$(cat "$filename")
    else
        article="$*"
        filename="直接输入"
    fi
    
    check_article "$article" "$filename"
}

# 运行主程序
main "$@"