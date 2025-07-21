# Claude WeChat 工具集

这是一个用于微信群聊管理和分析的Python工具集，包含消息发送、聊天记录获取、群组查询和日志分析等功能。

## 环境要求

- Python 3.9+
- 虚拟环境（推荐）

## 安装依赖

创建虚拟环境并安装依赖：

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install pyyaml requests aiohttp
```

## 配置文件

### config.yml
用于配置微信机器人API地址：

```yaml
webot_url: "http://your-webot-api-url/api/sendmsg"
```

### mcp.json
用于配置MCP服务器连接：

```json
{
  "mcpServers": {
    "chatlog": {
      "url": "http://your-mcp-server-url/sse"
    }
  }
}
```

## 工具使用说明

### 1. post_wechat.py - 微信群消息发送

**功能**: 发送纯文本消息到指定微信群

**用法**:
```bash
source venv/bin/activate
python post_wechat.py -i <消息文件> -wid <微信群ID>
```

**参数**:
- `-i, --input`: 包含要发送消息的纯文本文件路径
- `-wid, --wechat-id`: 目标微信群的ID

**示例**:
```bash
python post_wechat.py -i message.txt -wid GROUP_ID_123@chatroom
```

**依赖**: config.yml文件，包含webot_url配置

---

### 2. querywechatid.py - 微信群ID查询

**功能**: 根据群名称查询微信群ID

**用法**:
```bash
source venv/bin/activate
python querywechatid.py "群名称"
```

**参数**:
- 群名称（作为位置参数）

**示例**:
```bash
python querywechatid.py "AI软工"
# 输出: GROUP_ID_123@chatroom 或 null（如果未找到）
```

**依赖**: mcp.json文件，用于连接MCP服务器

---

### 3. getrecentchatlogs.py - 获取微信群聊天记录

**功能**: 获取指定微信群的近期聊天记录

**用法**:
```bash
source venv/bin/activate
python getrecentchatlogs.py -wid <微信群ID> [-o 输出文件] [-t 小时数] [--verbose] [--nouser 用户ID]
```

**参数**:
- `-wid, --wechat-id`: 微信群ID（必需）
- `-o, --output`: 输出文件路径或目录（可选，默认自动生成）
- `-t, --hours`: 获取近多少小时的记录（默认24小时）
- `--verbose, -v`: 显示详细信息
- `--nouser`: 要过滤的用户微信ID

**示例**:
```bash
# 获取近24小时的聊天记录
python getrecentchatlogs.py -wid GROUP_ID_123@chatroom

# 获取近48小时的记录并保存到指定文件
python getrecentchatlogs.py -wid GROUP_ID_456@chatroom -o output.md -t 48

# 获取记录并过滤特定用户
python getrecentchatlogs.py -wid GROUP_ID_123@chatroom --nouser wxid_abc123 -v
```

**依赖**: mcp.json文件，用于连接MCP服务器

---

### 4. runmcp.py - MCP客户端群聊分析

**功能**: 连接MCP服务器分析特定群聊数据

**用法**:
```bash
source venv/bin/activate
python runmcp.py -p <提示文件> -o <输出文件>
```

**参数**:
- `-p, --prompt`: 输入提示文件路径（如test.md）
- `-o, --output`: 输出文件路径（如test_out.md）

**示例**:
```bash
python runmcp.py -p analysis_prompt.md -o analysis_result.md
```

**内置群聊**:
- NS AI+: GROUP_ID_456@chatroom
- AI软工: 古法编程到尽头了: GROUP_ID_123@chatroom  
- Claude 全家桶 🫒 Life Hacker: GROUP_ID_789@chatroom

**依赖**: mcp.json文件，用于连接MCP服务器

---

### 5. analyze_logs.py - Claude CLI日志分析

**功能**: 使用Claude CLI分析日志文件

**用法**:
```bash
python analyze_logs.py [-p 提示文件] [-i 日志文件...] [-o 输出文件] [日志文件...]
```

**参数**:
- `-p, --prompt`: 提示文件（默认: prompt.md）
- `-i, --input`: 输入日志文件列表
- `-o, --output`: 输出文件名（默认: output_YYYYMMDD.md）
- 位置参数: 额外的日志文件

**示例**:
```bash
# 使用默认提示文件分析日志
python analyze_logs.py log1.txt log2.txt

