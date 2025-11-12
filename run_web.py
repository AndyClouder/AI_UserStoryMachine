#!/usr/bin/env python3
"""启动 StoryMachine 网页版服务器"""

import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """启动网页服务器"""
    try:
        import uvicorn
        from storymachine.web_simple import app

        print("启动 StoryMachine 网页版服务器...")
        print("服务器地址: http://localhost:8080")
        print("请在浏览器中打开上述地址")
        print("按 Ctrl+C 停止服务器")
        print()

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )

    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖:")
        print("uv sync")
        sys.exit(1)

    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()