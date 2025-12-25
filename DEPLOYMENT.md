# 部署指南 / Deployment Guide

本文档提供在VPS上部署Telegram机器人的详细步骤。

## 前置要求

- VPS服务器（建议Ubuntu 20.04+或Debian 11+）
- Root或sudo权限
- Python 3.8+
- 稳定的网络连接

## 方法一：使用systemd服务（推荐生产环境）

### 1. 准备环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和必要工具
sudo apt install -y python3 python3-pip python3-venv git

# 创建专用用户（可选但推荐）
sudo useradd -m -s /bin/bash telegram-bot
sudo su - telegram-bot
```

### 2. 部署代码

```bash
# 克隆仓库
cd /home/telegram-bot
git clone https://github.com/Olumens/Tg-bot.git
cd Tg-bot

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

填入以下内容：
```env
TELEGRAM_BOT_TOKEN=你的机器人token
OPENAI_API_KEY=你的OpenAI密钥
OPENAI_MODEL=gpt-3.5-turbo
```

### 4. 配置systemd服务

```bash
# 退出telegram-bot用户
exit

# 编辑服务文件
sudo nano /etc/systemd/system/telegram-bot.service
```

内容如下（修改路径为实际路径）：
```ini
[Unit]
Description=Telegram Bot with Todolist, AI Chat and Image Generation
After=network.target

[Service]
Type=simple
User=telegram-bot
Group=telegram-bot
WorkingDirectory=/home/telegram-bot/Tg-bot
Environment="PATH=/home/telegram-bot/Tg-bot/venv/bin"
ExecStart=/home/telegram-bot/Tg-bot/venv/bin/python /home/telegram-bot/Tg-bot/bot.py
Restart=always
RestartSec=10

# 日志配置
StandardOutput=journal
StandardError=journal

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 5. 启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start telegram-bot

# 查看状态
sudo systemctl status telegram-bot

# 设置开机自启
sudo systemctl enable telegram-bot
```

### 6. 管理服务

```bash
# 停止服务
sudo systemctl stop telegram-bot

# 重启服务
sudo systemctl restart telegram-bot

# 查看日志
sudo journalctl -u telegram-bot -f

# 查看最近100行日志
sudo journalctl -u telegram-bot -n 100
```

## 方法二：使用Screen（适合快速部署）

### 1. 安装Screen

```bash
sudo apt install screen -y
```

### 2. 部署代码

```bash
# 克隆仓库
git clone https://github.com/Olumens/Tg-bot.git
cd Tg-bot

# 安装依赖
pip3 install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

### 3. 启动机器人

```bash
# 创建screen会话
screen -S telegram-bot

# 运行机器人
python3 bot.py

# 分离会话（按键）
# Ctrl+A, 然后按 D
```

### 4. 管理Screen会话

```bash
# 查看所有会话
screen -ls

# 重新连接会话
screen -r telegram-bot

# 强制分离并连接
screen -d -r telegram-bot

# 结束会话（在会话内）
exit
```

## 方法三：使用Docker（推荐容器化部署）

### 1. 创建Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY bot.py .
COPY .env .

# 运行机器人
CMD ["python", "bot.py"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: telegram-bot
    restart: always
    volumes:
      - ./data:/app/data
    env_file:
      - .env
```

### 3. 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down

# 重启
docker-compose restart
```

## 安全加固

### 1. 防火墙配置

```bash
# 安装UFW
sudo apt install ufw -y

# 允许SSH（重要！）
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 保护.env文件

```bash
# 设置正确的权限
chmod 600 .env
chown telegram-bot:telegram-bot .env
```

### 3. 定期更新

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 更新Python包
cd /home/telegram-bot/Tg-bot
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 监控和维护

### 1. 查看系统资源使用

```bash
# CPU和内存使用
top

# 或使用htop（需要安装）
sudo apt install htop
htop

# 查看进程
ps aux | grep bot.py
```

