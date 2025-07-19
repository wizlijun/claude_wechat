#!/usr/bin/env python3
"""
获取微信群聊近期聊天记录脚本
Usage: python getrecentchatlogs.py -wid wechatid -o output.md -t 24
"""

import argparse
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Optional
import aiohttp


class WeChatLogClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        
    async def get_chatlog_by_time(self, wechat_id: str, start_time: datetime, end_time: datetime) -> str:
        """根据时间范围获取微信群聊记录"""
        try:
            async with aiohttp.ClientSession() as session:
                # 调试输出时间信息
                print(f"调试信息:")
                print(f"  开始时间: {start_time} (timestamp: {int(start_time.timestamp())})")
                print(f"  结束时间: {end_time} (timestamp: {int(end_time.timestamp())})")
                
                # 构建查询参数 (使用正确的MCP API参数格式)
                chatlog_url = self.server_url.replace('/sse', '/api/v1/chatlog')
                # 格式化时间范围为API要求的格式: "2025-07-15/22:31~2025-07-16/22:31"
                start_time_str = start_time.strftime("%Y-%m-%d/%H:%M")
                end_time_str = end_time.strftime("%Y-%m-%d/%H:%M")
                time_range = f"{start_time_str}~{end_time_str}"
                
                params = {
                    'talker': wechat_id,  # MCP API要求使用talker参数
                    'time': time_range  # 使用时间范围格式
                }
                
                print(f"  API URL: {chatlog_url}")
                print(f"  查询参数: {params}")
                
                async with session.get(chatlog_url, params=params) as response:
                    if response.status == 200:
                        chat_data = await response.text(encoding='utf-8', errors='ignore')
                        return chat_data
                    else:
                        error_text = await response.text()
                        return f"获取聊天记录失败: HTTP {response.status}\n错误信息: {error_text}"
                        
        except Exception as e:
            return f"请求处理错误: {e}"


def calculate_time_range(hours: int) -> tuple[datetime, datetime]:
    """计算时间范围：当前时间和指定小时前的时间"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    return start_time, end_time


def generate_output_filename(wechat_id: str, output_dir: str, current_time: datetime) -> str:
    """生成输出文件名: wechatid_chatlog_YYYYMMDD.md"""
    date_str = current_time.strftime('%Y%m%d')
    # 清理wechat_id中的特殊字符
    clean_wid = wechat_id.replace('@', '_').replace(':', '_')
    filename = f"{clean_wid}_chatlog_{date_str}.md"
    return os.path.join(output_dir, filename)


def filter_chatlog_data(chatlog_data: str, nouser: str) -> str:
    """过滤聊天记录，跳过指定用户的消息"""
    if not nouser:
        return chatlog_data
    
    lines = chatlog_data.split('\n')
    filtered_lines = []
    
    for line in lines:
        # 简单的过滤逻辑：如果行中包含指定的用户ID，则跳过该行
        if nouser not in line:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def format_chatlog_output(wechat_id: str, start_time: datetime, end_time: datetime, 
                         chatlog_data: str, hours: int) -> str:
    """格式化聊天记录输出"""
    header = f"""# 微信群聊记录

**群聊ID**: {wechat_id}
**查询时间范围**: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**时间跨度**: 近{hours}小时
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 聊天记录

"""
    return header + chatlog_data


async def main():
    parser = argparse.ArgumentParser(
        description='获取微信群聊近期聊天记录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python getrecentchatlogs.py -wid 27587714869@chatroom -o ./logs -t 24
  python getrecentchatlogs.py -wid 43543695744@chatroom -o output.md -t 48
        """
    )
    
    parser.add_argument(
        '-wid', '--wechat-id',
        required=True,
        help='微信群聊ID (如: 27587714869@chatroom)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='',
        help='输出文件路径或目录 (默认: 自动生成文件名)'
    )
    
    parser.add_argument(
        '-t', '--hours',
        type=int,
        default=24,
        help='获取近多少小时的聊天记录 (默认: 24)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息'
    )
    
    parser.add_argument(
        '--nouser',
        default='',
        help='要跳过的用户微信ID (默认: 不跳过任何用户)'
    )
    
    args = parser.parse_args()
    
    # 读取MCP配置
    try:
        with open('mcp.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        server_url = config['mcpServers']['chatlog']['url']
        if args.verbose:
            print(f"连接到MCP服务器: {server_url}")
        
    except FileNotFoundError:
        print("错误: 找不到 mcp.json 配置文件")
        sys.exit(1)
    except KeyError as e:
        print(f"错误: mcp.json 配置缺少必要字段 {e}")
        sys.exit(1)
    
    # 1. 计算时间范围
    start_time, end_time = calculate_time_range(args.hours)
    
    if args.verbose:
        print(f"查询时间范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"时间跨度: 近{args.hours}小时")
    
    # 2. 初始化客户端并获取聊天记录
    client = WeChatLogClient(server_url)
    
    try:
        print(f"正在获取群聊 {args.wechat_id} 的聊天记录...")
        chatlog_data = await client.get_chatlog_by_time(args.wechat_id, start_time, end_time)
        
        if args.verbose:
            print(f"获取到聊天记录 ({len(chatlog_data)} 字符)")
    
    except Exception as e:
        print(f"获取聊天记录失败: {e}")
        sys.exit(1)
    
    # 3. 过滤聊天记录
    if args.nouser:
        if args.verbose:
            print(f"过滤用户: {args.nouser}")
        chatlog_data = filter_chatlog_data(chatlog_data, args.nouser)
    
    # 4. 格式化输出内容
    formatted_output = format_chatlog_output(
        args.wechat_id, start_time, end_time, chatlog_data, args.hours
    )
    
    # 5. 确定输出文件路径
    if not args.output or args.output == '':
        # 如果没有指定输出路径，使用当前目录并生成标准文件名
        output_file = generate_output_filename(args.wechat_id, '.', end_time)
    elif os.path.isdir(args.output):
        # 如果是目录，生成标准文件名
        output_file = generate_output_filename(args.wechat_id, args.output, end_time)
    else:
        # 如果是文件路径，直接使用
        output_file = args.output
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # 6. 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        
        print(f"聊天记录已保存到: {output_file}")
        
        if args.verbose:
            print(f"文件大小: {os.path.getsize(output_file)} 字节")
            print("任务完成!")
        
    except Exception as e:
        print(f"写入输出文件失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())