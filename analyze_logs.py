#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import re
import tempfile
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Analyze log files using Claude CLI')
    parser.add_argument('-p', '--prompt', default='prompt.md', 
                       help='Prompt file (default: prompt.md)')
    parser.add_argument('-i', '--input', nargs='+', dest='log_files',
                       help='Input log files (space-separated list)')
    parser.add_argument('-o', '--output', 
                       help='Output filename (default: output_YYYYMMDD.md)')
    parser.add_argument('files', nargs='*', help='Additional log files')
    
    args = parser.parse_args()
    
    # Combine input files from -i and positional arguments
    log_files = (args.log_files or []) + args.files
    
    if not log_files:
        print("Error: No log files provided")
        print("Usage: python analyze_logs.py [-p prompt_file] [-i log_file] [log_files...]")
        print("Example: python analyze_logs.py -p test.md -i log1.txt log2.txt")
        sys.exit(1)
    
    # Check if prompt file exists
    if not os.path.exists(args.prompt):
        print(f"Error: {args.prompt} not found")
        sys.exit(1)
    
    # Check log files exist
    valid_files = []
    for log_file in log_files:
        if not os.path.exists(log_file):
            print(f"Warning: {log_file} not found, skipping...")
            continue
        valid_files.append(log_file)
    
    if not valid_files:
        print("Error: No valid log files found")
        sys.exit(1)
    
    try:
        # Create combined prompt
        combined_prompt = ""
        
        
        # 1. Add user's prompt file content
        with open(args.prompt, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        combined_prompt += prompt_content + "\n\n"
        
        # 2. Add all input log files content
        for log_file in valid_files:
            combined_prompt += f"=== {log_file} ===\n"
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            combined_prompt += log_content + "\n\n"
        
        # 3. Add output format instructions
        combined_prompt += """请按照以下格式输出结果：
<!-- start -->
[你的分析结果在这里]
<!-- end -->

"""
    
        # Save combined prompt to current directory
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_prompt_path = f"combined_prompt_{date_str}.md"
        
        with open(temp_prompt_path, 'w', encoding='utf-8') as f:
            f.write(combined_prompt)
        
        print(f"Combined prompt saved to: {temp_prompt_path}")
        
        # Build claude command with -p flag and cat
        # Use absolute path for crontab compatibility
        claude_path = "/opt/homebrew/bin/claude"
        claude_cmd_str = f'{claude_path} -p "$(cat {temp_prompt_path})"'
        
        print(f"Running command: {claude_cmd_str}")
        
        # Set up environment for crontab compatibility
        env = os.environ.copy()
        env['PATH'] = f"/opt/homebrew/bin:{env.get('PATH', '')}"
        env['ANTHROPIC_BASE_URL'] = 'https://gaccode.com/claudecode'
        env['NODE_EXTRA_CA_CERTS'] = '/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/ca.pem'
        
        # Execute claude command using shell=True for command substitution
        result = subprocess.run(claude_cmd_str, shell=True, capture_output=True, text=True, check=True, env=env)
        output = result.stdout
        
        # Extract content between <!-- start --> and <!-- end -->
        pattern = r'<!-- start -->(.*?)<!-- end -->'
        match = re.search(pattern, output, re.DOTALL)
        
        if match:
            msg = match.group(1).strip()
            # Check if extracted content is empty
            if not msg:
                print("Error: Extracted content between markers is empty")
                sys.exit(1)
        else:
            print("Error: No content found between <!-- start --> and <!-- end --> markers")
            sys.exit(1)
        
        # Generate output filename
        if args.output:
            output_file = args.output
        else:
            date_str = datetime.now().strftime('%Y%m%d')
            output_file = f"output_{date_str}.md"
        
        # Write extracted message to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(msg)
        
        # Verify the output file was written and is not empty
        if not os.path.exists(output_file):
            print("Error: Output file was not created")
            sys.exit(1)
            
        if os.path.getsize(output_file) == 0:
            print("Error: Output file is empty")
            sys.exit(1)
        
        print(f"Analysis complete. Results saved to: {output_file}")
        print(f"Combined prompt file kept at: {temp_prompt_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running claude command: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Keep the combined prompt file for debugging
        pass

if __name__ == "__main__":
    main()