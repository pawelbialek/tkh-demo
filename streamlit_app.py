# streamlit_app.py
import os
import sys
import asyncio
import streamlit as st
from threading import Thread

# ───── FIX PATH FOR YOUR EXACT STRUCTURE ─────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "tkh_jobs_playwright")))

from tkh_jobs_playwright.tkh_jobs_playwright.spiders.tkh_all_clean import TkhAllSpider

from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import asyncioreactor

# ───── FORCE ASYNCIO REACTOR (MUST BE FIRST) ─────
try:
    asyncioreactor.install()
except:
    pass

# ───── SESSION STATE ─────
if "progress" not in st.session_state:
    st.session_state.progress = {"items": 0, "pages": 0, "status": "Ready", "running": False}
progress = st.session_state.progress

# ───── ASYNC CRAWL ─────
async def crawl():
    progress.update(items=0, pages=0, status="Launching Playwright...", running=True)

    settings = Settings()
    settings.setmodule("tkh_jobs_playwright.tkh_jobs_playwright.settings")

    overrides = {
        "FEEDS": {"tkh_jobs.csv": {"format": "csv", "overwrite": True}},
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "LOG_LEVEL": "INFO",
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 4,
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_DEFAULT_ARGS": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    }
    for k, v in overrides.items():
        settings.set(k, v, priority="cmdline")

    runner = CrawlerRunner(settings)
    crawler = runner.create_crawler(TkhAllSpider)

    # ───── CORRECT WAY TO READ STATS (FIXED!) ─────
    def update():
        stats = crawler.stats  # This is a dict-like object
        progress["items"] = stats.get("item_scraped_count", 0)
        progress["pages"] = stats.get("response_received_count", 0)
        progress["status"] = f"Scraped {progress['items']} jobs..."

    from twisted.internet import reactor
    def periodic():
        if progress["running"]:
            update()
            reactor.callLater(2, periodic)
    reactor.callLater(2, periodic)

    # Start crawling
    await runner.crawl(crawler)
    update()  # final update

    progress["status"] = "Finished!"
    progress["running"] = False

# ───── BACKGROUND THREAD ─────
def run_spider():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(crawl())
    finally:
        loop.close()

# ───── UI ─────
st.title("TKH Jobs Spider")

if progress["running"]:
    bar = st.progress(0)
    status = st.empty()
    info = st.empty()

    while progress["running"]:
        items = progress["items"]
        pages = max(1, progress["pages"])
        percent = min(99, int(items * 2 + pages * 0.5))

        bar.progress(percent)
        status.text(progress["status"])
        info.text(f"Jobs: {items} • Pages: {pages}")
        st.rerun()

    bar.progress(100)
    st.success("Spider completed successfully!")
    st.balloons()

    if os.path.exists("tkh_jobs.csv"):
        with open("tkh_jobs.csv", "rb") as f:
            st.download_button(
                "Download tkh_jobs.csv",
                f,
                file_name="tkh_jobs.csv",
                mime="text/csv"
            )
    else:
        st.warning("No CSV generated.")

else:
    if st.button("Run Spider", type="primary"):
        Thread(target=run_spider, daemon=True).start()
        st.rerun()