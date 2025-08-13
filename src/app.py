# Adapter entry to delegate to the root-level app.py
# This keeps backward compatibility if someone runs: streamlit run src/app.py
import os
import sys

# Add project root to Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import and run the main app
try:
    from app import main
    main()
except ImportError as e:
    import streamlit as st
    st.error(f"无法导入主应用: {e}")
    st.info("请确保根目录的 app.py 文件存在且可访问")