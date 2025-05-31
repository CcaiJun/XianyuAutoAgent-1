#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
咸鱼AI客服系统 - 外部访问启动脚本
支持通过服务器IP地址进行外部访问
"""

import os
import sys
import subprocess

def main():
    print("🐟 咸鱼AI客服系统 - 外部访问启动")
    print("=" * 60)
    print("⚠️  注意：此模式将允许外部通过服务器IP访问Web界面")
    print("🔗 访问地址：http://192.210.183.167:5000")
    print("=" * 60)
    print()
    print("选择启动模式:")
    print("1. 启动Web管理界面 (外部可访问)")
    print("2. 启动命令行管理工具")
    print("3. 直接运行main.py")
    print("0. 退出")
    print()
    
    while True:
        try:
            choice = input("请选择 (0-3): ").strip()
            
            if choice == "1":
                print("\n🚀 启动Web管理界面 (外部可访问)...")
                print("🔗 内网访问: http://127.0.0.1:5000")
                print("🌐 外网访问: http://192.210.183.167:5000")
                print("⚠️  请确保防火墙已开放5000端口")
                print()
                subprocess.run([sys.executable, "web_app.py", "--host", "0.0.0.0", "--port", "5000"])
                break
                
            elif choice == "2":
                print("\n🚀 启动命令行管理工具...")
                subprocess.run([sys.executable, "manager.py"])
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