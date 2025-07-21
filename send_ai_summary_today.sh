#!/bin/bash

source venv/bin/activate

# ==============================================================================
# 微信AI总结工作流脚本
# 功能：获取多个群的聊天记录，用AI分析后发送结果到指定群
# ==============================================================================

# 配置变量
declare -a group_source_ids=(
    "27587714869@chatroom"
    "43543695744@chatroom"
    # "56984901177@chatroom"  # 可以添加更多群ID
)

group_send_id="56984901177@chatroom"
input_prompt="ai_prompt.md"
ignore_user="bushcraftsecret"  # 要忽略的用户微信ID，为空则不过滤任何用户

# 时间和文件名配置
hours=1  # 获取最近30小时的聊天记录
date_str=$(date '+%Y%m%d_%H%M%S')
today_str=$(date '+%Y%m%d')

# 输出文件配置
log_files=()
output_file="ai_summary_${today_str}.md"

# 调试信息开关
DEBUG=true

# ==============================================================================
# 调试信息输出函数
# ==============================================================================
debug_echo() {
    if [ "$DEBUG" = true ]; then
        echo "[DEBUG $(date '+%H:%M:%S')] $1"
    fi
}

info_echo() {
    echo "[INFO $(date '+%H:%M:%S')] $1"
}

error_echo() {
    echo "[ERROR $(date '+%H:%M:%S')] $1" >&2
}

# ==============================================================================
# 检查必要文件和工具
# ==============================================================================
check_prerequisites() {
    info_echo "检查运行环境..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        error_echo "python3 未找到，请先安装Python3"
        exit 1
    fi
    
    # 检查必要的脚本文件
    local scripts=("getrecentchatlogs.py" "analyze_logs.py" "post_wechat.py")
    for script in "${scripts[@]}"; do
        if [ ! -f "$script" ]; then
            error_echo "脚本文件 $script 不存在"
            exit 1
        fi
    done
    
    # 检查输入prompt文件
    if [ ! -f "$input_prompt" ]; then
        error_echo "输入prompt文件 $input_prompt 不存在"
        exit 1
    fi
    
    # 检查配置文件
    if [ ! -f "config.yml" ]; then
        error_echo "配置文件 config.yml 不存在"
        exit 1
    fi
    
    if [ ! -f "mcp.json" ]; then
        error_echo "配置文件 mcp.json 不存在"
        exit 1
    fi
    
    info_echo "环境检查完成"
}

