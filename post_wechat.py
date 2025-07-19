#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信群消息发送脚本
发送纯文本消息到指定微信群
"""

import argparse
import sys
import os
import yaml
import requests
import xml.etree.ElementTree as ET
from typing import Optional


def load_config() -> Optional[str]:
    """
    从 config.yml 文件中读取 webot_url 配置
    
    Returns:
        str: webot_url 的值，如果读取失败返回 None
    """
    try:
        # 检查配置文件是否存在
        if not os.path.exists('config.yml'):
            print("错误：找不到 config.yml 配置文件")
            return None
            
        # 读取配置文件
        with open('config.yml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
        # 检查 webot_url 是否存在
        if not config or 'webot_url' not in config:
            print("错误：config.yml 中缺少 webot_url 配置")
            return None
            
        webot_url = config['webot_url']
        if not webot_url:
            print("错误：config.yml 中 webot_url 配置为空")
            return None
            
        return webot_url
        
    except yaml.YAMLError as e:
        print(f"错误：解析 config.yml 文件失败 - {e}")
        return None
    except FileNotFoundError:
        print("错误：找不到 config.yml 配置文件")
        return None
    except Exception as e:
        print(f"错误：读取配置文件时发生未知错误 - {e}")
        return None


def read_text_file(file_path: str) -> Optional[str]:
    """
    读取输入的纯文本文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件内容，如果读取失败返回 None
    """
    try:
        if not os.path.exists(file_path):
            print(f"错误：找不到输入文件 {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            
        if not content:
            print("警告：输入文件内容为空")
            
        return content
        
    except Exception as e:
        print(f"错误：读取输入文件失败 - {e}")
        return None


def send_wechat_message(webot_url: str, wid: str, message: str) -> bool:
    """
    发送微信消息到指定群组
    
    Args:
        webot_url: 微信机器人API地址
        wid: 微信群ID
        message: 要发送的消息内容
        
    Returns:
        bool: 发送成功返回True，失败返回False
    """
    try:
        # 准备POST数据
        post_data = {
            'to': wid,
            'msg': message
        }
        
        # 发送HTTP POST请求
        print(f"正在发送消息到群组 {wid}...")
        response = requests.post(webot_url, data=post_data, timeout=30)
        
        # 检查HTTP响应状态
        if response.status_code != 200:
            print(f"错误：HTTP请求失败，状态码：{response.status_code}")
            return False
            
        # 解析响应（支持JSON和XML格式）
        try:
            # 首先尝试解析JSON
            import json
            response_data = json.loads(response.text)
            code = str(response_data.get('code', ''))
            msg = response_data.get('msg', '未知错误')
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试解析XML
            try:
                root = ET.fromstring(response.text)
                code_element = root.find('.//code')
                msg_element = root.find('.//msg')
                
                if code_element is None:
                    print("错误：响应中缺少code字段")
                    return False
                    
                code = code_element.text
                msg = msg_element.text if msg_element is not None else "未知错误"
                
            except ET.ParseError as e:
                print(f"错误：解析响应失败（既不是有效的JSON也不是有效的XML）- {e}")
                print(f"响应内容：{response.text}")
                return False
        
        # 检查返回码
        if code == '200':
            print("成功：消息发送成功")
            return True
        else:
            print(f"失败：消息发送失败，原因：{msg}")
            return False
            
    except requests.exceptions.Timeout:
        print("错误：请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("错误：连接失败，请检查网络或webot_url配置")
        return False
    except requests.exceptions.RequestException as e:
        print(f"错误：HTTP请求失败 - {e}")
        return False
    except Exception as e:
        print(f"错误：发送消息时发生未知错误 - {e}")
        return False


def main():
    """
    主函数
    """
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='发送纯文本消息到微信群')
    parser.add_argument('-i', '--input', required=True, help='输入的纯文本文件路径')
    parser.add_argument('-wid', '--wechat-id', required=True, help='微信群ID号')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 读取配置文件
    print("正在读取配置文件...")
    webot_url = load_config()
    if webot_url is None:
        sys.exit(1)
    
    print(f"使用webot_url: {webot_url}")
    
    # 读取输入文件
    print(f"正在读取输入文件: {args.input}")
    message_content = read_text_file(args.input)
    if message_content is None:
        sys.exit(1)
        
    if not message_content:
        print("警告：消息内容为空，继续发送...")
    
    # 发送微信消息
    success = send_wechat_message(webot_url, args.wechat_id, message_content)
    
    if success:
        print("程序执行完成")
        sys.exit(0)
    else:
        print("程序执行失败")
        sys.exit(1)


if __name__ == '__main__':
    main() 