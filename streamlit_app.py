# streamlit_app.py
import streamlit as st
import os
import subprocess
import sys

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# ONE-TIME PLAYWRIGHT CHROMIUM INSTALL — WORKS ON STREAMLIT CLOUD NOV 2025
browser_path = os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome")
if not os.path.exists(browser_path):
    with st.spinner("First run after deploy — downloading Chromium browser only (~150 MB, 30–90 seconds)..."):
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            st.error("Playwright install failed:")
            st.code(result.stderr)
            st.stop()
        else:
            st.success("Chromium browser installed successfully! Your spider is ready.")
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# streamlit_app.py
import streamlit as st
import os
import multiprocessing
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# <<< CRITICAL: Tell Scrapy where your settings are >>>
os.environ['SCRAPY_SETTINGS_MODULE'] = 'tkh_jobs_playwright/scrapy.cfg'

# Import your spider class
from tkh_jobs_playwright.tkh_jobs_playwright.spiders.tkh_all_clean import TkhAllSpider  # ← change only if class name differs

def run_spider():
    """This function runs in a separate process — no reactor conflict"""
    process = CrawlerProcess(settings={
        "FEEDS": {
            "results.json": {"format": "json", "overwrite": True},
        },
        "USER_AGENT": "Mozilla/5.0 (compatible; StreamlitBot/1.0)",
        # Add any other settings you need here
        # e.g. "DOWNLOAD_HANDLERS": {"http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler", ...}
    })

    process.crawl(TkhAllSpider)
    process.start()       # blocks inside this process only
    process.stop()

st.title("🕷️ TKH Jobs Spider Launcher")

if st.button("🚀 Run tkh_all_clean spider (this may take 2–10 min)", type="primary"):
    with st.spinner("Spider is running in background... please wait"):
        # Run spider in separate process → no Twisted conflict
        p = multiprocessing.Process(target=run_spider)
        p.start()
        p.join()          # wait for it to finish (blocks Streamlit until done)

    st.success("✅ Spider finished!")
    st.balloons()

    if os.path.exists("results.json"):
        with open("results.json", "rb") as f:
            st.download_button(
                "📥 Download results.json",
                f,
                file_name="tkh_jobs_latest.json",
                mime="application/json"
            )
    else:
        st.warning("No results.json was created — check your spider's ITEM_PIPELINES")