# ==============================================================================
# 步骤1: 获取各群聊天记录
# ==============================================================================
fetch_chat_logs() {
    info_echo "开始获取聊天记录..."
    
    for group_id in "${group_source_ids[@]}"; do
        debug_echo "处理群ID: $group_id"
        
        # 生成输出文件名
        clean_id=$(echo "$group_id" | sed 's/@/_/g' | sed 's/:/_/g')
        log_file="${clean_id}_chatlog_${today_str}.md"
        
        debug_echo "输出文件: $log_file"
        
        # 调用 getrecentchatlogs.py
        info_echo "获取群 $group_id 最近 $hours 小时的聊天记录..."
        
        # 构建命令，根据ignore_user参数决定是否添加--nouser
        local get_logs_cmd="python3 getrecentchatlogs.py -wid \"$group_id\" -o \"$log_file\" -t $hours --verbose"
        if [ -n "$ignore_user" ]; then
            get_logs_cmd+=" --nouser \"$ignore_user\""
            debug_echo "忽略用户: $ignore_user"
        fi
        
        debug_echo "执行命令: $get_logs_cmd"
        
        if eval "$get_logs_cmd"; then
            if [ -f "$log_file" ]; then
                log_files+=("$log_file")
                info_echo "成功获取 $group_id 的聊天记录: $log_file"
            else
                error_echo "文件 $log_file 未生成"
            fi
        else
            error_echo "获取群 $group_id 的聊天记录失败"
        fi
    done
    
    if [ ${#log_files[@]} -eq 0 ]; then
        error_echo "没有成功获取任何聊天记录文件"
        exit 1
    fi
    
    info_echo "聊天记录获取完成，共获得 ${#log_files[@]} 个文件"
}

# ==============================================================================
# 检查输出文件是否有效
# ==============================================================================
check_output_file() {
    local file="$1"
    
    # 检查文件是否存在
    if [ ! -f "$file" ]; then
        debug_echo "输出文件 $file 不存在"
        return 1
    fi
    
    # 检查文件是否为空
    if [ ! -s "$file" ]; then
        debug_echo "输出文件 $file 为空"
        return 1
    fi
    
    debug_echo "输出文件 $file 有效"
    return 0
}

# ==============================================================================
# 步骤2: AI分析聊天记录（带重试机制）
# ==============================================================================
analyze_logs() {
    info_echo "开始AI分析聊天记录..."
    
    local max_retries=2
    local attempt=1
    
    while [ $attempt -le $((max_retries + 1)) ]; do
        info_echo "AI分析尝试 $attempt/$((max_retries + 1))"
        
        # 如果不是第一次尝试，先删除可能存在的空文件
        if [ $attempt -gt 1 ] && [ -f "$output_file" ]; then
            rm -f "$output_file"
            debug_echo "删除之前的输出文件"
        fi
        
        # 构建analyze_logs.py的参数
        local analyze_cmd="python3 analyze_logs.py -p \"$input_prompt\" -o \"$output_file\""
        
        # 添加所有日志文件作为单个-i参数的输入
        if [ ${#log_files[@]} -gt 0 ]; then
            analyze_cmd+=" -i"
            for log_file in "${log_files[@]}"; do
                analyze_cmd+=" \"$log_file\""
            done
        fi
        
        debug_echo "执行命令: $analyze_cmd"
        
        # 执行分析
        if eval "$analyze_cmd"; then
            # 检查输出文件是否有效
            if check_output_file "$output_file"; then
                info_echo "AI分析完成，结果保存到: $output_file"
                
                # 显示输出文件信息
                local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null || echo "未知")
                debug_echo "输出文件大小: $file_size 字节"
                
                return 0
            else
                error_echo "分析完成但输出文件无效或为空"
            fi
        else
            error_echo "AI分析命令执行失败"
        fi
        
        # 如果不是最后一次尝试，等待一下再重试
        if [ $attempt -lt $((max_retries + 1)) ]; then
            info_echo "等待5秒后重试..."
            sleep 5
        fi
        
        attempt=$((attempt + 1))
    done
    
    error_echo "AI分析在 $((max_retries + 1)) 次尝试后仍然失败"
    return 1
}

# ==============================================================================
# 步骤3: 发送分析结果到微信群
# ==============================================================================
send_to_wechat() {
    info_echo "开始发送分析结果到微信群..."
    
    debug_echo "目标群ID: $group_send_id"
    debug_echo "发送文件: $output_file"
    
    # 检查输出文件是否存在
    if [ ! -f "$output_file" ]; then
        error_echo "输出文件 $output_file 不存在，取消发送"
        return 1
    fi
    
    # 检查输出文件是否为空
    if [ ! -s "$output_file" ]; then
        error_echo "输出文件 $output_file 为空，取消发送"
        return 1
    fi
    
    # 调用 post_wechat.py
    if python3 post_wechat.py -i "$output_file" -wid "$group_send_id"; then
        info_echo "AI分析结果已成功发送到群 $group_send_id"
        return 0
    else
        error_echo "发送到微信群失败"
        return 1
    fi
}

# ==============================================================================
# 清理临时文件
# ==============================================================================
cleanup() {
    if [ "$DEBUG" = false ]; then
        info_echo "清理临时文件..."
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                rm -f "$log_file"
                debug_echo "删除临时文件: $log_file"
            fi
        done
    else
        info_echo "调试模式，保留临时文件"
    fi
}

# ==============================================================================
# 主函数
# ==============================================================================
main() {
    info_echo "开始执行微信AI总结工作流"
    info_echo "========================================"
    
    # 显示配置信息
    info_echo "配置信息:"
    info_echo "  源群组数量: ${#group_source_ids[@]}"
    for i in "${!group_source_ids[@]}"; do
        info_echo "    [$((i+1))] ${group_source_ids[i]}"
    done
    info_echo "  目标群组: $group_send_id"
    info_echo "  输入prompt: $input_prompt"
    info_echo "  时间范围: 最近 $hours 小时"
    if [ -n "$ignore_user" ]; then
        info_echo "  忽略用户: $ignore_user"
    else
        info_echo "  忽略用户: 无"
    fi
    info_echo "  输出文件: $output_file"
    info_echo "========================================"
    
    # 步骤执行
    check_prerequisites
    
    fetch_chat_logs
    
    if analyze_logs; then
        if send_to_wechat; then
            info_echo "工作流执行成功完成！"
            cleanup
            exit 0
        else
            error_echo "发送步骤失败"
            exit 1
        fi
    else
        error_echo "分析步骤失败"
        exit 1
    fi
}

# ==============================================================================
# 错误处理
# ==============================================================================
handle_error() {
    error_echo "脚本执行过程中发生错误 (退出码: $1)"
    error_echo "错误发生在第 $2 行"
    cleanup
    exit 1
}

# 设置错误处理
trap 'handle_error $? $LINENO' ERR

# ==============================================================================
# 脚本入口
# ==============================================================================
# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "微信AI总结工作流脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示此帮助信息"
    echo "  --no-debug     关闭调试信息"
    echo ""
    echo "功能:"
    echo "  1. 从多个微信群获取聊天记录"
    echo "  2. 使用AI分析聊天记录"
    echo "  3. 将分析结果发送到指定微信群"
    echo ""
    echo "配置:"
    echo "  - 编辑脚本开头的 group_source_ids 数组来设置源群组"
    echo "  - 编辑 group_send_id 来设置目标群组"
    echo "  - 编辑 input_prompt 来设置AI分析的prompt文件"
    echo "  - 编辑 ignore_user 来设置要忽略的用户微信ID (留空则不过滤)"
    exit 0
fi

if [ "$1" = "--no-debug" ]; then
    DEBUG=false
fi

# 执行主函数
main