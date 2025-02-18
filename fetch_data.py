import os
import requests
import pandas as pd
import datetime

# Use GitHub Secrets for API Token
API_TOKEN = os.getenv("API_TOKEN")
header = {'Authorization': f'Token {API_TOKEN}'}

# Define path for saving yearly data
DATA_DIR = "yearly_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Get current year
current_year = datetime.datetime.now().year
start_time = f"{current_year}-01-01T00:00:00"
end_time = f"{current_year}-12-31T23:59:59"

# Fetch data and save
def fetch_and_store_yearly_data():
    api_df = pd.DataFrame()
    customer_ids = [...]  # Replace with real IDs

    for customer_id in customer_ids:
        if str(customer_id).lower() != 'nan':
            url = f"https://api.steama.co/customers/{customer_id}/utilities/1/usage/?start_time={start_time}&end_time={end_time}"
            response = requests.get(url, headers=header)

            if response.status_code == 200:
                temp_df = pd.DataFrame(response.json())
                temp_df['customer_id'] = customer_id
                api_df = pd.concat([api_df, temp_df], ignore_index=True)

    file_path = os.path.join(DATA_DIR, f"yearly_data_{current_year}.csv")
    api_df.to_csv(file_path, index=False)
    print(f"Yearly data for {current_year} saved to {file_path}")

# Run the function
fetch_and_store_yearly_data()
