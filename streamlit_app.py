# streamlit_app.py
import streamlit as st
from run_spider import run_scrapy_spider
import time
import os

st.title("My Scrapy Spider Launcher")

if st.button("Run Spider (Pure Python)"):
    with st.spinner("Spider is running..."):
        run_spider_blocking()
    st.success("Done!")
