# 使用示例 / Usage Examples

## 快速开始 Quick Start

### 1. 基本设置 Basic Setup

```bash
# 克隆仓库
git clone https://github.com/Olumens/Tg-bot.git
cd Tg-bot

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 token
nano .env
```

### 2. 配置示例 Configuration Example

`.env` 文件内容：

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. 启动机器人 Start Bot

```bash
# 方法1: 直接运行
python bot.py

# 方法2: 使用启动脚本
./start.sh

# 方法3: 后台运行
nohup python bot.py > bot.log 2>&1 &
```

## 功能演示 Feature Demonstrations

### 待办事项 Todolist

```
用户: /start
机器人: [显示主菜单]

用户: [点击 "📝 待办事项"]
机器人: [显示待办事项菜单]

用户: [点击 "➕ 添加任务"]
机器人: 请输入任务内容：

用户: 完成项目文档
机器人: ✅ 任务已添加！
       #1 - 完成项目文档

用户: [点击 "📋 查看任务"]
机器人: 📋 你的任务列表
       #1 - 完成项目文档
       ⏰ 2024-12-25 10:00
```

### AI聊天 AI Chat

```
用户: /ai
机器人: 🤖 AI聊天模式
       请发送消息，我会用AI回复你。

用户: 什么是人工智能？
机器人: 🤖 人工智能（AI）是计算机科学的一个分支...
       [AI生成的回复]

用户: 介绍一下机器学习
机器人: 🤖 机器学习是人工智能的核心技术之一...
       [AI生成的回复]
```

### 图片生成 Image Generation

```
用户: /image
机器人: 🎨 图片生成模式
       请发送图片描述，我会为你生成图片。

用户: 一只可爱的橙色猫咪在花园里玩耍
机器人: 🎨 正在生成图片，请稍候...
       [生成并发送图片]
       🎨 根据你的描述生成的图片：
       "一只可爱的橙色猫咪在花园里玩耍"
```

## 命令速查 Command Reference

| 命令 | 功能 |
|------|------|
| `/start` | 开始使用，显示欢迎消息和主菜单 |
| `/menu` | 显示主菜单 |
| `/todo` | 快速访问待办事项 |
| `/ai` | 快速访问AI聊天 |
| `/image` | 快速访问图片生成 |

## 菜单结构 Menu Structure

```
🏠 主菜单
├── 📝 待办事项 (Todolist)
│   ├── ➕ 添加任务
│   ├── 📋 查看任务
│   ├── ✅ 完成任务
│   └── 🗑️ 删除任务
├── 🤖 AI聊天 (AI Chat)
│   └── [直接发送消息进行对话]
├── 🎨 图片生成 (Image Gen)
│   └── [发送描述生成图片]
└── ℹ️ 帮助 (Help)
    └── [显示帮助信息]
```

## 高级配置 Advanced Configuration

### 使用不同的AI模型 Using Different AI Models

在 `.env` 文件中修改：

```env
# 使用 GPT-4
OPENAI_MODEL=gpt-4

# 使用 GPT-3.5 Turbo (默认，更便宜)
OPENAI_MODEL=gpt-3.5-turbo
```

### VPS部署建议 VPS Deployment Tips

```bash
# 使用 screen 持久运行
screen -S telegram-bot
cd /path/to/Tg-bot
python bot.py
# 按 Ctrl+A, D 分离会话

# 查看运行状态
screen -ls

# 重新连接
screen -r telegram-bot

# 查看日志
tail -f bot.log
```

### 使用systemd服务 Using systemd Service

```bash
# 编辑服务文件，修改路径和用户名
sudo nano telegram-bot.service

# 复制到systemd目录
sudo cp telegram-bot.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start telegram-bot

# 设置开机自启
sudo systemctl enable telegram-bot

# 查看状态
sudo systemctl status telegram-bot

# 查看日志
sudo journalctl -u telegram-bot -f
```

## 数据管理 Data Management

### 备份待办事项 Backup Todolist

```bash
# 备份所有待办事项文件
tar -czf todolist_backup_$(date +%Y%m%d).tar.gz todolist_*.json

# 恢复备份
tar -xzf todolist_backup_20241225.tar.gz
```

### 清理已完成任务 Clean Completed Tasks

待办事项文件位于 `todolist_{user_id}.json`，可以手动编辑这些JSON文件来管理任务。

## 故障排除 Troubleshooting

### 问题：机器人无响应
```bash
# 检查进程是否运行
ps aux | grep bot.py

# 查看日志
tail -f bot.log

# 检查网络连接
curl -I https://api.telegram.org
```

### 问题：AI功能报错
```bash
# 测试OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 检查余额
# 访问 https://platform.openai.com/account/usage
```

### 问题：依赖安装失败
```bash
# 更新pip
pip install --upgrade pip

# 单独安装问题包
pip install python-telegram-bot==20.7 --no-cache-dir
pip install openai==1.6.1 --no-cache-dir
```

## 安全建议 Security Tips

1. **不要泄露Token**: `.env` 文件不要提交到Git
2. **限制用户访问**: 可以在代码中添加白名单
3. **监控API使用**: 定期检查OpenAI API使用量
4. **备份数据**: 定期备份待办事项文件
5. **更新依赖**: 定期更新依赖包的安全补丁

## 性能优化 Performance Optimization

### 减少API调用成本

1. 使用 `gpt-3.5-turbo` 而不是 `gpt-4`
2. 设置合理的 `max_tokens` 限制
3. 使用较小的图片尺寸（如果不需要高分辨率）

### 优化响应速度

1. 使用VPS服务器靠近Telegram服务器地区
2. 使用较快的网络连接
3. 考虑使用缓存机制

## 扩展开发 Extension Development

### 添加新功能

编辑 `bot.py`，添加新的命令处理器：

```python
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自定义命令"""
    await update.message.reply_text("这是一个自定义功能")

# 在 main() 函数中注册
application.add_handler(CommandHandler("custom", custom_command))
```

### 添加用户权限控制

```python
ALLOWED_USERS = [123456789, 987654321]  # 允许的用户ID列表

def check_permission(user_id):
    return user_id in ALLOWED_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_permission(update.effective_user.id):
        await update.message.reply_text("抱歉，你没有权限使用此机器人。")
        return
    # 正常的start处理...
```

## 贡献指南 Contributing

欢迎提交Issue和Pull Request！

### 报告问题

1. 描述问题现象
2. 提供错误日志
3. 说明运行环境

### 提交代码

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证 License

MIT License - 详见 LICENSE 文件
