#!/usr/bin/env python3
"""
Query WeChat ID Script
Usage: python querywechatid.py "AI软工"
Returns the WeChat ID if found, otherwise returns null
"""

import sys
import asyncio
import aiohttp
import json


class WeChatIDQuery:
    def __init__(self, server_url: str):
        self.server_url = server_url
        
    async def query_wechat_id(self, search_term: str) -> str:
        """Query WeChat ID by group name or partial name"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get chatroom list
                chatroom_url = self.server_url.replace('/sse', '/api/v1/chatroom')
                
                async with session.get(chatroom_url) as response:
                    if response.status == 200:
                        chatroom_data = await response.text(encoding='utf-8', errors='ignore')
                        
                        # Parse CSV data (skip header)
                        lines = chatroom_data.strip().split('\n')
                        if len(lines) <= 1:
                            return "null"
                        
                        # Search for matching groups
                        for line in lines[1:]:  # Skip header
                            parts = line.split(',')
                            if len(parts) >= 3:
                                wechat_id = parts[0]
                                group_name = parts[2] if len(parts) > 2 else ""
                                
                                # Check if search term matches group name (case insensitive)
                                if search_term.lower() in group_name.lower():
                                    return wechat_id
                        
                        return "null"
                    else:
                        return "null"
                        
        except Exception as e:
            return "null"


async def main():
    if len(sys.argv) != 2:
        print("Usage: python querywechatid.py \"search_term\"")
        sys.exit(1)
    
    search_term = sys.argv[1]
    
    # Read MCP configuration
    try:
        with open('mcp.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        server_url = config['mcpServers']['chatlog']['url']
        
    except FileNotFoundError:
        print("null")
        sys.exit(0)
    except KeyError:
        print("null")
        sys.exit(0)
    
    # Query WeChat ID
    query = WeChatIDQuery(server_url)
    result = await query.query_wechat_id(search_term)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())