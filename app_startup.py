# app_startup.py
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"])
