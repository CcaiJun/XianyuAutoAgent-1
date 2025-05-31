"""
咸鱼AI客服系统 - main.py日志配置建议

为了让Web前端能够显示实时日志，建议在main.py中添加文件日志输出：
"""

from loguru import logger
import sys
import os

# 在main.py的if __name__ == '__main__':部分替换现有的logger配置

if __name__ == '__main__':
    # 加载环境变量
    load_dotenv()
    
    # 配置日志级别
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logger.remove()  # 移除默认handler
    
    # 添加控制台输出（保持原有功能）
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 🔥 添加文件输出（Web前端需要）
    logger.add(
        "logs/xianyu_agent.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",      # 文件大小超过10MB时轮转
        retention="7 days",    # 保留7天的日志
        compression="zip",     # 压缩旧日志
        encoding="utf-8"
    )
    
    logger.info(f"日志级别设置为: {log_level}")
    logger.info("🌐 Web前端可访问: http://localhost:8080")
    
    # 其余代码保持不变...
