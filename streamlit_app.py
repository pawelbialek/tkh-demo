# streamlit_app.py
import streamlit as st
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# <<< VERY IMPORTANT: Tell Scrapy where your project actually is >>>
os.environ['SCRAPY_SETTINGS_MODULE'] = 'tkh_jobs_playwright/scrapy.cfg'

# Import your spider class directly (this is the most reliable way)
from tkh_jobs_playwright.spiders.tkh_all_clean import TkhAllCleanSpider
#                                                ^^^^^^^^^^^^^^^^^^^^
#                                                Change only if your class name is different
#                                                (open the file — it's the class that inherits from Spider)

st.title("🕷️ TKH Jobs Spider Launcher")

if st.button("🚀 Run tkh_all_clean spider", type="primary"):
    with st.spinner("Spider is crawling... this may take 2–10 minutes"):
        # Create process with the correct settings
        process = CrawlerProcess(settings={
            "FEEDS": {
                "results.json": {"format": "json", "overwrite": True},
            },
            "USER_AGENT": "Mozilla/5.0 (compatible; StreamlitBot/1.0)",
            # Add any other settings you need from your settings.py
        })

        process.crawl(TkhAllCleanSpider)   # ← pass the CLASS, not the string name
        process.start()                    # blocks until finished

    st.success("✅ Spider finished successfully!")
    st.balloons()

    # Offer download if file exists
    if os.path.exists("results.json"):
        with open("results.json", "rb") as f:
            st.download_button(
                "📥 Download results.json",
                f,
                file_name="tkh_jobs_latest.json",
                mime="application/json"
            )
    else:
        st.warning("No output file was created (check spider pipelines)")