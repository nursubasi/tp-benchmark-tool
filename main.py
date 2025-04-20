import pandas as pd

# Assuming the Excel file is directly in your project root directory
excel_file = 'Example BM Study - potential comparables 1st iteration.xlsx'

# Load the Excel file
try:
    df = pd.read_excel(excel_file)
    print(df)  # You can process the dataframe as needed
except FileNotFoundError as e:
    print(f"Error: {e}")