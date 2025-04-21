import streamlit as st

st.set_page_config(page_title="TP Benchmarking Tool", layout="centered")

st.title("TP Benchmarking Tool")

# Tested party input
tested_party_description = st.text_area("Enter tested party description")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Run button
if st.button("Run GPT Analysis"):
    if not tested_party_description or not uploaded_file:
        st.warning("Please provide both the tested party description and an Excel file.")
    else:
        st.success("Inputs received. Analysis will run here soon...")

# Placeholder for showing prompt results (future)
st.write("Sample GPT responses will appear here...")

