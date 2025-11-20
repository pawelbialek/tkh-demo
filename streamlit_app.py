# streamlit_app.py
import streamlit as st
import time
import os

# better_run_spider.py
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spider_blocking():
    process = CrawlerProcess(get_project_settings())
    
    # Replace 'tkh_all_clean' with your spider name
    process.crawl('tkh_all_clean')
    process.start()  # This blocks until spider finishes


st.title("My Scrapy Spider Launcher")

if st.button("Run Spider (Pure Python)"):
    with st.spinner("Spider is running..."):
        run_spider_blocking()
    st.success("Done!")