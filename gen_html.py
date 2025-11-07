#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Convert markdown to HTML using Claude CLI')
    parser.add_argument('-i', '--input', required=True, help='Input markdown file')
    parser.add_argument('-o', '--output', required=True, help='Output HTML file')

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found")
        sys.exit(1)

    try:
        # Read markdown content
        with open(args.input, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Extract title from markdown (first line starting with #)
        title = "AI资讯摘要"  # Default title
        lines = markdown_content.strip().split('\n')
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()

        # Create prompt
        prompt = f"""请将以下markdown文本转换为结构清晰、认知负荷轻量的HTML页面。

要求：
1. 使用完整的HTML5结构（包含<!DOCTYPE html>、<html>、<head>、<body>等标签）
2. 在<title>标签中使用文档的标题：{title}
3. 添加适当的CSS样式，使页面简洁美观、易于阅读
4. 使用响应式设计，适配移动端和桌面端
5. 保持内容的层次结构清晰
6. emoji和格式要正确显示
7. 使用合适的字体和间距，降低认知负荷
8. 添加适当的颜色和视觉元素，但不要过于花哨
9. 直接输出完整的HTML代码，不要用markdown代码块包裹

Markdown内容：

{markdown_content}

请直接输出完整的HTML代码。
"""

        # Save prompt to temp file
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_prompt_path = f"html_prompt_{date_str}.txt"

        with open(temp_prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt)

        print(f"Prompt saved to: {temp_prompt_path}")

        # Build claude command
        claude_path = "/opt/homebrew/bin/claude"
        claude_cmd_str = f'{claude_path} -p "$(cat {temp_prompt_path})"'

        print(f"Running command: {claude_cmd_str}")

        # Set up environment
        env = os.environ.copy()
        env['PATH'] = f"/opt/homebrew/bin:{env.get('PATH', '')}"
        env['ANTHROPIC_BASE_URL'] = 'https://gaccode.com/claudecode'
        env['NODE_EXTRA_CA_CERTS'] = '/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/ca.pem'

        # Execute claude command
        result = subprocess.run(claude_cmd_str, shell=True, capture_output=True, text=True, check=True, env=env)
        html_output = result.stdout.strip()

        # Extract HTML if wrapped in code blocks
        if '```html' in html_output:
            # Extract content between ```html and ```
            start = html_output.find('```html') + 7
            end = html_output.rfind('```')
            if end > start:
                html_output = html_output[start:end].strip()
        elif '```' in html_output:
            # Extract content between ``` and ```
            parts = html_output.split('```')
            if len(parts) >= 3:
                html_output = parts[1].strip()
                if html_output.startswith('html\n'):
                    html_output = html_output[5:].strip()

        # Ensure HTML starts with <!DOCTYPE
        if not html_output.strip().startswith('<!DOCTYPE') and not html_output.strip().startswith('<html'):
            print("Warning: Generated content doesn't appear to be complete HTML")

        # Write HTML to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_output)

        # Verify the output file
        if not os.path.exists(args.output):
            print("Error: Output file was not created")
            sys.exit(1)

        file_size = os.path.getsize(args.output)
        if file_size == 0:
            print("Error: Output file is empty")
            sys.exit(1)

        print(f"HTML generation complete. Output saved to: {args.output}")
        print(f"File size: {file_size} bytes")
        print(f"Prompt file kept at: {temp_prompt_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error running claude command: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
