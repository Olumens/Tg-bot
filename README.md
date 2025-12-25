# Telegram Bot - 功能完整的Telegram机器人

利用VPS以及Telegram机器人，实现在Telegram机器人发送对应菜单，设置Todolist以及调用AI及图片生成。

## 功能特点

📝 **待办事项管理 (Todolist)**
- 添加新任务
- 查看所有任务
- 完成任务
- 删除任务
- 每个用户独立的任务列表

🤖 **AI聊天 (AI Chat)**
- 使用OpenAI GPT模型进行智能对话
- 支持自然语言交互
- 可配置不同的AI模型

🎨 **图片生成 (Image Generation)**
- 使用DALL-E 3生成高质量图片
- 根据文字描述创建图像
- 支持多种风格和主题

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Olumens/Tg-bot.git
cd Tg-bot
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或使用虚拟环境（推荐）：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例配置文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenAI API Key (用于AI聊天和图片生成功能)
OPENAI_API_KEY=your_openai_api_key_here

# 可选：OpenAI模型设置
OPENAI_MODEL=gpt-3.5-turbo
```

#### 获取 Telegram Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的token到 `.env` 文件

#### 获取 OpenAI API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册并登录账号
3. 进入 API Keys 页面创建新的API密钥
4. 复制密钥到 `.env` 文件

### 4. 运行机器人

```bash
python bot.py
```

如果一切正常，你会看到：
```
机器人启动成功！按 Ctrl+C 停止。
```

## 使用说明

### 基本命令

- `/start` - 开始使用机器人，显示欢迎消息
- `/menu` - 显示主菜单
- `/todo` - 快速访问待办事项功能
- `/ai` - 快速访问AI聊天功能
- `/image` - 快速访问图片生成功能

### 待办事项功能

1. **添加任务**：点击"添加任务"按钮，然后输入任务内容
2. **查看任务**：点击"查看任务"查看所有未完成的任务
3. **完成任务**：点击"完成任务"，选择要完成的任务
4. **删除任务**：点击"删除任务"，选择要删除的任务

每个用户的任务独立存储，互不干扰。

### AI聊天功能

1. 点击"AI聊天"按钮或使用 `/ai` 命令
2. 直接发送消息，AI会自动回复
3. 使用 `/menu` 返回主菜单

### 图片生成功能

1. 点击"图片生成"按钮或使用 `/image` 命令
2. 发送图片描述（例如："一只可爱的橙色猫咪在花园里玩耍"）
3. 等待图片生成完成
4. 使用 `/menu` 返回主菜单

## 在VPS上部署

### 使用systemd服务（推荐）

创建服务文件 `/etc/systemd/system/telegram-bot.service`：

```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Tg-bot
Environment="PATH=/path/to/Tg-bot/venv/bin"
ExecStart=/path/to/Tg-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### 使用screen或tmux

```bash
# 使用screen
screen -S telegram-bot
python bot.py
# 按 Ctrl+A 然后按 D 分离会话

# 恢复会话
screen -r telegram-bot

# 或使用tmux
tmux new -s telegram-bot
python bot.py
# 按 Ctrl+B 然后按 D 分离会话

# 恢复会话
tmux attach -t telegram-bot
```

## 项目结构

```
Tg-bot/
├── bot.py              # 主程序文件
├── requirements.txt    # Python依赖
├── .env.example       # 环境变量示例
├── .env               # 环境变量配置（需自行创建）
├── .gitignore         # Git忽略文件
├── README.md          # 项目说明文档
└── todolist_*.json    # 用户任务数据（自动生成）
```

## 数据存储

- 待办事项数据存储在本地JSON文件中
- 每个用户有独立的 `todolist_{user_id}.json` 文件
- 数据包括任务ID、内容、创建时间、完成状态等

## 故障排除

### 机器人无法启动

- 检查 `.env` 文件是否正确配置
- 确认 `TELEGRAM_BOT_TOKEN` 是否有效
- 查看错误日志信息

### AI功能不可用

- 确认已安装 `openai` 包
- 检查 `OPENAI_API_KEY` 是否正确
- 确认OpenAI账户有足够的额度

### 图片生成失败

- 确认使用的是DALL-E 3支持的账户
- 检查API额度是否充足
- 图片描述需要符合OpenAI的内容政策

## 注意事项

1. **API费用**：OpenAI API按使用量收费，请注意控制使用
2. **数据安全**：`.env` 文件包含敏感信息，不要提交到Git
3. **权限管理**：可以在代码中添加用户白名单功能
4. **备份数据**：定期备份 `todolist_*.json` 文件

## 开发与贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 作者

[Olumens](https://github.com/Olumens)
