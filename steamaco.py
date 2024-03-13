import requests
import requests
import pandas as pd 
from datetime import date, timedelta

#function used to get permission to access steamaco APIs
def pre_req_steamaco():
    details={'username':'Ian_Thomson_Student','password':'nnXCprewaU'}
    url = 'https://api.steama.co/get-token/'                  
    r = requests.post(url=url, data=details)
    print(r.text)

#function used to fetch data from steamco APIs
def data_steamaco(url):
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}        #personalised token
    #url = "https://api.steama.co/sites/26385/utilities/1/usage/"        #data that is collected
    r = requests.get(url=url, headers = header)
    print(r.status_code)
    s = r.content
    df = pd.read_json(s)        #stored in a data file
    print(df)       #print data frame to check collected data
    df.to_csv("df", sep=',', index=False, encoding='utf-8')

#function used to fetch data from steamco APIs over time period
def data_steamaco_time():
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}
    #url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=2022-11-02-01T00:00:00&end_time=2022-11-03-01T00:00:00"        #data that is collected
    url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=2023-02-04&end_time=2023-03-08" 
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)        #stored in a data file
    print(df)       #print data frame to check collected data
    df.to_csv("Mthembanji_all_load_4_2_23-8_3_23", sep=',', index=False, encoding='utf-8')
    url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=2023-02-04&end_time=2023-03-08" 
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)        #stored in a data file
    print(df)       #print data frame to check collected data
    df.to_csv("Kudembe_all_load_4_2_23-8_3_23", sep=',', index=False, encoding='utf-8')

def get_most_recent_load(site_id):
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}
    end = date.today().strftime("%Y-%m-%d")
    start = (date.today()-timedelta(days=41)).strftime("%Y-%m-%d")
    url = "https://api.steama.co/sites/"+site_id+"/utilities/1/usage/?start_time="+start+"&end_time="+end
    print(url)
    r = requests.get(url=url, headers = header)
    if r.status_code == 200:
        s = r.content
        df = pd.read_json(s)        #stored in a data file
        print(df)
    else:
        print("Request error: ", r.status_code)

def get_all_load(site):
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}
    start = date.today()-timedelta(days=369)#).strftime("%Y-%m-%d")
    print(start)
    while start < date.today():
        end = start+timedelta(days=41)
        if end > date.today():
            end = date.today()
        url = "https://api.steama.co/sites/"+site+"/utilities/1/usage/?start_time="+start.strftime("%Y-%m-%d")+"&end_time="+end.strftime("%Y-%m-%d")
        print("Get:" + url)
        r = requests.get(url=url, headers = header)
        if r.status_code == 200:
            if "df" in locals():
                df = df.append(pd.read_json(r.content))
            else:
                df = pd.read_json(r.content)
        else:
            print("Request error: ", r.status_code)
        start = end      
    return df

def save_loads():
    Kudembe_df = get_all_load("26678")
    Kudembe_df.to_csv("Kudembe_all_load_3_2_23-7_2_24", sep=',', index=False, encoding='utf-8')
    print(Kudembe_df['usage'].to_list())
    Mthembanji_df = get_all_load("26385")
    Mthembanji_df.to_csv("Mthembanji_all_load_3_2_23-7_2_24", sep=',', index=False, encoding='utf-8')

def avg_yearly_load(site_id):
    data = get_all_load(site_id)

    # Assuming df is your DataFrame and it has columns 'timestamp' and 'load'
    data['timestamp'] = pd.to_datetime(data['timestamp'])  # Ensure 'timestamp' is in datetime format
    data.set_index('timestamp', inplace=True)  # Set 'timestamp' as the index

    # Group by hour and calculate mean
    average_load = data.groupby(data.index.hour).mean()
    max_load = data.groupby(data.index.hour).max()
    min_load = data.groupby(data.index.hour).min()
    print("Average load")
    print(average_load)
    print("Max load")
    print(max_load)
    print("Min load")
    print(min_load)
    return average_load, max_load, min_load


