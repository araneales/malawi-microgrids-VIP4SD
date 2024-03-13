# This script will generate a '8760' file for the prevoius year.
import requests
import pandas as pd 
from datetime import date, timedelta

def get_all_load(customer_id):
    '''This function will return the hourly load for a given customer as a pandas df.'''
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}
    start = date.today()-timedelta(days=365)#).strftime("%Y-%m-%d")
    print("Customer ID: ", customer_id)
    while start < date.today():
        end = start+timedelta(days=41)
        if end > date.today():
            end = date.today()
        url = "https://api.steama.co/customers/"+str(customer_id)+"/utilities/1/usage/?start_time="+start.strftime("%Y-%m-%d")+"&end_time="+end.strftime("%Y-%m-%d")
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

def get_all_customers(site_name):
    '''This function will return all the customer ids for a given site as a list. Note that the site name is used, not the site id.'''
    header = {'Authorization': 'Token d0ff229d5c086264c96e7e6e5541d8266eed90e4'}
    url = "https://api.steama.co/customers/?site=" + site_name
    res_users = []
    bus_users = []
    ins_users = []
    while url:
        print("Get:" + url)
        r = requests.get(url=url, headers = header)
        if r.status_code == 200:
            r_dict = r.json()
            url = r_dict['next']
            for i in r_dict['results']:
                if i['user_type'] == 'RES':
                    res_users.append(i['id'])
                elif i['user_type'] == 'BUS':
                    bus_users.append(i['id'])
                elif i['user_type'] == 'INS':
                    ins_users.append(i['id'])
        else:
            print("Request error: ", r.status_code)
    return res_users, bus_users, ins_users

def create_column(user_list):
    '''This function will create a column for the 8760 using the user list.'''
    for user in user_list:
        if "df" in locals():
            df = df.append(get_all_load(user))
        else:
            df = get_all_load(user)
    return df.groupby('timestamp').sum()

def create_8760(site_name):
    '''This function will create the 8760 file for the site.'''
    res_users, bus_users, ins_users = get_all_customers(site_name)
    res_column = create_column(res_users)
    res_column.rename(columns={'usage': 'res'}, inplace=True)
    bus_column = create_column(bus_users)
    bus_column.rename(columns={'usage': 'bus'}, inplace=True)
    ins_column = create_column(ins_users)
    ins_column.rename(columns={'usage': 'ins'}, inplace=True)
    merged_df = pd.merge(res_column, bus_column, on='timestamp', how='outer')
    merged_df = pd.merge(merged_df, ins_column, on='timestamp', how='outer')
    file_name = site_name + "_8760.csv"
    merged_df.to_csv(file_name, sep=',', encoding='utf-8')

def get_site(sites):
    '''This function will return the site name for the 8760 file.'''
    print("Available sites: ", sites)
    site = input("Enter the site name: ")
    if site in sites:
        return site
    else:
        print("Invalid site name.")
        return get_site(sites)
    
sites = ["Kudembe", "Mthembanji"] # A list of all the available sites

def main():
    create_8760(get_site(sites))

if __name__ == "__main__":
    main()