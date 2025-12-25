#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Telegram Bot
Tests the bot structure and functionality without actual API calls
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all necessary modules can be imported"""
    print("Testing imports...")
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler
        print("✅ Telegram imports successful")
    except ImportError as e:
        print(f"❌ Telegram import failed: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ OpenAI import successful")
    except ImportError:
        print("⚠️ OpenAI not available (optional)")
    
    return True


def test_bot_structure():
    """Test bot.py structure and classes"""
    print("\nTesting bot structure...")
    
    # Import without running
    import bot
    
    # Check TodoList class
    if not hasattr(bot, 'TodoList'):
        print("❌ TodoList class not found")
        return False
    print("✅ TodoList class found")
    
    # Check handler functions
    required_handlers = [
        'start', 'menu_handler', 'todo_handler', 
        'handle_message', 'menu_command', 'main'
    ]
    
    for handler in required_handlers:
        if not hasattr(bot, handler):
            print(f"❌ Handler '{handler}' not found")
            return False
    print(f"✅ All {len(required_handlers)} handlers found")
    
    return True


def test_todolist_functionality():
    """Test TodoList class functionality"""
    print("\nTesting TodoList functionality...")
    
    import bot
    
    # Create a test TodoList instance
    test_user_id = 999999999
    todo = bot.TodoList(test_user_id)
    
    # Test adding task
    task_id = todo.add_task("测试任务")
    if task_id != 1:
        print(f"❌ Add task failed: expected ID 1, got {task_id}")
        return False
    print("✅ Add task successful")
    
    # Test getting tasks
    tasks = todo.get_tasks()
    if len(tasks) != 1:
        print(f"❌ Get tasks failed: expected 1 task, got {len(tasks)}")
        return False
    print("✅ Get tasks successful")
    
    # Test completing task
    if not todo.complete_task(task_id):
        print("❌ Complete task failed")
        return False
    print("✅ Complete task successful")
    
    # Test task is marked as completed
    all_tasks = todo.get_tasks(include_completed=True)
    if not all_tasks[0]['completed']:
        print("❌ Task not marked as completed")
        return False
    print("✅ Task marked as completed")
    
    # Test deleting task
    if not todo.delete_task(task_id):
        print("❌ Delete task failed")
        return False
    print("✅ Delete task successful")
    
    # Test ID collision prevention
    # Add multiple tasks, delete middle one, add another
    id1 = todo.add_task("任务1")
    id2 = todo.add_task("任务2")
    id3 = todo.add_task("任务3")
    
    # Delete middle task
    todo.delete_task(id2)
    
    # Add new task - should get ID 4, not ID 3
    id4 = todo.add_task("任务4")
    if id4 <= id3:
        print(f"❌ ID collision: expected ID > {id3}, got {id4}")
        return False
    print("✅ ID collision prevention working")
    
    # Cleanup test file
    if os.path.exists(todo.filename):
        os.remove(todo.filename)
        print("✅ Test file cleaned up")
    
    return True


def test_menu_keyboards():
    """Test menu keyboard creation"""
    print("\nTesting menu keyboards...")
    
    import bot
    
    # Test main menu
    main_menu = bot.get_main_menu_keyboard()
    if not main_menu:
        print("❌ Main menu keyboard failed")
        return False
    print("✅ Main menu keyboard created")
    
    # Test todo menu
    todo_menu = bot.get_todo_menu_keyboard()
    if not todo_menu:
        print("❌ Todo menu keyboard failed")
        return False
    print("✅ Todo menu keyboard created")
    
    return True


def test_configuration():
    """Test configuration file"""
    print("\nTesting configuration...")
    
    # Check .env.example exists
    if not os.path.exists('.env.example'):
        print("❌ .env.example not found")
        return False
    print("✅ .env.example found")
    
    # Check required variables in example
    with open('.env.example', 'r') as f:
        content = f.read()
        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
        for var in required_vars:
            if var not in content:
                print(f"❌ {var} not in .env.example")
                return False
    print("✅ All required variables in .env.example")
    
    return True


def test_files_structure():
    """Test project files structure"""
    print("\nTesting project structure...")
    
    required_files = [
        'bot.py',
        'requirements.txt',
        'README.md',
        '.env.example',
        '.gitignore',
        'start.sh',
        'telegram-bot.service'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file '{file}' not found")
            return False
    print(f"✅ All {len(required_files)} required files found")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Telegram Bot Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Bot Structure Test", test_bot_structure),
        ("TodoList Functionality Test", test_todolist_functionality),
        ("Menu Keyboards Test", test_menu_keyboards),
        ("Configuration Test", test_configuration),
        ("Files Structure Test", test_files_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
