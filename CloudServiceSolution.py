import pandas as pd
import io
import os # Google cloud storage for excel
from google.cloud import storage 

APP_ROOT = os.path.dirname(os.path.abspath(__file__)) # Find relative root location

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '{0}\mthembanji-microgrid-dashboard-33d3d459c48a.json'.format(APP_ROOT) # Json file to access private credentials
storage_client = storage.Client()
'''
# Create new bucket
bucket_name = 'dashboard_data_bucket'
bucket = storage_client.bucket(bucket_name)
bucket.location = 'US'
bucket = storage_client.create_bucket(bucket)
'''

# Accessing a specific bucket, create new instance
my_bucket = storage_client.get_bucket('dashboard_data_bucket')

# Print bucket detail
print(vars(my_bucket))
'''
# Download the files
def download_file_from_bucket(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        with open(file_path, 'wb') as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        print(e)
        return False

blob = my_bucket.blob('Power.csv')
storage_client.download_blob_to_file(blob)
'''

# download_file_from_bucket('Power.csv',os.getcwd(),my_bucket)


def download_file_from_bucket(blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket("dashboard_data_bucket")
        blob = bucket.blob(blob_name)
        data_bytes = blob.download_as_bytes()
        df = pd.read_csv(io.StringIO(data_bytes.decode('utf-8')))   
        print(df)
        return True
    except Exception as e:
        print(e)
        return False

download_file_from_bucket("Power.csv")
