#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
咸鱼AI客服系统 - 快速启动脚本
简化版启动工具，快速启动管理界面
"""

import os
import sys
import subprocess

def main():
    print("🐟 咸鱼AI客服系统 - 快速启动")
    print("=" * 50)
    print()
    print("选择启动模式:")
    print("1. 启动命令行管理工具 (推荐)")
    print("2. 直接启动Web界面")
    print("3. 直接运行main.py")
    print("0. 退出")
    print()
    
    while True:
        try:
            choice = input("请选择 (0-3): ").strip()
            
            if choice == "1":
                print("\n🚀 启动命令行管理工具...")
                subprocess.run([sys.executable, "manager.py"])
                break
                
            elif choice == "2":
                print("\n🚀 启动Web界面...")
                print("Web界面将在 http://127.0.0.1:5000 启动")
                subprocess.run([sys.executable, "web_app.py"])
                break
                
            elif choice == "3":
                print("\n🚀 直接运行main.py...")
                subprocess.run([sys.executable, "main.py"])
                break
                
            elif choice == "0":
                print("\n👋 退出程序")
                break
                
            else:
                print("❌ 无效选择，请输入 0-3")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出程序")
            break
        except Exception as e:
            print(f"\n❌ 启动失败: {str(e)}")
            break

if __name__ == "__main__":
    main() 