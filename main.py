import pandas as pd
import os
from openai import OpenAI
import time

# Excel file 
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
        # Update token counters
        total_prompt_tokens += response.usage.prompt_tokens
        total_completion_tokens += response.usage.completion_tokens
        print(f"\n Prompt {i+1} GPT Response:\n{answer}\n")
        results.append({"Prompt": prompt, "GPT Response": answer})
        time.sleep(1.5)  # Safe delay to avoid hitting the rate limit
    except Exception as e:
        print(f" Error occurred (Prompt {i+1}): {e}")
        results.append({"Prompt": prompt, "GPT Response": f"ERROR: {e}"})

def save_results_to_excel(results, filename="GPT_Responses_Iteration1.xlsx"):
    try:
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)
        print(f"\n Results saved to Excel file: {filename}")
    except Exception as e:
        print(f"\n Error saving results to Excel: {e}")

save_results_to_excel(results)

# Calculate total tokens and estimated cost
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


