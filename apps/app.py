import streamlit as st

st.set_page_config(page_title="Cecilia - The Cuban Language Model", page_icon="logo.png")
st.logo("logo.png", size="large")

with open("README.md", "r") as f:
    readme_content = f.read()

st.markdown(readme_content)
