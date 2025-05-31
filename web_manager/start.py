#!/usr/bin/env python3
"""
XianyuAutoAgent Web管理界面启动脚本

一键启动前后端服务的便捷脚本，自动检查依赖、安装缺失的包，
并同时启动FastAPI后端和Vue.js前端服务。

功能特性：
- 自动环境检查
- 依赖安装检测
- 并发启动服务
- 优雅关闭处理

Author: AI Assistant
Created: 2024-01-XX
Version: 1.0.0
"""

import os
import sys
import subprocess
import signal
import threading
import time
from pathlib import Path
from typing import List, Optional


class WebManagerLauncher:
    """Web管理界面启动器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.backend_dir = self.script_dir / "backend"
        self.frontend_dir = self.script_dir / "frontend"
        
        # 进程列表
        self.processes: List[subprocess.Popen] = []
        self.running = False
        
    def check_requirements(self) -> bool:
        """
        检查运行环境和依赖
        
        Returns:
            bool: 环境检查是否通过
        """
        print("🔍 检查运行环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
            print("   需要Python 3.8或更高版本")
            return False
        
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"✅ Node.js版本: {node_version}")
            else:
                print("❌ Node.js未安装，请先安装Node.js 16+")
                return False
        except FileNotFoundError:
            print("❌ Node.js未安装，请先安装Node.js 16+")
            return False
        
        # 检查npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"✅ npm版本: {npm_version}")
            else:
                print("❌ npm未安装")
                return False
        except FileNotFoundError:
            print("❌ npm未安装")
            return False
        
        return True
    
    def install_backend_deps(self) -> bool:
        """
        安装后端依赖
        
        Returns:
            bool: 安装是否成功
        """
        print("\n📦 检查后端依赖...")
        
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt文件不存在")
            return False
        
        try:
            # 检查是否已安装FastAPI
            result = subprocess.run([sys.executable, '-c', 'import fastapi'], 
                                  capture_output=True)
            if result.returncode == 0:
                print("✅ 后端依赖已安装")
                return True
            
            print("📥 安装后端依赖...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], cwd=self.backend_dir)
            
            if result.returncode == 0:
                print("✅ 后端依赖安装成功")
                return True
            else:
                print("❌ 后端依赖安装失败")
                return False
                
        except Exception as e:
            print(f"❌ 安装后端依赖时出错: {e}")
            return False
    
    def install_frontend_deps(self) -> bool:
        """
        安装前端依赖
        
        Returns:
            bool: 安装是否成功
        """
        print("\n📦 检查前端依赖...")
        
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ package.json文件不存在")
            return False
        
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            print("✅ 前端依赖已安装")
            return True
        
        try:
            print("📥 安装前端依赖...")
            result = subprocess.run(['npm', 'install'], cwd=self.frontend_dir)
            
            if result.returncode == 0:
                print("✅ 前端依赖安装成功")
                return True
            else:
                print("❌ 前端依赖安装失败")
                return False
                
        except Exception as e:
            print(f"❌ 安装前端依赖时出错: {e}")
            return False
    
    def start_backend(self) -> Optional[subprocess.Popen]:
        """
        启动后端服务
        
        Returns:
            Optional[subprocess.Popen]: 后端进程对象
        """
        print("\n🚀 启动后端服务...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'app.py'
            ], cwd=self.backend_dir)
            
            # 等待服务启动
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ 后端服务启动成功 (http://localhost:8000)")
                return process
            else:
                print("❌ 后端服务启动失败")
                return None
                
        except Exception as e:
            print(f"❌ 启动后端服务时出错: {e}")
            return None
    
    def start_frontend(self) -> Optional[subprocess.Popen]:
        """
        启动前端服务
        
        Returns:
            Optional[subprocess.Popen]: 前端进程对象
        """
        print("\n🚀 启动前端服务...")
        
        try:
            process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], cwd=self.frontend_dir)
            
            # 等待服务启动
            time.sleep(5)
            
            if process.poll() is None:
                print("✅ 前端服务启动成功 (http://localhost:3000)")
                return process
            else:
                print("❌ 前端服务启动失败")
                return None
                
        except Exception as e:
            print(f"❌ 启动前端服务时出错: {e}")
            return None
    
    def setup_signal_handlers(self):
        """设置信号处理器，用于优雅关闭"""
        def signal_handler(signum, frame):
            print(f"\n\n🛑 接收到信号 {signum}，正在优雅关闭服务...")
            self.stop_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop_services(self):
        """停止所有服务"""
        print("🛑 正在停止服务...")
        
        self.running = False
        
        for process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"停止进程时出错: {e}")
        
        print("✅ 所有服务已停止")
    
    def monitor_processes(self):
        """监控进程状态"""
        while self.running:
            time.sleep(5)
            
            for i, process in enumerate(self.processes):
                if process.poll() is not None:
                    service_name = "后端服务" if i == 0 else "前端服务"
                    print(f"⚠️ {service_name}意外退出，返回码: {process.returncode}")
                    self.running = False
                    break
    
    def run(self):
        """主运行函数"""
        print("=" * 50)
        print("🎯 XianyuAutoAgent Web管理界面启动器")
        print("=" * 50)
        
        # 检查环境
        if not self.check_requirements():
            print("\n❌ 环境检查失败，请解决上述问题后重试")
            return False
        
        # 安装依赖
        if not self.install_backend_deps():
            print("\n❌ 后端依赖安装失败")
            return False
        
        if not self.install_frontend_deps():
            print("\n❌ 前端依赖安装失败")
            return False
        
        # 设置信号处理
        self.setup_signal_handlers()
        
        # 启动服务
        backend_process = self.start_backend()
        if not backend_process:
            return False
        
        frontend_process = self.start_frontend()
        if not frontend_process:
            backend_process.terminate()
            return False
        
        self.processes = [backend_process, frontend_process]
        self.running = True
        
        print("\n" + "=" * 50)
        print("🎉 所有服务启动成功！")
        print("📊 管理界面: http://localhost:3000")
        print("📋 API文档: http://localhost:8000/docs")
        print("💡 按 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 启动进程监控
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        try:
            # 主线程等待
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_services()
        
        return True


def main():
    """主函数"""
    launcher = WebManagerLauncher()
    success = launcher.run()
    
    if not success:
        print("\n❌ 启动失败")
        sys.exit(1)
    else:
        print("\n✅ 程序正常退出")
        sys.exit(0)


if __name__ == "__main__":
    main() 