# 使用自定义提示文件
python analyze_logs.py -p custom_prompt.md -i chat.log error.log

# 指定输出文件
python analyze_logs.py -p analysis.md -i data.log -o result.md
```

**依赖**: 
- Claude CLI工具已安装
- 提示文件存在
- 日志文件存在

---

### 6. send_ai_summary_today.sh - 微信AI总结工作流

**功能**: 自动化微信群聊分析工作流，包括获取聊天记录、AI分析和发送结果

**用法**:
```bash
./send_ai_summary_today.sh [选项]
```

**选项**:
- `--help, -h`: 显示帮助信息
- `--no-debug`: 关闭调试信息

**工作流程**:
1. 从多个配置的微信群获取聊天记录
2. 使用AI分析聊天记录生成摘要
3. 将分析结果发送到指定微信群

**配置说明**:
- `group_source_ids`: 源群组ID数组，支持多个群
- `group_send_id`: 目标群组ID，用于发送分析结果
- `input_prompt`: AI分析使用的提示文件路径
- `ignore_user`: 要忽略的用户微信ID（可选）
- `hours`: 获取聊天记录的时间范围（小时）

**重试机制**:
- AI分析具备自动重试功能，最多重试2次（总共3次尝试）
- 当输出文件为空或不存在时自动重试
- 重试间隔5秒，失败后会清理无效文件

**示例**:
```bash
# 运行完整工作流
./send_ai_summary_today.sh

# 关闭调试模式运行
./send_ai_summary_today.sh --no-debug

# 查看帮助信息
./send_ai_summary_today.sh --help
```

**依赖**:
- 虚拟环境已激活
- config.yml和mcp.json配置文件
- ai_prompt.md提示文件
- 所有Python脚本文件存在

## 使用工作流程示例

### 1. 发送消息到群聊
```bash
# 1. 查询群ID
python querywechatid.py "AI软工"
# 输出: GROUP_ID_123@chatroom

# 2. 准备消息文件
echo "Hello, World!" > message.txt

# 3. 发送消息
python post_wechat.py -i message.txt -wid GROUP_ID_123@chatroom
```

### 2. 获取并分析群聊记录
```bash
# 1. 获取近期聊天记录
python getrecentchatlogs.py -wid GROUP_ID_123@chatroom -t 48 -o recent_chat.md

# 2. 创建分析提示
echo "请总结这些聊天记录的主要话题" > analysis_prompt.md

# 3. 分析聊天记录
python analyze_logs.py -p analysis_prompt.md -i recent_chat.md -o summary.md
```

### 3. 自动化工作流（推荐）
```bash
# 1. 配置工作流脚本
# 编辑 send_ai_summary_today.sh 中的群组ID配置
# 设置 group_source_ids 数组（源群组）
# 设置 group_send_id（目标群组）

# 2. 准备AI分析提示文件
echo "请分析以下群聊记录并生成简洁的总结报告" > ai_prompt.md

# 3. 运行完整自动化流程
./send_ai_summary_today.sh

# 该脚本会自动完成：
# - 从多个群获取聊天记录
# - AI分析生成摘要（带重试机制）
# - 发送结果到指定群
```

## 注意事项

1. **虚拟环境**: 强烈建议在虚拟环境中运行所有脚本
2. **配置文件**: 确保config.yml和mcp.json文件配置正确
3. **权限**: 确保有足够的权限访问指定的微信群和MCP服务器
4. **文件路径**: 所有文件路径建议使用绝对路径或确保工作目录正确
5. **编码**: 所有文本文件建议使用UTF-8编码

## 故障排除

### 常见错误

1. **ModuleNotFoundError**: 确保已激活虚拟环境并安装了所需依赖
2. **配置文件缺失**: 检查config.yml或mcp.json文件是否存在且格式正确
3. **连接失败**: 检查网络连接和服务器地址配置
4. **权限错误**: 确保对输出目录有写入权限

### 调试技巧

- 使用`--verbose`或`-v`参数查看详细信息
- 检查生成的临时文件了解处理过程
- 验证配置文件格式和服务器连接状态
