#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
咸鱼AI客服系统 - 命令行管理工具
功能：Web应用管理、状态查看、数字选择菜单
"""

import os
import sys
import time
import signal
import psutil
import requests
import subprocess
from datetime import datetime

# 配置参数
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
WEB_URL = f"http://{WEB_HOST}:{WEB_PORT}"

class WebAppManager:
    """Web应用管理器"""
    
    def __init__(self):
        self.web_process = None
        self.web_pid_file = "web_app.pid"
    
    def start_web_app(self):
        """启动Web应用"""
        if self.is_web_running():
            print("🟡 Web应用已在运行中")
            return False
        
        try:
            print("🚀 正在启动Web应用...")
            
            # 启动web应用进程
            self.web_process = subprocess.Popen(
                [sys.executable, "web_app.py", "--host", WEB_HOST, "--port", str(WEB_PORT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd()
            )
            
            # 保存PID到文件
            with open(self.web_pid_file, "w") as f:
                f.write(str(self.web_process.pid))
            
            # 等待服务启动
            print("⏳ 等待服务启动...")
            for i in range(30):  # 最多等待30秒
                time.sleep(1)
                if self.check_web_health():
                    print(f"✅ Web应用启动成功！")
                    print(f"📱 访问地址: {WEB_URL}")
                    print(f"🔧 进程PID: {self.web_process.pid}")
                    return True
                print(f"   等待中... ({i+1}/30)")
            
            print("❌ Web应用启动超时")
            self.stop_web_app()
            return False
            
        except Exception as e:
            print(f"❌ 启动Web应用失败: {str(e)}")
            return False
    
    def stop_web_app(self):
        """停止Web应用"""
        try:
            # 尝试从PID文件获取进程ID
            pid = None
            if os.path.exists(self.web_pid_file):
                try:
                    with open(self.web_pid_file, "r") as f:
                        pid = int(f.read().strip())
                except (ValueError, IOError):
                    pass
            
            # 如果有当前进程实例
            if self.web_process and self.web_process.poll() is None:
                pid = self.web_process.pid
            
            if pid:
                try:
                    # 尝试优雅停止
                    process = psutil.Process(pid)
                    process.terminate()
                    
                    # 等待进程结束
                    for _ in range(10):
                        if not process.is_running():
                            break
                        time.sleep(0.5)
                    
                    # 如果还在运行，强制杀死
                    if process.is_running():
                        process.kill()
                        time.sleep(1)
                    
                    print("✅ Web应用已停止")
                    
                except psutil.NoSuchProcess:
                    print("✅ Web应用已停止")
                except Exception as e:
                    print(f"⚠️  停止Web应用时出现问题: {str(e)}")
            else:
                print("🟡 Web应用未在运行")
            
            # 清理PID文件
            if os.path.exists(self.web_pid_file):
                os.remove(self.web_pid_file)
            
            self.web_process = None
            return True
            
        except Exception as e:
            print(f"❌ 停止Web应用失败: {str(e)}")
            return False
    
    def is_web_running(self):
        """检查Web应用是否在运行"""
        # 检查PID文件
        if os.path.exists(self.web_pid_file):
            try:
                with open(self.web_pid_file, "r") as f:
                    pid = int(f.read().strip())
                
                # 检查进程是否存在
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    if process.is_running():
                        return True
                
                # PID文件存在但进程不存在，清理文件
                os.remove(self.web_pid_file)
                
            except (ValueError, IOError, psutil.NoSuchProcess):
                # 清理无效的PID文件
                if os.path.exists(self.web_pid_file):
                    os.remove(self.web_pid_file)
        
        # 检查当前进程实例
        if self.web_process and self.web_process.poll() is None:
            return True
        
        return False
    
    def check_web_health(self):
        """检查Web应用健康状态"""
        try:
            response = requests.get(f"{WEB_URL}/api/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_web_status(self):
        """获取Web应用详细状态"""
        if not self.is_web_running():
            return {
                "status": "stopped",
                "pid": None,
                "url": WEB_URL,
                "health": False
            }
        
        try:
            # 获取PID
            pid = None
            if os.path.exists(self.web_pid_file):
                try:
                    with open(self.web_pid_file, "r") as f:
                        pid = int(f.read().strip())
                except:
                    pass
            
            if not pid and self.web_process:
                pid = self.web_process.pid
            
            # 检查健康状态
            health = self.check_web_health()
            
            # 获取进程信息
            cpu_percent = None
            memory_mb = None
            
            if pid:
                try:
                    process = psutil.Process(pid)
                    cpu_percent = round(process.cpu_percent(), 1)
                    memory_mb = round(process.memory_info().rss / 1024 / 1024, 1)
                except:
                    pass
            
            return {
                "status": "running",
                "pid": pid,
                "url": WEB_URL,
                "health": health,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb
            }
            
        except Exception as e:
            return {
                "status": "error",
                "pid": None,
                "url": WEB_URL,
                "health": False,
                "error": str(e)
            }
    
    def get_main_status(self):
        """获取main.py进程状态"""
        try:
            if not self.check_web_health():
                return {"status": "web_offline", "message": "Web应用未运行"}
            
            response = requests.get(f"{WEB_URL}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {})
            
            return {"status": "unknown", "message": "无法获取状态"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


def print_header():
    """打印程序头部信息"""
    print("=" * 60)
    print("🐟 咸鱼AI客服系统 - 管理工具")
    print("=" * 60)


def print_status(manager):
    """打印系统状态"""
    print("\n📊 系统状态:")
    print("-" * 40)
    
    # Web应用状态
    web_status = manager.get_web_status()
    print(f"🌐 Web应用状态: ", end="")
    
    if web_status["status"] == "running":
        if web_status["health"]:
            print(f"🟢 运行中 (PID: {web_status['pid']})")
        else:
            print(f"🟡 启动中 (PID: {web_status['pid']})")
        
        if web_status.get("cpu_percent") is not None:
            print(f"   💻 CPU: {web_status['cpu_percent']}%")
        if web_status.get("memory_mb") is not None:
            print(f"   🧠 内存: {web_status['memory_mb']} MB")
        print(f"   🔗 访问地址: {web_status['url']}")
        
    elif web_status["status"] == "stopped":
        print("🔴 已停止")
    else:
        print(f"❌ 错误: {web_status.get('error', '未知错误')}")
    
    # main.py进程状态
    main_status = manager.get_main_status()
    print(f"🤖 AI客服进程: ", end="")
    
    if main_status.get("status") == "running":
        print(f"🟢 运行中 (PID: {main_status.get('pid')})")
        if main_status.get("running_time"):
            print(f"   ⏱️  运行时间: {main_status['running_time']}")
        if main_status.get("cpu_percent") is not None:
            print(f"   💻 CPU: {main_status['cpu_percent']}%")
        if main_status.get("memory_mb") is not None:
            print(f"   🧠 内存: {main_status['memory_mb']} MB")
            
    elif main_status.get("status") == "stopped":
        print("🔴 已停止")
    elif main_status.get("status") == "starting":
        print("🟡 启动中...")
    elif main_status.get("status") == "stopping":
        print("🟡 停止中...")
    elif main_status.get("status") == "web_offline":
        print("⚠️  Web应用离线")
    else:
        print(f"❌ {main_status.get('message', '状态未知')}")


def print_menu():
    """打印操作菜单"""
    print("\n🎛️  操作菜单:")
    print("-" * 40)
    print("1. 启动Web应用")
    print("2. 停止Web应用")
    print("3. 重启Web应用")
    print("4. 查看系统状态")
    print("5. 打开Web界面")
    print("0. 退出程序")
    print("-" * 40)


def open_web_browser(url):
    """打开Web浏览器"""
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"✅ 已尝试打开浏览器: {url}")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {str(e)}")
        print(f"请手动访问: {url}")


def main():
    """主函数"""
    manager = WebAppManager()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print("\n\n🛑 收到停止信号，正在清理...")
        if manager.is_web_running():
            print("停止Web应用...")
            manager.stop_web_app()
        print("👋 再见！")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            print_header()
            print_status(manager)
            print_menu()
            
            try:
                choice = input("\n请输入选项编号 (0-5): ").strip()
                
                if choice == "1":
                    print("\n🚀 启动Web应用...")
                    if manager.start_web_app():
                        print("✅ 启动成功！")
                    else:
                        print("❌ 启动失败！")
                
                elif choice == "2":
                    print("\n🛑 停止Web应用...")
                    if manager.stop_web_app():
                        print("✅ 停止成功！")
                    else:
                        print("❌ 停止失败！")
                
                elif choice == "3":
                    print("\n🔄 重启Web应用...")
                    print("停止当前应用...")
                    manager.stop_web_app()
                    time.sleep(2)
                    print("启动新应用...")
                    if manager.start_web_app():
                        print("✅ 重启成功！")
                    else:
                        print("❌ 重启失败！")
                
                elif choice == "4":
                    print("\n🔄 刷新状态...")
                    time.sleep(1)  # 给用户一个刷新的感觉
                    continue
                
                elif choice == "5":
                    if manager.is_web_running() and manager.check_web_health():
                        open_web_browser(WEB_URL)
                    else:
                        print("❌ Web应用未运行或不健康，请先启动Web应用")
                
                elif choice == "0":
                    print("\n👋 退出程序...")
                    if manager.is_web_running():
                        user_input = input("检测到Web应用正在运行，是否停止? (y/N): ").strip().lower()
                        if user_input in ["y", "yes", "是"]:
                            print("停止Web应用...")
                            manager.stop_web_app()
                    print("再见！")
                    break
                
                else:
                    print("❌ 无效选项，请输入 0-5 之间的数字")
                
                # 暂停一下让用户看到结果
                if choice != "4":
                    input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n🛑 用户中断...")
                break
            except Exception as e:
                print(f"\n❌ 操作出错: {str(e)}")
                input("按回车键继续...")
    
    finally:
        # 清理资源
        if manager.is_web_running():
            print("清理Web应用...")
            manager.stop_web_app()


if __name__ == "__main__":
    main() 