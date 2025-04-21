import pandas as pd
import os
import time
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

def run_gpt_analysis(df, tested_party_description, filename="GPT_Responses_Output.xlsx"):
    # Function to scrape website content
    def scrape_website_text(url):
        try:
            if not url.startswith("http"):
                url = "http://" + url
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return f" Unable to retrieve content from website: {url}"
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text[:1000]  # Token-safe length
        except Exception as e:
            return f" Error accessing website: {url} – {str(e)}"

    # Prompt creation
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

    # Initialize API
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    total_prompt_tokens = 0
    total_completion_tokens = 0
    results = []

    # GPT Call
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

    # Save results
    try:
        result_df = pd.DataFrame(results)
        result_df.to_excel(filename, index=False)
        print(f"\n Results saved to Excel file: {filename}")
    except Exception as e:
        print(f"\n Error saving results to Excel: {e}")

    # Token Summary
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

    return results[:3]  # First few results for preview in UI if needed

if __name__ == "__main__":
    df = pd.read_excel("Example BM Study - potential comparables 3rd iteration.xlsx")
    tested_party_description = (
        "A Netherlands-based procurement and logistics service provider in the medical industry, "
        "functioning as a limited-risk entity. Its core functions include coordinating shipments, "
        "handling local storage, and overseeing delivery processes in Africa."
    )
    run_gpt_analysis(df, tested_party_description)