### 2. 日志管理

```bash
# 如果使用systemd
sudo journalctl -u telegram-bot --since today

# 如果使用nohup
tail -f bot.log

# 清理旧日志
sudo journalctl --vacuum-time=7d
```

### 3. 数据备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/telegram-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cd /home/telegram-bot/Tg-bot
tar -czf $BACKUP_DIR/todolist_backup_$DATE.tar.gz todolist_*.json

# 保留最近7天的备份
find $BACKUP_DIR -name "todolist_backup_*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
# 添加行：
# 0 2 * * * /home/telegram-bot/Tg-bot/backup.sh
```

## 故障排除

### 问题1：机器人无法启动

```bash
# 检查日志
sudo journalctl -u telegram-bot -n 50

# 检查配置文件
cat .env | grep -v '^#'

# 手动测试
cd /home/telegram-bot/Tg-bot
source venv/bin/activate
python bot.py
```

### 问题2：网络连接问题

```bash
# 测试Telegram API连通性
curl -I https://api.telegram.org

# 测试OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 检查DNS
ping api.telegram.org
```

### 问题3：权限问题

```bash
# 修复文件权限
sudo chown -R telegram-bot:telegram-bot /home/telegram-bot/Tg-bot
chmod 755 /home/telegram-bot/Tg-bot
chmod 644 /home/telegram-bot/Tg-bot/*.py
chmod 600 /home/telegram-bot/Tg-bot/.env
```

### 问题4：内存不足

```bash
# 查看内存使用
free -h

# 创建swap空间（如果需要）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 性能优化

### 1. 使用缓存

可以在bot.py中添加缓存机制，减少API调用：

```python
import functools
import time

@functools.lru_cache(maxsize=100)
def cached_api_call(prompt, timestamp):
    # API调用逻辑
    pass

# 使用时传入当前时间戳（精确到分钟）
timestamp = int(time.time() / 60)
result = cached_api_call(prompt, timestamp)
```

### 2. 调整系统参数

```bash
# 编辑系统限制
sudo nano /etc/security/limits.conf

# 添加：
telegram-bot soft nofile 65536
telegram-bot hard nofile 65536
```

## 更新机器人

```bash
# 方法1：使用systemd
sudo systemctl stop telegram-bot
cd /home/telegram-bot/Tg-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start telegram-bot

# 方法2：使用Docker
cd /home/telegram-bot/Tg-bot
git pull
docker-compose down
docker-compose up -d --build
```

## 多机器人部署

如果需要部署多个机器人实例：

```bash
# 复制目录
cp -r Tg-bot Tg-bot-2

# 修改配置
cd Tg-bot-2
nano .env  # 使用不同的token

# 创建新服务
sudo cp /etc/systemd/system/telegram-bot.service \
        /etc/systemd/system/telegram-bot-2.service

# 修改服务文件
sudo nano /etc/systemd/system/telegram-bot-2.service
# 更新WorkingDirectory和ExecStart路径

# 启动新服务
sudo systemctl start telegram-bot-2
sudo systemctl enable telegram-bot-2
```

## 常用命令快速参考

```bash
# systemd服务
sudo systemctl start telegram-bot      # 启动
sudo systemctl stop telegram-bot       # 停止
sudo systemctl restart telegram-bot    # 重启
sudo systemctl status telegram-bot     # 状态
sudo journalctl -u telegram-bot -f     # 查看日志

# Screen会话
screen -S telegram-bot                 # 创建会话
screen -ls                             # 列出会话
screen -r telegram-bot                 # 连接会话
# Ctrl+A D                             # 分离会话

# Docker
docker-compose up -d                   # 启动
docker-compose down                    # 停止
docker-compose logs -f                 # 查看日志
docker-compose restart                 # 重启
```

## 联系与支持

如遇到问题，请在GitHub仓库提交Issue：
https://github.com/Olumens/Tg-bot/issues
