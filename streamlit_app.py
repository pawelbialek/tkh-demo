
import os
os.system("playwright install")

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
    process = CrawlerProcess(settings={
        "FEEDS": {
            "tkh_jobs.csv": {"format": "csv", "overwrite": True},
        },
        "USER_AGENT": "Mozilla/5.0 (compatible; StreamlitBot/1.0)",
        "LOG_LEVEL": "INFO",
        "LOGSTATS_INTERVAL": 10,
    })

    process.crawl(TkhAllSpider)
    process.start()       # blocks inside this process only
    process.stop()

st.title("🕷️ TKH Jobs Spider Launcher")

if st.button("🚀 Run tkh jobs spider", type="primary"):
    with st.spinner("Spider is running in background... please wait"):
        # Run spider in separate process → no Twisted conflict
        p = multiprocessing.Process(target=run_spider)
        p.start()
        p.join()          # wait for it to finish (blocks Streamlit until done)

    st.success("✅ Spider finished!")
    st.balloons()

    if os.path.exists("tkh_jobs.csv"):
        with open("tkh_jobs.csv", "rb") as f:
            st.download_button(
                "📥 Download tkh_jobs.csv",
                f,
                file_name="tkh_jobs.csv",
                mime="text/csv"
            )
    else:
        st.warning("No results.json was created — check your spider's ITEM_PIPELINES")
