import requests
import requests
import pandas as pd 


#function used to get permission to access steamaco APIs
def pre_req_steamaco():
    details={'username':'Ian_Thomson_Student','password':'nnXCprewaU'}
    url = 'https://api.steama.co/get-token/'                  
    r = requests.post(url=url, data=details)
    print(r.text)

#function used to fetch data from steamco APIs
def data_steamaco():
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}        #personalised token
    url = "https://api.steama.co/sites/26385/utilities/1/usage/"        #data that is collected
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)        #stored in a data file
    print(df)       #print data frame to check collected data
    print(header)

#function used to fetch data from steamco APIs over time period
def data_steamaco_time():
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}
    url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=2022-11-02&end_time=2022-11-03"        #data that is collected
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)        #stored in a data file
    print(df)       #print data frame to check collected data

#pre_req_steamaco()
#data_steamaco()
data_steamaco_time()
