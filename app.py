import streamlit as st
import pandas as pd
from main import run_gpt_analysis

st.set_page_config(page_title="TP Benchmarking Tool", layout="centered")

st.title("TP Benchmarking Tool")

# Tested party input
tested_party_description = st.text_area("Enter tested party description")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

results = []

# Run button
if st.button("Run GPT Analysis"):
    if not tested_party_description or not uploaded_file:
        st.warning("Please provide both the tested party description and an Excel file.")
    else:
        df = pd.read_excel(uploaded_file)
        output_filename = uploaded_file.name.replace(".xlsx", "") + "_GPT_Responses.xlsx"
        results = run_gpt_analysis(df, tested_party_description, filename=output_filename)
        st.success("Analysis completed successfully.")

        # Display first 3 GPT responses (trimmed)
        st.subheader("Sample GPT Responses")
        for i, r in enumerate(results[:3], 1):
            response_text = r["GPT Response"]
            short_response = response_text[:500] + "..." if len(response_text) > 500 else response_text
            st.markdown(f"**Prompt {i}:** {short_response}")

        # Download button
        with open(output_filename, "rb") as f:
            st.download_button("Download Results", data=f, file_name=output_filename)