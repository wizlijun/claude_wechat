#!/usr/bin/env python3
"""
MCP Client Script for WeChat Group Chat Analysis
Usage: python runmcp.py -p test.md -o test_out.md
"""

import argparse
import asyncio
import json
import sys
from typing import Optional
import aiohttp
import asyncio


class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        
    async def send_request(self, prompt: str) -> str:
        """Send request to MCP server and analyze chatlog"""
        try:
            async with aiohttp.ClientSession() as session:
                # First, get recent sessions to understand what groups are available
                session_url = self.server_url.replace('/sse', '/api/v1/session')
                print(f"Getting recent sessions from: {session_url}")
                
                async with session.get(session_url) as response:
                    if response.status == 200:
                        session_data = await response.text(encoding='utf-8', errors='ignore')
                        print(f"Recent sessions (first 500 chars): {session_data[:500]}...")
                        
                        # Look for the groups mentioned in the prompt using correct IDs
                        target_groups = [
                            "43543695744@chatroom",  # NS AI+
                            "27587714869@chatroom",  # AI软工: 古法编程到尽头了 
                            "49332505177@chatroom"   # Claude 全家桶 🫒 Life Hacker
                        ]
                        chatlog_results = []
                        
                        for group in target_groups:
                            print(f"\nSearching for chatlog in group: {group}")
                            
                            # Try to get chatlog for this group
                            chatlog_url = self.server_url.replace('/sse', '/api/v1/chatlog')
                            params = {
                                'chatroom': group,
                                'limit': 100  # Get last 100 messages
                            }
                            
                            async with session.get(chatlog_url, params=params) as chat_response:
                                if chat_response.status == 200:
                                    chat_data = await chat_response.text(encoding='utf-8', errors='ignore')
                                    print(f"Got chatlog for {group} (first 300 chars): {chat_data[:300]}...")
                                    chatlog_results.append(f"=== {group} ===\n{chat_data}\n")
                                else:
                                    print(f"Failed to get chatlog for {group}: {chat_response.status}")
                        
                        if chatlog_results:
                            # Combine all chatlog data
                            combined_data = "\n".join(chatlog_results)
                            
                            # Create analysis prompt combining the original prompt with actual data
                            analysis_prompt = f"""
{prompt}

以下是群聊数据：
{combined_data}
"""
                            return analysis_prompt
                        else:
                            return f"无法获取到指定群聊的数据。可用的会话信息：\n{session_data}"
                    else:
                        return f"无法连接到MCP API：HTTP {response.status}"
                        
        except Exception as e:
            return f"处理请求时出错：{e}"


async def main():
    parser = argparse.ArgumentParser(description='Run MCP client with prompt file')
    parser.add_argument('-p', '--prompt', required=True, help='Input prompt file (e.g., test.md)')
    parser.add_argument('-o', '--output', required=True, help='Output file (e.g., test_out.md)')
    
    args = parser.parse_args()
    
    # Read MCP configuration
    try:
        with open('mcp.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        server_url = config['mcpServers']['chatlog']['url']
        print(f"Connecting to MCP server: {server_url}")
        
    except FileNotFoundError:
        print("Error: mcp.json not found")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing configuration key {e}")
        sys.exit(1)
    
    # Read prompt file
    try:
        with open(args.prompt, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        print(f"Read prompt from: {args.prompt}")
        
    except FileNotFoundError:
        print(f"Error: Prompt file {args.prompt} not found")
        sys.exit(1)
    
    # Initialize MCP client and send request
    client = MCPClient(server_url)
    
    try:
        print("Sending request to MCP server...")
        result = await client.send_request(prompt_content)
        
        # Write result to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"Result written to: {args.output}")
        print("MCP request completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())