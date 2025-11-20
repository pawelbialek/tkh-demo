# streamlit_app.py   ← MUST be this exact name
import streamlit as st

st.title("My Scrapy Spider Launcher")   # ← this will now appear

st.write("If you can see this text, everything is working!")

if st.button("Test button"):
