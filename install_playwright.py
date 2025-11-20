# install_playwright.py
import os
import subprocess
import sys

print("Installing Playwright browsers...")
subprocess.run(["playwright", "install", "--with-deps", "chromium"], check=True)
