import pandas as pd
import requests
import io
from datetime import datetime, timedelta

# Load your Excel file
df_businesslist = pd.read_excel("Businesslist1.xlsx", converters={'customer_id': str})

# Business types to extract
business_types = [
    {'label': 'Grocery Shop', 'value': 'grocery_shop'},
    {'label': 'Barber Shop', 'value': 'barber_shop'},
    {'label': 'Bar', 'value': 'bar'},
    {'label': 'Video Show', 'value': 'video_show'},
    {'label': 'Street food vendor', 'value': 'street_food_vendor'},
    {'label': 'Restaurant', 'value': 'restaurant'},
    {'label': 'Tailor', 'value': 'tailor'},
    {'label': 'Wood/metal shop', 'value': 'wood/metal_workshop'},
    {'label': 'Phone charging', 'value': 'phone_charging'},
    {'label': 'Other', 'value': 'Other'},
]

# Token and date range
token = "91b021f1dad23ed3967fd7b3fcee130f4859f8fe"
start_date = "2024-04-02"
end_date = "2024-12-31"
header = {'Authorization': f'Token {token}'}

# Split date range into intervals
def split_date_range(start, end, days=30):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    ranges = []
    while start < end:
        chunk_end = min(start + timedelta(days=days), end)
        ranges.append((start.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        start = chunk_end + timedelta(days=1)
    return ranges

date_intervals = split_date_range(start_date, end_date)
real_data_df = pd.DataFrame()

# Collect data via API
for biz in business_types:
    col = biz['value']
    label = biz['label']
    if col in df_businesslist.columns:
        filtered_df = df_businesslist[df_businesslist[col].str.contains("yes", na=False)]
        for interval_start, interval_end in date_intervals:
            for cust_id in filtered_df["customer_id"]:
                if pd.notna(cust_id):
                    url = f"https://api.steama.co/customers/{cust_id}/utilities/1/usage/?start_time={interval_start}&end_time={interval_end}"
                    try:
                        response = requests.get(url, headers=header)
                        if response.status_code == 200:
                            temp_df = pd.read_json(io.BytesIO(response.content))
                            temp_df["customer_id"] = cust_id
                            temp_df["business_type"] = label
                            real_data_df = pd.concat([real_data_df, temp_df], ignore_index=True)
                            print(f"{cust_id} [{label}] from {interval_start} to {interval_end} ✓")
                        else:
                            print(f"⚠️ Failed for {cust_id}: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Error for {cust_id}: {e}")

# Save to Excel
# Remove timezone info from timestamp
real_data_df['timestamp'] = pd.to_datetime(real_data_df['timestamp']).dt.tz_localize(None)

# Save to Excel
real_data_df.to_excel("real_usage_data_apr_to_dec_2024.xlsx", index=False)

print("✅ Data saved to 'real_usage_data_apr_to_dec_2024.xlsx'")