'''
def update_av_load_graph(start_date_value, end_date_value, site, bttn1, bttn2,is_open):
    
    site=site
    date = str(start_date_value)
    date2=str(end_date_value)
    div=bttn1
    div2 = bttn2
    
    if(div2==1):
        T = "Total"
    else:
        T = "Average User"
    
    #redefining start and end time so that it can be passed through function in correct format
    start_time = str(date)
    end_time = str(date2)
    num = calc_difference_in_days(start_time,end_time)
    
    if (num==0) or (num>400): # TODO This has been changed fro 40
        y_dont_care = []
        x_dont_care = []
        for index in range(1,24):
            y_dont_care.append(0)
            x_dont_care.append(index)
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_dont_care, y=y_dont_care,
                            mode='lines+markers',
                            ))
        
        fig.update_layout(title = "Invalid Input",
                       xaxis_title='Time',
                       yaxis_title='Demand (kWh)')  
        return fig, not is_open
    else:
        pass

    
    #again redefining start and end time to be in correct format for get request
    start_time = str(date) + "-01T00:00:00"
    end_time = str(date2) + "-01T00:00:00"
    
    #request to customer list
    if(site == 1):
        url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=60"
    elif(site == 2):
        url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=50"
            
    r = requests.get(url=url, headers = header)
    s = r.content
    #converting json string to a panda object
    dfC = pd.read_json(io.BytesIO(s))
    
    #declaring arrays to store names (for get requests later)
    cust_fnames_res=[]
    cust_fnames_bus=[]
    cust_fnames_ins=[]
    
    cust_snames_res=[]
    cust_snames_bus=[]
    cust_snames_ins=[]
    
    #seperating customer names based on user category
    for index in range(0,len(dfC)):
                holder = dfC['results'][index]
            #if the user type is res add 1
                if(holder['user_type'] == "RES"):
                    cust_fnames_res.append(holder['first_name'])
                    cust_snames_res.append(holder['last_name'])
                elif(holder['user_type'] == "BUS"):
                    cust_fnames_bus.append(holder['first_name'])
                    cust_snames_bus.append(holder['last_name'])
                else:
                    cust_fnames_ins.append(holder['first_name'])
                    cust_snames_ins.append(holder['last_name'])
    
    #array storing business + institution 
    cust_fnames_bus_ins=cust_fnames_bus+cust_fnames_ins
    cust_snames_bus_ins=cust_snames_bus+cust_snames_ins
    
    all_cust_fnames= cust_fnames_bus_ins+cust_fnames_res
    
    #Initialising arrays - to allow for values to be added rather than appended in for loops
    #Resizing them so that they are right sized depending on user selected range
    total_hourly_usage=[0]*(24*num)
    take_away_usage = [0]*(24*num)
    hourly_usage = [0]*(24*num)
    timestamp = []
    time = [] 
    load_profile = []
    count=0
    

    if (div==1):
        U="All Users"
        count = len(all_cust_fnames)
        if(site == 1):
            url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Mthembanji"
        elif(site == 2):
            url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Kudembe"
        r2 = requests.get(url=url, headers = header)
        s2 = r2.content
        df2 = pd.read_json(io.BytesIO(s2))
                                
        for index in range(0,len(df2['timestamp'])):
            hourly_usage[index] += df2['usage'][index]
    
    elif (div==2):

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"

        U= "Residential Users"
        for index in range(0,len(cust_fnames_bus_ins)):
            first_name=cust_fnames_bus_ins[index]
            surname=cust_snames_bus_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(io.BytesIO(s))
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(io.BytesIO(s2))
            
            if df2.empty:
                continue
            
            count+=1
            
            #This is (business + institutions) usage - to be taken away
            for index in range(0,len(df2['timestamp'])):
                take_away_usage[index] += df2['usage'][index]
                
                
        total_url= "https://api.steama.co/sites/26385/utilities/1/usage/" + "?start_time=" + start_time + "&end_time=" + end_time

            
        r3 = requests.get(url=total_url, headers = header)
        s3 = r3.content
        df3 = pd.read_json(io.BytesIO(s3))
         
        #Filling total usage array          
        for index in range(0,len(df3['timestamp'])):
                        total_hourly_usage[index]+=(df3['usage'][index])
        
        #Now taking away
        for index in range(0,len(df2['timestamp'])):
            if (div2==1):
                hourly_usage[index]=total_hourly_usage[index] - take_away_usage[index]
            else:
                hourly_usage[index]=(total_hourly_usage[index] - take_away_usage[index])/count        
    
    elif (div==3):

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"

        U = "Business Users"
        for index in range(0,len(cust_fnames_bus)):
            first_name=cust_fnames_bus[index]
            surname=cust_snames_bus[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(io.BytesIO(s))
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(io.BytesIO(s2))
            
            if df2.empty:
                continue
            
            count+=1
            
            for index in range(0,len(df2['timestamp'])):
                if (div2==1):
                    hourly_usage[index] += df2['usage'][index]
                else:
                    hourly_usage[index] += df2['usage'][index]/count
    #same method as businesses ^    
    else:

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"

        U= "Institutional Users"         
        for index in range(0,len(cust_fnames_ins)):
            first_name=cust_fnames_ins[index]
            surname=cust_snames_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(io.BytesIO(s))
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(io.BytesIO(s2))
            
            if df2.empty:
                continue
            
            count+=1          
            
            for index in range(0,len(df2['timestamp'])):
                if (div2==1):
                    hourly_usage[index] += df2['usage'][index]
                else:
                    hourly_usage[index] += df2['usage'][index]/count
    
    for index in range(0,len(df2['timestamp'])):
            timestamp.append(str(df2['timestamp'][index]))
            
    for index in range(0,24):
        if(index<10):
            a = "0" + str(index)
        else:
            a = str(index)
        temp = a + ":00:00+00:00"
        amount = 0
        for count in range(0,len(timestamp)):
            holder = timestamp[count]
            if(temp == holder[11:26]):
                amount += float(hourly_usage[count])
                continue
            else:
                continue
        if (div2==1):
            load_profile.append(amount/num)
        else:
            load_profile.append((amount/num)/count)
        time.append(temp[0:8])
    
    
    start_time = str(date)
    end_time = str(date2) #


    title =  T + " Load Profile for " + U + " for: " + start_time + " to " + end_time + " (" + str(site_name) + ")"
    
    FillSpreadSheet(title, "Time", "Demand (kWh)", time, load_profile, "Load_Profile_Range")   
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=time, y=load_profile,
                        mode='lines+markers',
                        ))
            
    fig.update_layout(title = T + " Load Profile for " + U + " for: " + start_time + " to " + end_time + " (" + str(site_name) + ")",
                      xaxis_title='Time',
                      yaxis_title='Demand (kWh)',
                      yaxis_range=[-0.02,max(load_profile)+0.02])
    
    return fig, is_open
 '''   
#pre_req_steamaco()
#data_steamaco()
#data_steamaco_time()
#save_loads()
avg_yearly_load("26678")
#fdata_steamaco("https://api.steama.co/sites/26385/utilities/1/readings/")