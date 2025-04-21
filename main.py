import pandas as pd
import os
import time
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Excel file 
excel_file = 'Example BM Study - potential comparables 3rd iteration.xlsx'

# Read the Excel file
df = pd.read_excel(excel_file)


# Fixed tested party explanation 
tested_party_description = (
    "A Netherlands-based procurement and logistics service provider in the medical industry, "
    "functioning as a limited-risk entity. Its core functions include coordinating shipments, "
    "handling local storage, and overseeing delivery processes in Africa."
)

# Function to scrape website content
def scrape_website_text(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url  # Add scheme if missing
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f" Unable to retrieve content from website: {url}"
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:1000]  # Trim to ~1000 characters for token safety
    except Exception as e:
        return f" Error accessing website: {url} – {str(e)}"

# Prompt creation for each company
prompts = []
for idx, row in df.iterrows():
    company = row["Company Name"]
    country = row["Country"]
    sic = row["Primary US SIC"]
    description = row["Business Descriptions"]
    website = row["Website"]
    website_text = scrape_website_text(website)

    prompt = f"""
Tested Party:
{tested_party_description}

Company Under Review:
Name: {company}
Country: {country}
Industry: {sic}
Description: {description}
Website: {website}

Website Content Extracted:
{website_text}

Question:
Based on the business description, website content and the tested party’s functions, is this company comparable for transfer pricing purposes? 
Please answer with "Comparable" or "Not Comparable", and explain your reasoning briefly.
"""
    prompts.append(prompt)

# Show first 3 prompts as confirmation
for i, p in enumerate(prompts[:3], 1):
    print(f"\n--- Prompt {i} ---\n{p}\n")

# Get API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize counters
total_prompt_tokens = 0
total_completion_tokens = 0

# Send prompts to GPT and collect responses
results = []
for i, prompt in enumerate(prompts):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        total_prompt_tokens += response.usage.prompt_tokens
        total_completion_tokens += response.usage.completion_tokens
        print(f"\n Prompt {i+1} GPT Response:\n{answer}\n")
        results.append({"Prompt": prompt, "GPT Response": answer})
        time.sleep(1.5)
    except Exception as e:
        print(f" Error occurred (Prompt {i+1}): {e}")
        results.append({"Prompt": prompt, "GPT Response": f"ERROR: {e}"})

# Save results to Excel
def save_results_to_excel(results, filename="GPT_Responses_Iteration3.xlsx"):
    try:
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)
        print(f"\n Results saved to Excel file: {filename}")
    except Exception as e:
        print(f"\n Error saving results to Excel: {e}")

save_results_to_excel(results)

# Token summary
COST_PER_1K_PROMPT_TOKENS = 0.0015
COST_PER_1K_COMPLETION_TOKENS = 0.002

total_tokens = total_prompt_tokens + total_completion_tokens
estimated_cost = (total_prompt_tokens / 1000) * COST_PER_1K_PROMPT_TOKENS + \
                 (total_completion_tokens / 1000) * COST_PER_1K_COMPLETION_TOKENS

print("\n--- GPT Usage Summary ---")
print(f"Model: gpt-3.5-turbo")
print(f"Total Prompt Tokens: {total_prompt_tokens}")
print(f"Total Completion Tokens: {total_completion_tokens}")
print(f"Total Tokens Used: {total_tokens}")
print(f"Estimated Cost: ${estimated_cost:.4f} USD")
