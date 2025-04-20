import pandas as pd

# Assuming the Excel file is directly in your project root directory
excel_file = 'Example BM Study - potential comparables 1st iteration.xlsx'

# Read the Excel file

df = pd.read_excel(excel_file)

# Fixed tested party explanation 
tested_party_description = (
    "A Netherlands-based procurement and logistics service provider in the medical industry, "
    "functioning as a limited-risk entity. Its core functions include coordinating shipments, "
    "handling local storage, and overseeing delivery processes in Africa."
)

# Prompt creation for first 15 potantial comparable companies
prompts = []
for idx, row in df.iterrows():
    company = row["Company Name"]
    country = row["Country"]
    sic = row["Primary US SIC"]
    description = row["Business Descriptions"]

    prompt = f"""
Tested Party:
{tested_party_description}

Company Under Review:
Name: {company}
Country: {country}
Industry: {sic}
Description: {description}

Question:
Based on the business description and the tested party’s functions, is this company comparable for transfer pricing purposes? 
Please answer with "Comparable" or "Not Comparable", and explain your reasoning briefly.
"""
    prompts.append(prompt)

# Show first 3 prompts in the console as confirmation
for i, p in enumerate(prompts[:3], 1):
    print(f"\n--- Prompt {i} ---\n{p}\n")

# Show how many prompts are created in total
print(f"\nTotal prompts created: {len(prompts)}")

import os
from openai import OpenAI

# Get API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Send a simple test message
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print("GPT Response:\n", response.choices[0].message.content)

