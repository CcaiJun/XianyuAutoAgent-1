#!/usr/bin/env python3
"""
咸鱼AI客服系统 - Web前端启动脚本

简化的启动脚本，用于快速启动Web管理界面
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """
    主函数 - 启动Web服务
    """
    print("=" * 60)
    print("🐟 咸鱼AI客服系统 - Web管理界面")
    print("=" * 60)
    print("📋 功能: 实时日志监控")
    print("🌐 技术: Flask + WebSocket + 原生HTML")
    print("=" * 60)
    
    try:
        # 导入并启动Web应用
        from app import main as start_web_app
        start_web_app()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请先安装依赖: pip install -r requirements_web.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中止程序")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 