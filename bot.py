#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Telegram Bot with Menu, Todolist, AI Chat, and Image Generation
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. AI features will be disabled.")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_TASK = 1
WAITING_FOR_AI_MESSAGE = 2
WAITING_FOR_IMAGE_PROMPT = 3

# Initialize OpenAI client if available
openai_client = None
if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
    try:
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")


class TodoList:
    """Manages todolist for each user"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.filename = f"todolist_{user_id}.json"
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def add_task(self, task: str) -> int:
        """Add a new task and return its ID"""
        task_id = len(self.tasks) + 1
        new_task = {
            'id': task_id,
            'task': task,
            'created': datetime.now().isoformat(),
            'completed': False
        }
        self.tasks.append(new_task)
        self.save_tasks()
        return task_id
    
    def get_tasks(self, include_completed: bool = False) -> List[Dict]:
        """Get all tasks, optionally including completed ones"""
        if include_completed:
            return self.tasks
        return [task for task in self.tasks if not task['completed']]
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                self.tasks.pop(i)
                self.save_tasks()
                return True
        return False


def get_main_menu_keyboard():
    """Create the main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📝 待办事项 (Todolist)", callback_data="menu_todo"),
            InlineKeyboardButton("🤖 AI聊天 (AI Chat)", callback_data="menu_ai"),
        ],
        [
            InlineKeyboardButton("🎨 图片生成 (Image Gen)", callback_data="menu_image"),
            InlineKeyboardButton("ℹ️ 帮助 (Help)", callback_data="menu_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_todo_menu_keyboard():
    """Create the todolist menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("➕ 添加任务", callback_data="todo_add"),
            InlineKeyboardButton("📋 查看任务", callback_data="todo_list"),
        ],
        [
            InlineKeyboardButton("✅ 完成任务", callback_data="todo_complete"),
            InlineKeyboardButton("🗑️ 删除任务", callback_data="todo_delete"),
        ],
        [InlineKeyboardButton("🔙 返回主菜单", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = update.effective_user
    welcome_text = f"""
👋 欢迎, {user.mention_html()}!

这是一个功能丰富的Telegram机器人，提供以下功能：

📝 **待办事项 (Todolist)** - 管理你的任务列表
🤖 **AI聊天** - 与AI助手对话
🎨 **图片生成** - 使用AI生成图片

请从下面的菜单中选择一个功能：
"""
    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_main":
        text = "🏠 **主菜单**\n\n请选择一个功能："
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
    
    elif query.data == "menu_todo":
        text = "📝 **待办事项管理**\n\n选择一个操作："
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=get_todo_menu_keyboard()
        )
    
    elif query.data == "menu_ai":
        if not openai_client:
            await query.edit_message_text(
                "❌ AI功能未配置。请设置OPENAI_API_KEY环境变量。",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回主菜单", callback_data="menu_main")
                ]])
            )
        else:
            await query.edit_message_text(
                "🤖 **AI聊天**\n\n请直接发送消息，我会用AI回复你。\n\n使用 /menu 返回主菜单。"
            )
            context.user_data['ai_mode'] = True
    
    elif query.data == "menu_image":
        if not openai_client:
            await query.edit_message_text(
                "❌ 图片生成功能未配置。请设置OPENAI_API_KEY环境变量。",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回主菜单", callback_data="menu_main")
                ]])
            )
        else:
            await query.edit_message_text(
                "🎨 **图片生成**\n\n请发送图片描述，我会为你生成图片。\n\n使用 /menu 返回主菜单。"
            )
            context.user_data['image_mode'] = True
    
    elif query.data == "menu_help":
        help_text = """
ℹ️ **帮助信息**

**命令列表：**
/start - 开始使用机器人
/menu - 显示主菜单
/todo - 快速访问待办事项
/ai - 快速访问AI聊天
/image - 快速访问图片生成

**待办事项功能：**
• 添加任务 - 创建新的待办任务
• 查看任务 - 查看所有未完成的任务
• 完成任务 - 标记任务为已完成
• 删除任务 - 删除不需要的任务

**AI聊天功能：**
直接发送消息，AI会回复你。

**图片生成功能：**
发送图片描述，AI会生成相应的图片。
"""
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 返回主菜单", callback_data="menu_main")
            ]])
        )


async def todo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle todolist operations"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    todo = TodoList(user_id)
    
    if query.data == "todo_add":
        await query.edit_message_text(
            "➕ **添加新任务**\n\n请输入任务内容："
        )
        context.user_data['waiting_for'] = 'task'
        return WAITING_FOR_TASK
    
    elif query.data == "todo_list":
        tasks = todo.get_tasks()
        if not tasks:
            text = "📋 **你的任务列表**\n\n暂无未完成的任务！"
        else:
            text = "📋 **你的任务列表**\n\n"
            for task in tasks:
                created = datetime.fromisoformat(task['created']).strftime('%Y-%m-%d %H:%M')
                text += f"#{task['id']} - {task['task']}\n   ⏰ {created}\n\n"
        
        await query.edit_message_text(
            text,
            reply_markup=get_todo_menu_keyboard()
        )
    
    elif query.data == "todo_complete":
        tasks = todo.get_tasks()
        if not tasks:
            await query.edit_message_text(
                "没有可完成的任务。",
                reply_markup=get_todo_menu_keyboard()
            )
        else:
            keyboard = []
            for task in tasks:
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ #{task['id']} - {task['task'][:30]}...",
                        callback_data=f"complete_{task['id']}"
                    )
                ])
            keyboard.append([
                InlineKeyboardButton("🔙 返回", callback_data="menu_todo")
            ])
            
            await query.edit_message_text(
                "选择要完成的任务：",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif query.data == "todo_delete":
        tasks = todo.get_tasks(include_completed=True)
        if not tasks:
            await query.edit_message_text(
                "没有可删除的任务。",
                reply_markup=get_todo_menu_keyboard()
            )
        else:
            keyboard = []
            for task in tasks:
                status = "✅" if task['completed'] else "⏳"
                keyboard.append([
                    InlineKeyboardButton(
                        f"🗑️ {status} #{task['id']} - {task['task'][:30]}...",
                        callback_data=f"delete_{task['id']}"
                    )
                ])
            keyboard.append([
                InlineKeyboardButton("🔙 返回", callback_data="menu_todo")
            ])
            
            await query.edit_message_text(
                "选择要删除的任务：",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif query.data.startswith("complete_"):
        task_id = int(query.data.split("_")[1])
        if todo.complete_task(task_id):
            await query.edit_message_text(
                f"✅ 任务 #{task_id} 已完成！",
                reply_markup=get_todo_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                "❌ 任务未找到。",
                reply_markup=get_todo_menu_keyboard()
            )
    
    elif query.data.startswith("delete_"):
        task_id = int(query.data.split("_")[1])
        if todo.delete_task(task_id):
            await query.edit_message_text(
                f"🗑️ 任务 #{task_id} 已删除！",
                reply_markup=get_todo_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                "❌ 任务未找到。",
                reply_markup=get_todo_menu_keyboard()
            )


async def receive_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save a new task"""
    if context.user_data.get('waiting_for') == 'task':
        user_id = update.effective_user.id
        task_text = update.message.text
        
        todo = TodoList(user_id)
        task_id = todo.add_task(task_text)
        
        await update.message.reply_text(
            f"✅ 任务已添加！\n\n#{task_id} - {task_text}",
            reply_markup=get_todo_menu_keyboard()
        )
        
        context.user_data['waiting_for'] = None
        return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    # Check if in AI chat mode
    if context.user_data.get('ai_mode'):
        await handle_ai_chat(update, context)
    # Check if in image generation mode
    elif context.user_data.get('image_mode'):
        await handle_image_generation(update, context)
    # Check if waiting for task input
    elif context.user_data.get('waiting_for') == 'task':
        await receive_task(update, context)
    else:
        await update.message.reply_text(
            "请使用 /menu 查看可用功能，或 /start 重新开始。"
        )


async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI chat messages"""
    if not openai_client:
        await update.message.reply_text(
            "❌ AI功能未配置。请使用 /menu 返回主菜单。"
        )
        return
    
    user_message = update.message.text
    
    # Send "typing" action
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": "你是一个有帮助的AI助手。"},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        await update.message.reply_text(f"🤖 {ai_response}")
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        await update.message.reply_text(
            f"❌ AI服务出错: {str(e)}\n\n使用 /menu 返回主菜单。"
        )


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image generation requests"""
    if not openai_client:
        await update.message.reply_text(
            "❌ 图片生成功能未配置。请使用 /menu 返回主菜单。"
        )
        return
    
    prompt = update.message.text
    
    # Send "upload_photo" action
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="upload_photo"
    )
    
    await update.message.reply_text("🎨 正在生成图片，请稍候...")
    
    try:
        # Call DALL-E API
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        await update.message.reply_photo(
            photo=image_url,
            caption=f"🎨 根据你的描述生成的图片：\n\"{prompt}\""
        )
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await update.message.reply_text(
            f"❌ 图片生成失败: {str(e)}\n\n使用 /menu 返回主菜单。"
        )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu"""
    # Clear any active modes
    context.user_data['ai_mode'] = False
    context.user_data['image_mode'] = False
    context.user_data['waiting_for'] = None
    
    await update.message.reply_text(
        "🏠 **主菜单**\n\n请选择一个功能：",
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )


async def todo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick access to todolist"""
    await update.message.reply_text(
        "📝 **待办事项管理**\n\n选择一个操作：",
        parse_mode='Markdown',
        reply_markup=get_todo_menu_keyboard()
    )


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick access to AI chat"""
    if not openai_client:
        await update.message.reply_text(
            "❌ AI功能未配置。请设置OPENAI_API_KEY环境变量。"
        )
    else:
        context.user_data['ai_mode'] = True
        context.user_data['image_mode'] = False
        await update.message.reply_text(
            "🤖 **AI聊天模式**\n\n请发送消息，我会用AI回复你。\n使用 /menu 返回主菜单。"
        )


async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick access to image generation"""
    if not openai_client:
        await update.message.reply_text(
            "❌ 图片生成功能未配置。请设置OPENAI_API_KEY环境变量。"
        )
    else:
        context.user_data['image_mode'] = True
        context.user_data['ai_mode'] = False
        await update.message.reply_text(
            "🎨 **图片生成模式**\n\n请发送图片描述，我会为你生成图片。\n使用 /menu 返回主菜单。"
        )


def main():
    """Start the bot"""
    # Get bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("错误: 请在.env文件中设置TELEGRAM_BOT_TOKEN")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("todo", todo_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("image", image_command))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(todo_handler, pattern="^todo_"))
    application.add_handler(CallbackQueryHandler(todo_handler, pattern="^complete_"))
    application.add_handler(CallbackQueryHandler(todo_handler, pattern="^delete_"))
    
    # Add message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # Start the bot
    logger.info("Bot started successfully!")
    print("机器人启动成功！按 Ctrl+C 停止。")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
