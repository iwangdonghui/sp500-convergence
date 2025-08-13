#!/usr/bin/env python3
"""
启动脚本 - S&P 500 分析工具 Web UI
"""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'numpy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True


def main():
    """主函数"""
    print("🚀 启动 S&P 500 分析工具 Web UI")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    app_path = current_dir / "app.py"
    
    if not app_path.exists():
        print("❌ 找不到 app.py 文件")
        sys.exit(1)
    
    print("✅ 启动 Streamlit 应用...")
    print("🌐 应用将在浏览器中自动打开")
    print("📝 使用 Ctrl+C 停止应用")
    print("-" * 50)
    
    try:
        # 启动 Streamlit 应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
