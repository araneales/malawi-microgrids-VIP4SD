#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu Feb 11 15:53:26 2021
@original author: heatherwaddell
@pre existing author(s): aaron,chris,jack
@current author(s): ian,jamie,adam,ruaridh,

"""
import os # find current file directory
import datetime as datetime
import dash
from dash import dcc as file 
from dash import State
from dash import Dash, dcc, html, Input, Output, dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import plotly.express as px
from datetime import date
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db 
import time
import xlsxwriter
from io import BytesIO


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP],suppress_callback_exceptions=True) 
server = app.server
# CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, MINTY, MORPH, PULSE, QUARTZ, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, VAPOR, YETI, ZEPHYR.
#Original = LUX
#fav = COSMO, ZEPHYR
session=requests.Session()


# Current directory for Flask app
APP_ROOT = os.path.dirname(os.path.abspath(__file__)) # Find relative root location

# Current directory for Flask app + file name
# Use this file_path variable in your code to refer to your file 


#====================TECHINCAL=============================================

def success(status):
       if status == 200 or status == 201:
              return True
       else:
              return False

# STEP 1
STEPONEURL = "https://auth.smaapis.de/oauth2/token"
step1payload = "POST%20sandbox.smaapis.de%2Foauth2%2Ftoken=&HTTP%2F1.1=&Host%3A%20smaapis.de=&Content-Type%3A%20application%2Fx-www-form-urlencoded=&client_id=strathclyde_api&client_secret=1f773505-616b-49a0-a462-5889fa690384&grant_type=client_credentials&scope=offline_access"
headers1 = CaseInsensitiveDict()
headers1["Content-Type"] = "application/x-www-form-urlencoded"

r1 = requests.post(STEPONEURL, data=step1payload,headers=headers1)
# print("\n(STEP ONE) Status Code: {0}. Successful: {1}\n".format(r1.status_code,success(r1.status_code))) (DEBUGGING)
TOKEN = r1.json()['access_token']
# print("{0}\n".format(TOKEN)) # (PRINT TOKEN) (DEBUGGING)

# STEP 2
STEPTWOURL = "https://async-auth.smaapis.de/oauth2/v2/bc-authorize"
headers2 = {'Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
step2payload = {'loginHint':'aaron.shek.2020@uni.strath.ac.uk'}

r2 = requests.post(STEPTWOURL, json=step2payload,headers=headers2) 
# print("\n(STEP TWO) Status Code: {0}. Successful: {1}\n".format(r2.status_code,success(r2.status_code))) (DEBUGGING)
# print(r2.json()) (DEBUGGING)

# STEP 3 - GET DATA VIA API FOR EXAMPLE
r = "https://async-auth.smaapis.de/monitoring/v1/plants"
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}

r = session.get(r,headers=headers2)
#print("\nStatus Code: {0}. Successful: {1}\n".format(r.status_code,success(r.status_code)))
data_initial = r.json()
#print(data_initial) 

#Sunny Portal
def refreshtoken(r1):
       STEPONEURL = "https://auth.smaapis.de/oauth2/token"
       step1payload = "POST%20sandbox.smaapis.de%2Foauth2%2Ftoken=&HTTP%2F1.1=&Host%3A%20smaapis.de=&Content-Type%3A%20application%2Fx-www-form-urlencoded=&client_id=strathclyde_api&client_secret=1f773505-616b-49a0-a462-5889fa690384&grant_type=client_credentials&scope=offline_access"
       headers1 = CaseInsensitiveDict()
       headers1["Content-Type"] = "application/x-www-form-urlencoded"
       r1 = requests.post(STEPONEURL, data=step1payload,headers=headers1)
       STEPONEURL = "https://auth.smaapis.de/oauth2/token"
       step1payload = "POST%20auth.smaapis.de%2Foauth2%2Ftoken=&HTTP%2F1.1=&Host%3A%20smaapis.de=&Content-Type%3A%20application%2Fx-www-form-urlencoded=&client_id=strathclyde_api&client_secret=1f773505-616b-49a0-a462-5889fa690384&grant_type=refresh_token&refresh_token={0}&scope=offline_access".format(r1.json()['refresh_token'])
       headers1 = CaseInsensitiveDict()
       headers1["Content-Type"] = "application/x-www-form-urlencoded"
       r1 = requests.post(STEPONEURL, data=step1payload,headers=headers1)
       TOKEN = r1.json()['access_token']
       STEPTWOURL = "https://async-auth.smaapis.de/oauth2/v2/bc-authorize"
       headers2 = {'Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
       step2payload = {'loginHint':'aaron.shek.2020@uni.strath.ac.uk'}
       r2 = requests.post(STEPTWOURL, json=step2payload,headers=headers2)
       return TOKEN


header = {'Authorization': 'Token 519802b968a55413f26964f53f99787cffaf11ac'}

url_ER = "https://api.steama.co/exchange-rates/?format=json"                   
r = requests.get(url=url_ER, headers = header)
s = r.content
df_ER = pd.read_json(s)##

# Initialising Firebase app as admin 
cred = credentials.Certificate({"type": "service_account",
  "project_id": "openrmu",
  "private_key_id": "0df42dfd548fea43869cd10331f8280ff8c9dfef",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDZzabBUqJsCI9I\nC86u762NNSNAWkcA3cMGUE0xS8nwW9SyTwGv9WiT9hoHi3VgIDyRNXIqF56upYd0\nPzo3i3W1aKFyw4DWjS2D8JebUwAaH8K6ESiScONkZThz3VEoDylnO/qtmNq9e5qd\ndGbo+/SFyR3Dr1CaRBwoRzcdtdaOHNcah4ALy4KnZh18SkEAKeacZHsS9HN418yN\nCcy9bVkexB/XeHT+60hrw4qKzonlrX1pT2v9Han+Yy3tdLQ+SqmLBcpJFvbaDqdZ\nEvKkC104Bs+YTycDwQ7YrM39bylNC6uB2EGtEvexLq0uSBMHBAVJwvWkA5NknsbR\ntDi22g3VAgMBAAECggEAWwgsw81lbHDxbePdeVlcuNG2T53L4m1Np3Rlpw5tsyO2\nlOYXpvMTyA/K1k9v+gLPPcPQWQ5xOL6fjDMnAnMr+evm2sAit8ne9a/XtcgtmT2g\nFkO4qOg86keyHh8o3ezkWa0Ee40RE7Q3LcsqfgNcspQZ+CFst2VzPVRykVzgdZmL\n0FA6SUQulJGDE7EU79eQte4CKUpBbUzLe/SNOUjB02e2UEdcXNfLWS9OyChezToH\ndRJtwAydwrAhO1JSc9Kmc89SGF4hFKkmAsFwoTNw8Xhe7OTqo0s2wl8fiL9TAeMP\nTPSdi8dItgLVCKDHaNnHI9r6CGRL0j11pOhH+ZFEWwKBgQDxgLdH1MRoIjy85gdp\nPmNiegmxTZdmHNrj/Z2Sq0sXcXMVMKpL9tMI1sg4JQxc2DYCy6LxpknyQcwkxjMP\nhqhXHTxvRhmuxJuV+HPSBSgD29Br8UWmZ0Iat2Zi44eiycbsmvEp77iaUtysE8LZ\niTzmSZgmvAuQz7o2yVKnacBw0wKBgQDm4LwdkKMcz/AVzaYC+mJKHoG4/MuQ8gCq\n43h/FT3Urs/C8dtArf+GyM27iQYp4PVIhUXCD3Bp+IILo8uqsCM81w1hib8rNOt9\nMYEeXL77iXGpkAAz7i0l3R21TgAIaQ1vPdIqx0QWtc64m3kd1KpeSk/1oLBPfm+/\nnUIkk4idtwKBgQCt5toTx4qG0eCaxamgh2RZjTddjVnwFecpNX86Fk7EWtVb9Ocs\nPFhKjR8wDr2QPcDm0mxLRksJP4gZEv/Btl2SHWNfXUMxLjI7E+WS3lOqM6cpk1ts\nL/7R7i60FtOczV+JESmH4S81MWXmI3Sz4LcRvPzrJ43MgUi+GsqB8wy4MQKBgH3d\nZrB3eXTrp2c7hZV6Crt9hhrjNdb/F34SJE6jteGMq5cLYwwPz44bSo1CVineidnP\nTghNgmtDHyJZWV7kR1GTq6fRAHb9kqPdqRZ0WWmntF9MMdAduF87/EYrD7mGC9zp\nRvorR+NZmijqGU058ucUfCLcR0IPG7zKbpSiGYhhAoGBANGDW5EotF8aEvtSKyXq\nODmaZdNu8C1LPp8b8e9yZZtjJr+bOa5GzVcycb+Uy+kKuyf+teLMdkPsaGks7SW8\nTg/Hp4hIQO2RansYQcSlmMknHb3GEhQ224P12ybS1KyQF8YbtENd5PmnldmLsmnB\nq/QETElvwzJnSw6Hh7NEirTl\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-q13qo@openrmu.iam.gserviceaccount.com",
  "client_id": "100792905573479873385",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-q13qo%40openrmu.iam.gserviceaccount.com" })

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://openrmu-default-rtdb.europe-west1.firebasedatabase.app'
       })


def FillSpreadSheet(title, header1, header2, array1, array2,filename): ##Function used to fill downloadable spreadsheets
    
    file =filename + ".xlsx"
    workbook = xlsxwriter.Workbook(file, {'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    
    cell_format = workbook.add_format()
    cell_format2 = workbook.add_format()
    
    cell_format.set_bg_color('orange')
    cell_format2.set_bg_color('yellow')
    
    worksheet.write(0,0,title,cell_format)
    worksheet.write(0,1,"",cell_format)
    worksheet.write(0,2,"",cell_format)
    
    
    worksheet.write(1,0,header1, cell_format2)
    worksheet.write(1,1,header2, cell_format2)
    
    worksheet.write_column(2,0,array1)
    worksheet.write_column(2,1,array2)
    workbook.close()

def FillSpreadSheet1(title, header1, header2, header3, header4, header5, array1, array2, array3, array4, array5, filename): ##Used to fill batt temp spreasheets only
    
    file =filename + ".xlsx"
    workbook = xlsxwriter.Workbook(file, {'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    
    cell_format = workbook.add_format()
    cell_format2 = workbook.add_format()
    
    cell_format.set_bg_color('orange')
    cell_format2.set_bg_color('yellow')
    
    worksheet.write(0,0,title,cell_format)
    worksheet.write(0,1,"",cell_format)
    worksheet.write(0,2,"",cell_format)
    worksheet.write(0,3,"",cell_format)
    worksheet.write(0,4,"",cell_format)
    worksheet.write(0,5,"",cell_format)
    
    
    worksheet.write(1,0,header1, cell_format2)
    worksheet.write(1,1,header2, cell_format2)
    worksheet.write(1,2,header3, cell_format2)
    worksheet.write(1,3,header4, cell_format2)
    worksheet.write(1,4,header5, cell_format2)
    
    
    worksheet.write_column(2,0,array1)
    worksheet.write_column(2,1,array2)
    worksheet.write_column(2,2,array3)
    worksheet.write_column(2,3,array4)
    worksheet.write_column(2,4,array5)
    workbook.close()

def FillSpreadSheet2(title, header1, header2, header3, array1, array2, array3, filename): ##Used to fill one Battery SOC spreadhseet only
    
    file =filename + ".xlsx"
    workbook = xlsxwriter.Workbook(file, {'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    
    cell_format = workbook.add_format()
    cell_format2 = workbook.add_format()
    
    cell_format.set_bg_color('orange')
    cell_format2.set_bg_color('yellow')
    
    worksheet.write(0,0,title,cell_format)
    worksheet.write(0,1,"",cell_format)
    worksheet.write(0,2,"",cell_format)
    worksheet.write(0,3,"",cell_format)

    
    
    worksheet.write(1,0,header1, cell_format2)
    worksheet.write(1,1,header2, cell_format2)
    worksheet.write(1,2,header3, cell_format2)

    
    
    worksheet.write_column(2,0,array1)
    worksheet.write_column(2,1,array2)
    worksheet.write_column(2,2,array3)

    workbook.close()


#====================SOCIAL IMPACT=============================================
#......................DATAFRAMES..............................................
# Health and Education # 
df_SmartphoneSatisfaction = pd.read_excel(os.path.join(APP_ROOT, r'AccessToSmartphones.xlsx'))
df_NoSchool = pd.read_excel(os.path.join(APP_ROOT, r'Children_Not_School.xlsx'))
df_StudyingHours = pd.read_excel(os.path.join(APP_ROOT, r'StudyingHours.xlsx'))
df_HealthInfo = pd.read_excel(os.path.join(APP_ROOT, r'HealthInformationSource.xlsx'))

# Employment and Finance # 
df_Finances = pd.read_excel(os.path.join(APP_ROOT, r'Monthly_Finances.xlsx'))
df_Income = pd.read_excel(os.path.join(APP_ROOT, r'Monthly_Income.xlsx'))
df_FinancialSecurity = pd.read_excel(os.path.join(APP_ROOT, r'Financial_Security.xlsx'))
df_business_month = pd.read_excel(os.path.join(APP_ROOT, r'Businesses_Month.xlsx'))

# Energy Access #
df_EnergySources = pd.read_excel(os.path.join(APP_ROOT, r'Electricity_Source.xlsx'))
df_EnergySatisfaction = pd.read_excel(os.path.join(APP_ROOT, r'Energy_Satisfaction.xlsx'))
df_Appliances = pd.read_excel(os.path.join(APP_ROOT, r'Household_Appliances.xlsx'))
df_LightSource = pd.read_excel(os.path.join(APP_ROOT, r'Lighting_Source.xlsx'))

# Tarif and Services #
df_CostSatisfaction = pd.read_excel(os.path.join(APP_ROOT, r'Cost_Satisfaction.xlsx'))
df_PaymentMethod = pd.read_excel(os.path.join(APP_ROOT, r'PaymentMethod_Satisfaction.xlsx'))
df_satisfaction = pd.read_excel(os.path.join(APP_ROOT, r'Recommendation_Likelihood.xlsx'))

# Women Empowerment #
df_WomenFreetime = pd.read_excel(os.path.join(APP_ROOT, r'Womens_Freetime.xlsx'))
df_WomenIndependance = pd.read_excel(os.path.join(APP_ROOT, r'Women_Independance.xlsx'))
df_WomenRespectHOME = pd.read_excel(os.path.join(APP_ROOT, r'Respect_Household.xlsx'))
df_WomenRespectCOMM = pd.read_excel(os.path.join(APP_ROOT, r'Respect_Community.xlsx'))
df_HomeSecurity = pd.read_excel(os.path.join(APP_ROOT, r'HouseholdSecurity.xlsx'))
#......................FUNCTIONS...............................................
# Health and Education #
def funct_StudyingHours(df):
    survey = df['Survey']
    avg_hours = df['Avg_Hours']
    fig_StudyingHours = px.bar(
        df,
        title = 'Average Number of Hours Spent Studying in the Home',
        x = survey,
        y = avg_hours,)
    return fig_StudyingHours

def funct_NoSchool(df):
    children   = df['Number of Children']
    survey     = df['Survey']
    fig_NoSchool = px.bar(
        df,
        title = 'Number of Children not in School',
        x = survey,
        y = children)
    return fig_NoSchool

def funct_SmartphoneSatisfaction(df):
    survey  = df['Survey']
    v_unhap = df['Very Unhappy']
    q_unhap = df['Quite Unhappy']
    neutral = df['Neutral']
    q_hap   = df['Quite Happy']
    v_hap   = df['Very Happy']
    
    fig_SmartPhoneSatisfaction = px.bar(
        df,
        title = 'Payment Method Satisfaction',
        x = survey,
        y = [v_unhap,q_unhap,neutral,q_hap,v_hap],
        color_discrete_map = {
            'Very Unhappy':'red',
            'Quite Unhappy':'orange',
            'Neutral':'yellow',
            'Quite Happy':'limegreen',
            'Very Happy':'green'},
        range_y = [0,55],)
    return fig_SmartPhoneSatisfaction

def funct_HealthInfo(df): 
    sources    = df['Health Information Source']
    households = df['Households']
    survey     = df['Survey']

    fig_HealthInfo = px.bar(
        df,
        title = 'Main Source for Accessing Health Information (Number of Households)',
        x = sources,
        y = households,
        animation_frame = survey,
        animation_group = sources,
        range_y = [0,55])
    return fig_HealthInfo

# Employment and Finance #
def funct_Finances(df):
    finances  = df['Average Monthly (MWK)']
    limit   = df['Range']
    survey  = df['Survey']
    fig_Income = px.line(
        df,
        title = 'Monthly Income and Expenditure (MWK)',
        x = survey,
        y = finances,
        color = limit,)
    return fig_Income

def funct_Income(df):
    income = df['Monthly Income (MWK)']
    limit  = df['Range']
    survey = df['Survey']
    fig_incomex = px.line(
        df,
        x = survey,
        y = income,
        color = limit,)
    return fig_incomex

def funct_FinancialSecurity(df):
    survey     = df['Survey']
    v_insecure = df['Very Insecure']
    q_insecure = df['Quite Insecure']
    neutral    = df['Neutral']
    q_secure   = df['Quite Secure']
    v_secure   = df['Very Secure']
    fig_FinancialSecurity = px.bar(
        df,
        title = 'Household Financial Security',
        x = survey,
        y = [v_insecure,q_insecure,neutral,q_secure,v_secure],
        color_discrete_map = {
            'Very Insecure':'red',
            'Quite Insecure':'orange',
            'Neutral':'yellow',
            'Quite Secure':'limegreen',
            'Very Secure':'green'},
        range_y = [0,55],)
    return fig_FinancialSecurity

def funct_Business_Month(df):
    date = df['Date']
    num_business = df['Number of Businesses']
    fig_BusinessMonth = px.line(
        df,
        title = 'Number of Businesses VS. Months After Microgrid Installation',
        x = date,
        y = num_business,)
    return fig_BusinessMonth

# Energy Access #
def funct_EnergySources(df): 
    sources    = df['Source']
    households = df['Households']
    survey     = df['Survey']

    fig_sources = px.bar(
        df_EnergySources,
        title = 'Source of Electricity Used (Household)',
        x = sources,
        y = households,
        animation_frame = survey,
        animation_group = sources,
        range_y = [0,55])
    return fig_sources

def funct_EnergySatisfaction(df):
    survey  = df['Survey']
    v_unhap = df['Very Unhappy']
    q_unhap = df['Quite Unhappy']
    neutral = df['Neutral']
    q_hap   = df['Quite Happy']
    v_hap   = df['Very Happy']

    fig_EnergySatisfaction = px.bar(
        df,
        title = 'Enegrgy Access Satisfaction',
        x = survey,
        y = [v_unhap,q_unhap,neutral,q_hap,v_hap],
        color_discrete_map = {
            'Very Unhappy':'red',
            'Quite Unhappy':'orange',
            'Neutral':'yellow',
            'Quite Happy':'limegreen',
            'Very Happy':'green'},
        range_y = [0,55],)
    return fig_EnergySatisfaction

def funct_Appliances(df): 
    appliance    = df['Appliance']
    households = df['Households']
    survey     = df['Survey']

    fig_app = px.bar(
        df,
        title = 'Appliances used in the Household',
        x = appliance,
        y = households,
        animation_frame = survey,
        animation_group = appliance,
        range_y = [0,55])
    return fig_app

def funct_LightSource(df):
    light_sources = df['Light Source']
    households    = df['Households']
    survey        = df['Survey']

    fig_LightSources = px.bar(
        df,
        title = 'Light Sources used in the Household',
        x = light_sources,
        y = households,
        animation_frame = survey,
        animation_group = light_sources,
        range_y = [0,55])
    return fig_LightSources

# Tariff and Services #
def funct_CostSatisfaction(df):
    survey  = df['Survey']
    v_unhap = df['Very Unhappy']
    q_unhap = df['Quite Unhappy']
    neutral = df['Neutral']
    q_hap   = df['Quite Happy']
    v_hap   = df['Very Happy']
    
    fig_satisfaction = px.bar(
        df,
        title = 'Tariff Pricing Satisfaction',
        x = survey,
        y = [v_unhap,q_unhap,neutral,q_hap,v_hap],
        color_discrete_map = {
            'Very Unhappy':'red',
            'Quite Unhappy':'orange',
            'Neutral':'yellow',
            'Quite Happy':'limegreen',
            'Very Happy':'green'},
        range_y = [0,55],)
    return fig_satisfaction
        
def funct_PaymentMethod(df):
    survey  = df['Survey']
    v_unhap = df['Very Unhappy']
    q_unhap = df['Quite Unhappy']
    neutral = df['Neutral']
    q_hap   = df['Quite Happy']
    v_hap   = df['Very Happy']
    
    fig_PaymentMethod = px.bar(
        df,
        title = 'Payment Method Satisfaction',
        x = survey,
        y = [v_unhap,q_unhap,neutral,q_hap,v_hap],
        color_discrete_map = {
            'Very Unhappy':'red',
            'Quite Unhappy':'orange',
            'Neutral':'yellow',
            'Quite Happy':'limegreen',
            'Very Happy':'green'},
        range_y = [0,55],)
    return fig_PaymentMethod

def funct_Recommendation(df):
    survey  = df['Survey']
    v_unhap = df['Very Unlikely']
    q_unhap = df['Unlikely']
    neutral = df['May Recommend']
    q_hap   = df['Likely']
    v_hap   = df['Very Likely']

    fig_Recommendation = px.bar(
        df,
        title = 'Microgrid Recommendation Likelihood',
        x = survey,
        y = [v_unhap,q_unhap,neutral,q_hap,v_hap],
        color_discrete_map = {
            'Very Unlikely':'red',
            'Unlikely':'orange',
            'May Recommend':'yellow',
            'Likely':'limegreen',
            'Very Likely':'green'},
        range_y = [0,55],)
    return fig_Recommendation
    
# Women Empowerment #
def funct_WomenFreetime(df):
    similar   = df['Remained Similar']
    sw_increased = df['Somewhat Increased']
    vm_increased = df['Very Much Increased']
    survey    = df['Survey']

    fig_WomenFreetime = px.bar(
        df,
        title = "Ammount of Freetime (Number of Women)",
        x = survey,
        y = [vm_increased,sw_increased, similar], 
        range_y = [0,28])
    
    return fig_WomenFreetime

def funct_WomenIndependance(df):
    similar   = df['Remained Similar']
    sw_increased = df['Somewhat Increased']
    vm_increased = df['Very Much Increased']
    survey    = df['Survey']

    fig_WomenIndependance = px.bar(
        df,
        title = "Independance and Decision Making Power (Number of Females)",
        x = survey,
        y = [vm_increased,sw_increased, similar], 
        range_y = [0,28])
    
    return fig_WomenIndependance

def funct_WomenRespectHOME(df):
    similar   = df['Remained Similar']
    sw_increased = df['Somewhat Increased']
    vm_increased = df['Very Much Increased']
    survey    = df['Survey']

    fig_WomenRespectHOME = px.bar(
        df,
        title = "Respect Within the Household (Number of Females)",
        x = survey,
        y = [vm_increased,sw_increased, similar], 
        range_y = [0,28])
    
    return fig_WomenRespectHOME

def funct_WomenRespectCOMM(df):
    similar   = df['Remained Similar']
    sw_increased = df['Somewhat Increased']
    vm_increased = df['Very Much Increased']   
    survey    = df['Survey']

    fig_WomenRespectCOMM = px.bar(
        df,
        title = "Respect Within the Community (Number of Females)",
        x = survey,
        y = [vm_increased,sw_increased, similar], 
        range_y = [0,28])
    
    return fig_WomenRespectCOMM

def funct_HomeSecurity(df):
    similar   = df['Remained Similar']
    sw_increased = df['Somewhat Increased']
    vm_increased = df['Very Much Increased']
    survey    = df['Survey']

    fig_HomeSecurity = px.bar(
        df,
        title = "Security in the Home (Number of Females)",
        x = survey,
        y = [vm_increased,sw_increased, similar], 
        range_y = [0,28])
    
    return fig_HomeSecurity
#.......................FIGURES................................................
# Health and Education #
fig_StudyingHours = funct_StudyingHours(df_StudyingHours)
fig_StudyingHours.update_layout(title = "Average Number of Hours Spent Studying in the Home (Weekly)",
               xaxis_title='Survey',
               yaxis_title='Average Number of Hours Studying per Week (Hours)') 

fig_NoSchool = funct_NoSchool(df_NoSchool)
fig_NoSchool.update_layout(title = "Number of School Aged Children not in Education",
               xaxis_title='Survey',
               yaxis_title='Number of Children') 

fig_SmartPhoneSatisfaction = funct_SmartphoneSatisfaction(df_SmartphoneSatisfaction)
fig_SmartPhoneSatisfaction.update_layout(title = "Satisfaction of Access to Smartphones",
               xaxis_title='Survey',
               yaxis_title='Number of Households') 

fig_HealthInfo = funct_HealthInfo(df_HealthInfo)
fig_HealthInfo.update_layout(title = "Main Source for Accessing Health Information (Number of Households)",
               xaxis_title='Survey',
               yaxis_title='Number of Households') 

# Employment and Finance #
fig_Finances = funct_Finances(df_Finances)
fig_Finances.update_layout(title = "Average Monthly Income and Expenditure",
               xaxis_title='Survey',
               yaxis_title='Monthly Income and Expenditure (MWK)') 

fig_Income = funct_Income(df_Income)
fig_Income.update_layout(title = "Monthly Income, Highest and Lowest Average (MWK)",
               xaxis_title = 'Survey',
               yaxis_title = 'Monthly Income (MWK)')

fig_FinancialSecurity = funct_FinancialSecurity(df_FinancialSecurity)
fig_FinancialSecurity.update_layout(title = "Household Financial Security",
               xaxis_title='Survey',
               yaxis_title='Number of Households')

fig_BusinessMonth = funct_Business_Month(df_business_month)
fig_BusinessMonth.update_layout(title = "Number of Businesses VS. Months After Microgrid Installation",
               xaxis_title='Month and Year',
               yaxis_title='Number of Businesses') 

# Energy Access #
fig_EnergySources = funct_EnergySources(df_EnergySources)
fig_EnergySources.update_layout(title = "Household Source of Electricity Used",
               xaxis_title='Source',
               yaxis_title='Number of Households') 

fig_EnergySatisfaction = funct_EnergySatisfaction(df_EnergySatisfaction)
fig_EnergySatisfaction.update_layout(title = "Household Energy Access Satisfaction",
               xaxis_title='Survey',
               yaxis_title='Number of Households') 

fig_Appliances = funct_Appliances(df_Appliances)
fig_Appliances.update_layout(title = "Appliances in the Household",
               xaxis_title='Survey',
               yaxis_title='Appliance') 

fig_LightSources = funct_LightSource(df_LightSource)
fig_LightSources.update_layout(title = "Household Light Source",
               xaxis_title='Survey',
               yaxis_title='Light Source') 

# Tariff and Services #
fig_CostSatisfaction = funct_CostSatisfaction(df_CostSatisfaction)
fig_CostSatisfaction.update_layout(title = "Tariff Pricing Satisfaction",
               xaxis_title='Survey',
               yaxis_title='Number of Households') 

fig_PaymentMethod = funct_PaymentMethod(df_PaymentMethod)
fig_PaymentMethod.update_layout(title = "Payment Method Satisfaction",
               xaxis_title='Survey',
               yaxis_title='Number of Households') 

fig_Recommendation = funct_Recommendation(df_satisfaction)
fig_Recommendation.update_layout(title = "Microgrid Recommendation Liklihood",
               xaxis_title='Survey',
               yaxis_title='Number of Households') 

# Women Empowerment #
fig_WomenFreetime = funct_WomenFreetime(df_WomenFreetime)
fig_WomenFreetime.update_layout(title = "Ammount of Free Time",
               xaxis_title='Survey',
               yaxis_title='Number of Females') 

fig_WomenIndependance = funct_WomenIndependance(df_WomenIndependance)
fig_WomenIndependance.update_layout(title = "Independance and Decision Making Power",
               xaxis_title='Survey',
               yaxis_title='Number of Females') 

fig_WomenRespectHOME = funct_WomenRespectHOME(df_WomenRespectHOME)
fig_WomenRespectHOME.update_layout(title = "Respect Within the HOUSEHOLD",
               xaxis_title='Survey',
               yaxis_title='Number of Females') 

fig_WomenRespectCOMM = funct_WomenRespectCOMM(df_WomenRespectCOMM)
fig_WomenRespectCOMM.update_layout(title = "Respect within the COMMUNITY",
               xaxis_title='Survey',
               yaxis_title='Number of Females') 

fig_HomeSecurity = funct_HomeSecurity(df_HomeSecurity)
fig_HomeSecurity.update_layout(title = "Security in the Home",
               xaxis_title='Survey',
               yaxis_title='Number of Females') 
#==============================================================================


for index in range(len(df_ER['rate'])):
    if(df_ER['source'][index]=='MWK' and df_ER['target'][index]=='USD'):
        ER = df_ER['rate'][index]
        break
    else:
        continue
    
today = datetime.datetime.now()
past_date = str(today - datetime.timedelta(days=30))
start_time = past_date[0:10] + "T00:00:00"

C_date = str(today)

C_year = int(C_date[0:4])
C_month = int(C_date[5:7])
C_day = int(C_date[8:10])
     
url = "https://api.steama.co/sites/26385/revenue/" + "?start_time=" + start_time
r = requests.get(url=url, headers = header)
s = r.content
df = pd.read_json(s)

# Request from the first URL
url1 = "https://api.steama.co/sites/26385/revenue/" + "?start_time=" + start_time
r1 = requests.get(url=url1, headers = header)
s1 = r1.content
df1 = pd.read_json(s1)

# Request from the second URL
url2 = "https://api.steama.co/sites/26678/revenue/" + "?start_time=" + start_time
r2 = requests.get(url=url2, headers = header)
s2 = r2.content
df2 = pd.read_json(s2)

# Combine the two datasets
df = pd.concat([df1, df2], ignore_index=True)

if(len(df)==0):
    print("There have been no transactions in the last 30 days.")
else:
    amountMK = 0
    
    for index in range(0,len(df['timestamp'])):
        amountMK += float((df['revenue'][index]))
        
    amountUSD = amountMK*ER
    
y_dont_care = []
x_dont_care = []
for index in range(1,24):
    y_dont_care.append(0)
    x_dont_care.append(index)
    
holder_fig = go.Figure()
holder_fig.add_trace(go.Scatter(x=x_dont_care, y=y_dont_care,
                    mode='lines+markers',
                    ))

holder_fig.update_layout(title = "Holder Graph",
               xaxis_title='Time',
               yaxis_title='Unknown')  

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
     "background-color": "#f2f2f2",
}

CONTENT_STYLE = {
    "margin-left": "17rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H1("Navigation"),

        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact", external_link=True),
                dbc.NavLink("Demand", href="/demand", active="exact", external_link=True),
                dbc.NavLink("Technical", href="/technical", active="exact", external_link=True),
                dbc.NavLink("Social Impact", href="/social", active="exact", external_link=True),
                dbc.NavLink("Maintenance", href="/maintenance", active="exact", external_link=True),
                dbc.NavLink("Learn More", href = "/learnmore", active="exact", external_link=True)
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
        


content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])
# For YYYY-MM inputs
if C_month < 10: # To suit YY/MM format since C_month does not include the 0 in front of singular months i.e 01,03
    currentYYMM = '{0}-0{1}'.format(C_year,C_month) # C_ = Current 
else:
    currentYYMM = '{0}-{1}'.format(C_year,C_month) # Will update on a month by month basis

def displayTotalGeneration():
    TOKEN = refreshtoken(r1)
    rgen = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Total?WithTotal=true"
    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    rgen = session.get(rgen,headers=headers2)
    #print("\nStatus Code: {0}. Successful: {1}\n".format(rgen.status_code,success(rgen.status_code)))
    data_initial = rgen.json()
    #print(data_initial)
    TotalGenerationDisplay = 0
    for value in data_initial['set']:
                TotalGenerationDisplay = (TotalGenerationDisplay + (value['totalGeneration']))
    
    TotalGenerationDisplay = TotalGenerationDisplay/1000000
    return str(round(TotalGenerationDisplay, 2))

def displayTotalConsumption():
    TOKEN = refreshtoken(r1)
    rgen = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Total?WithTotal=true"
    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    rgen = session.get(rgen,headers=headers2)
    #print("\nStatus Code: {0}. Successful: {1}\n".format(rgen.status_code,success(rgen.status_code)))
    data_initial = rgen.json()
    #print(data_initial)
    TotalConsumptionDisplay = 0
    for value in data_initial['set']:
                TotalConsumptionDisplay = (TotalConsumptionDisplay + (value['totalConsumption']))
    
    TotalConsumptionDisplay = TotalConsumptionDisplay/1000000
    return str(round(TotalConsumptionDisplay, 2))    

def displayTotalSavings():
    TOKEN = refreshtoken(r1)
    rgen = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Total?WithTotal=true"
    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    rgen = session.get(rgen,headers=headers2)
    #print("\nStatus Code: {0}. Successful: {1}\n".format(rgen.status_code,success(rgen.status_code)))
    data_initial = rgen.json()
    #print(data_initial)
    TotalGenerationDisplay = 0
    for value in data_initial['set']:
                TotalGenerationDisplay = (TotalGenerationDisplay + (value['totalGeneration']))
    
    TotalGenerationDisplay = TotalGenerationDisplay/1000000
    CarbonSavingsDisplay = TotalGenerationDisplay * 2.4
    return str(round(CarbonSavingsDisplay, 2))
              
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                html.Div(
                children = html.H1("Malawi Microgrid Dashboard"),style={'backgroundColor': '#f2f2f2', 'textAlign': 'center'}),
                html.Div([
                html.Hr(),
                html.Br(),
                html.Img(src='https://i.postimg.cc/fWxCPPXX/view-from-the-top-2.jpg',style={'width':'900px', 'height':'280px'}), 
                ], style={'textAlign': 'center'}),
                html.Hr(),
            
        html.Br(),
        dcc.Tabs(id='home_tabs', value='tab-1', children=[
        dcc.Tab(label='Background Information', value = 'tab-1'),
        dcc.Tab(label='Mthembanji', value = 'tab-2'),
        dcc.Tab(label='Kudembe', value='tab-3'),
        ],),
        html.Div(id='home_content'),]
                 
    elif pathname == "/demand":
        return [
                html.Div(
                children = html.H1("Demand Data"),style={'backgroundColor': '#f2f2f2', 'textAlign': 'center'}),
                html.Hr(),
                html.H3("The total revenue generated for the last 30 days is $" + str(round(amountUSD,2))),
                html.Br(),
                dcc.Tabs(id='tabs-example', value='tab-1', children=[
                dcc.Tab(label='Revenue Data', value='tab-1'),
                dcc.Tab(label='Monthly Demand', value = 'tab-2'),
                dcc.Tab(label='Load Profiles', value='tab-3'),
                dcc.Tab(label='Peak Load Data', value='tab-4'),
                dcc.Tab(label='Connection Status', value='tab-5'),
                dcc.Tab(label='Individual Customer Data', value='tab-6')
                ],),
                html.Div(id='tabs-example-content'),
                ]
    elif pathname == "/technical":
        return [
                html.Div(
                children = html.H1("Technical Data"),style={'backgroundColor': '#f2f2f2', 'textAlign': 'center'}),                          
                html.Hr(),
                html.H3("The total power generated so far is {0} MWh, total consumption is {1} Mwh, and total potential carbon savings is {2} t CO2".format(displayTotalGeneration(),displayTotalConsumption(),displayTotalSavings())),
                html.P("Techincal data relating the to the functionality of the generation and distribution systems, a variety of data on technical performance is being collected through remote monitoring of the PV, batteries and inverters, along with measurements and observations of the system collected through scheduled maintenance visits on site."),
                html.P("All data is currently being drawn in from the SMA Sunny Portal API after an initial OAUTH2 verification process for security so that there is no unauthorised use of the secret token being used elsewhere. "),
                html.Hr(),
                dcc.Tabs(id='technical_tabs_1', value='tab-1', children=[
                dcc.Tab(label='Consumption', value='tab-1'),
                dcc.Tab(label='Generation', value='tab-2'),
                dcc.Tab(label='Battery State of Charge', value='tab-3'),
                dcc.Tab(label='Battery Temperature', value = 'tab-4'),
                dcc.Tab(label='System Downtime', value='tab-5'),
                dcc.Tab(label='System Efficiency', value = 'tab-6'),
                dcc.Tab(label='Carbon Savings', value = 'tab-7')
                ],),
                html.Div(id='technical_tabs_1_content'),
                ]
    elif pathname == "/social":
        return [
                html.Div(
                children = html.H1("Social Impact Data"),style={'backgroundColor': '#f2f2f2', 'textAlign': 'center'}),
                html.Hr(),
                html.P("Social Impact data is the measure of how a product or service changes the lives of the people and community that uses it. The social impact data of the microgrid has been broken down into five categories shown by the tabs below. "),
                html.P("As of February 2022, three Social Impact surveys have been conducted. "),
                html.Li("Baseline: August 2019"),
                html.Strong("Microgrid Installed: July 2020"),
                html.Li("Survey 1: May 2021"),
                html.Li("Survey 2: February 2022"),
                html.Li("Survey 3: (planned) July 2022"),
                       
                html.Br(),
                html.Hr(),
                dcc.Tabs(id='social_tabs', value='tab-1', children=[
                dcc.Tab(label='Energy Access', value='tab-1'), 
                dcc.Tab(label='Tariff and Service', value='tab-2'),                    
                dcc.Tab(label='Health, Education and Communication', value='tab-3'),
                dcc.Tab(label='Employment and Finance', value='tab-4'),
                dcc.Tab(label='Women Empowerment', value='tab-5'),
                ],),              
                html.Div(id='social_tabs_content'),
                ]
    elif pathname == "/maintenance":
        return [
                html.Div(
                children = html.H1("Maintenance"),style={'backgroundColor': '#f2f2f2', 'textAlign': 'center'}),
                html.Hr(),
                html.P("Maintenance is a critical aspect to the longevity of any solar microgrid network, failure to maintain such equipment will guarantee short-term success and failure in the future. Going forward, this dashboard recommends a tab where site manager(s) can upload comments regarding their latest site visit and bring to attention any issues that may have arisen. As well as display their latest maintenance/ repair logs as well and a map. "),
                html.Br(),
                html.P("The SOP-011: Site Visit Maintenance Report is a checklist to be conducted by any UP field managers alongside site agents and/or staff. Download the template below."),
                html.Button("Click to download SOP-011: Site Visit Maintenance Report Template", id="maintenance-file"),
                dcc.Download(id="download-maintenance-file"),
                html.Br(),
                html.Hr(),
                ]
    elif pathname == "/learnmore":
        return [
                html.Div(
                children = html.H1("Learn More"),style={'backgroundColor': '#f2f2f2', 'textAlign': 'center'}),
                html.Hr(),
                html.P("For questions or comments please get in touch - aran.eales@strath.ac.uk"),
                html.P("On this page, you may find useful links where you can learn more about our microgrid in Malawi (part of the EASE project). We have also included links to numerous research articles that are relevant to our project."),
                html.Hr(),
                html.H2("EASE"),
                html.P("Visit the EASE website if you would like to find out more about its outputs & outcomes as well as discover other cool projects similar to ours!"),
                dbc.CardLink("EASE website", href="https://ease.eee.strath.ac.uk/"),
                html.Hr(),
                html.H2("MINI-GRID LINKS"),
                html.P("Please Choose from the list below - you will be redirected to the relevant website"),
                dbc.CardLink("African Minigrid Developers Association", href="https://africamda.org/"),
                html.Br(),
                html.Br(),   
                dbc.CardLink("Regulatory Framework for Minigrids in Malawi", href="https://rise.esmap.org/data/files/library/malawi/Renewable%20Energy/Supporting%20Documentation/Malawi_Mini-Grids%20Framework-Ready%20for%20review%20by%20Ministry%20of%20Justice.pdf"),
                html.Br(),
                html.Br(), 
                dbc.CardLink("Benchmarking Africa’s Minigrids Report 2022", href="https://africamda.org/2022/07/01/benchmarking-africas-minigrids-report-2022-key-findings/"),
                html.Br(),
                html.Br(), 
                dbc.CardLink("Performance Monitoring Of African Micro-Grids: Good Practices and Operational Data", href="https://www.nrel.gov/docs/fy20osti/71767.pdf"),
                html.Br(),
                html.Hr(),
                html.H2("UNIVERSITY OF STRATHCLYDE MICROGRID RESEARCH"), 
                html.P("Please Choose from the list below - you will be redirected to the relevant website"),
                dbc.CardLink("Social Impact of Mini-grids: Monitoring, Evaluation and Learning", href="https://www.researchgate.net/publication/329424742_Social_Impact_of_Mini-grids_Monitoring_Evaluation_and_Learning"),
                html.Br(),
                html.Br(),
                dbc.CardLink("Assessing the market for solar photovoltaic (PV) microgrids in Malawi", href="https://pureportal.strath.ac.uk/en/publications/assessing-the-market-for-solar-photovoltaic-pv-microgrids-in-mala"),
                html.Br(),
                html.Br(),
                dbc.CardLink(" Assessing the feasibility of solar microgrid social enterprises as an appropriate delivery model for achieving SDG7", href="https://pureportal.strath.ac.uk/en/publications/assessing-the-feasibility-of-solar-microgrid-social-enterprises-a"),
                html.Br(),
                html.Br(),
                dbc.CardLink("Feasibility study for a solar PV microgrid in Malawi", href="https://pureportal.strath.ac.uk/en/publications/feasibility-study-for-a-solar-pv-microgrid-in-malawi"),
                html.Br(),
                html.Br(),
                dbc.CardLink("Renewable Energy Mini-grids in Malawi: Status, Barriers and Opportunities", href="https://pureportal.strath.ac.uk/en/publications/feasibility-study-for-a-solar-pv-microgrid-in-malawi"),
                html.Hr(),
                html.P("We hope that these links are of good use to you and that you find what you're looking for. However, please do not hesitate to contact us if you would like more information!"),
                html.Div(id='learnmore'),
                ]           
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
    
@app.callback(
        Output('technical_tabs_1_content', 'children'),
        Input('technical_tabs_1', 'value'))

def render_tech_tabs_1(tab): # ======================================================================================================================= WIP ======================================================= #
    if tab == 'tab-1':
        return html.Div([
                html.Br(),
                html.Hr(),
                html.H2("Consumption"),
                html.H6("Please Select a date (Do not select several months):"),
                dcc.DatePickerRange(
                id='my-date-picker-range-2',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                start_date=date(C_year, C_month-1, 1), # Display previous month days as an example to get started
                end_date=date(C_year, C_month-1, 12) # Changed so it selects current day, previously it was set to June the 5th 2020
                # more user friendly
                ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="consumption-range-file"),
                dcc.Download(id="download-consumption-range-file"),
                dcc.Graph(id = 'my_graph_6', figure = {}),
                html.P("This graph shows the total consumption of the solar microgrid more specifically over a certain range."),
                html.P("This is another key data indicator to track as it shows when the system is being most consumed or when it is at its least used state. Typically trends indicate that the peak usage is around the evening presumably from cooking utilities being under load (social) and steady increase during the mornings. These trends & data can then be extrapolated into the future to allow for maximum efficient use of the solar microgrid as to when to prioritise output power during peak times or not."),
                html.H6("Please Select a Year: "),# New quality of life improvements
                dcc.RadioItems(id = 'slct_user_2',
                options=[
                    {'label': '2022', 'value': 2022},
                    {'label': '2021', 'value': 2021},
                    {'label': '2020', 'value':2020},
                ],
                value=2022,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
                ), 
                html.Br(),
                html.Button("Click to download spreadsheet", id="consumption-year-file"),
                dcc.Download(id="download-consumption-year-file"),
                dcc.Graph(id='my_graph_5_1', figure={}),
                html.P("This graph shows the total consumption over a month-by-month basis."),
                html.P("This is particularly useful as it allows conclusions to be drawn such as when the solar microgrid is under the most consumption, or when it is the least. Please note that there is no data available before July 2020 as that was when the microgrid was installed. "),
                html.Hr(),
                ])                
    elif tab == 'tab-2':
        return html.Div([
                html.Br(),
                html.Hr(),
                html.H2("Total Generation of Microgrid"),
                html.P("Please select a date:"),
                dcc.DatePickerSingle(
                    id='my-date-picker-single-gen',
                    min_date_allowed=date(2020, 6, 5),
                    max_date_allowed=date(C_year, C_month, C_day),
                    initial_visible_month=date(C_year, C_month, C_day),
                    date=date(C_year, C_month, C_day)
            ),  
                html.Br(),
                html.Button("Click to download spreadsheet", id="generation-day-file"),
                dcc.Download(id="download-generation-day-file"),
                dcc.Graph(id='graph_7', figure = {}),
                html.P("This chart displays the total generation (energy balance)."),
                html.P("This key data indicator shows when the system is generating most power, and the least power respectively. As indicitive of this graph, it would suggest the peak generation is around the early mornings of 9am, before levelling off during the day."),           
                html.H6("Please Select a Year: "),# New quality of life improvements
                dcc.RadioItems(id = 'slct_user_3_1',
                options=[
                    {'label': '2022', 'value': 2022},
                    {'label': '2021', 'value': 2021},
                    {'label': '2020', 'value':2020},
                ],
                value=2022,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
                ), 
                html.Br(),
                html.Button("Click to download spreadsheet", id="generation-year-file"),
                dcc.Download(id="download-generation-year-file"),                
                dcc.Graph(id='my_graph_7_1', figure={}),
                html.Hr(),
                ])
    elif tab == 'tab-3':
        return html.Div([ 
                html.Br(),
                html.Hr(),
                html.H2("State of Charge (energy balance)"), 
                html.H6("Please Select a Date (Do not select several months):"),

                dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                start_date=date(C_year, C_month-1, 1), # Display previous month days as an example to get started
                end_date=date(C_year, C_month-1, 12) # Changed so it selects current day, previously it was set to June the 5th 2020
                # more user friendly
                ),
                html.Br(),
                html.Button("Click to download spreadsheet", id="soc-range-file"),
                dcc.Download(id="download-soc-range-file"),
                dcc.Graph(id='my_graph_5', figure={}),

                html.P("This chart displays the current state of charge of the batteries."),
                html.P("This is another key data indicator to track as it allows for one to come to conclusions regarding when the charge of the batteries are charged, or depleted. Again, note the anomolous data display between 23rd to 25th of January. All data is being drawn in from the SMA Sunny Portal API."),
                html.H6("Please Select a Date: "),
                dcc.DatePickerSingle(
                id='my-date-picker-single-charge',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day)
            ),
                html.Br(),
                html.Button("Click to download spreadsheet", id="soc-day-file"),
                dcc.Download(id="download-soc-day-file"),
                dcc.Graph(id='graph_6_1',figure={}),
                html.P("This chart displays the battery state of charge over a given day in increments of 5 minutes (highest possible definition defined by Sunny Portal API)."),
                html.P("This is a very useful graph as it indicates the state of charge of the battery throughout any given day and shows the depletion of the battery as the PV systems are off (during night) and when it is at its peak maximum charge (during afternoons when the solar microgrid is producing power)."),
                html.Br(),
                html.H6("Please Select a Year: "),# New quality of life improvements
                dcc.RadioItems(id = 'slct_user_5',
                options=[
                    {'label': '2022', 'value': 2022},
                    {'label': '2021', 'value': 2021},
                    {'label': '2020', 'value':2020},
                ],
                value=2022,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="soc-year-file"),
                dcc.Download(id="download-soc-year-file"),
                dcc.Graph(id='my_graph_6_2',figure={}),
                html.P("This side-by-side bar chart provides insight into the average state of the batteries charging and discharging per monthly basis, respectively. The data is according to the live reading of the battery counter"),
                html.Hr(),
                ])
    elif tab == 'tab-4':
        return html.Div([
            html.Br(),
            html.Hr(),
            html.H2("Average Battery Temperature Over Given Month"),
            html.H6("Please Select a Month:"),
            dcc.Input(id='my-date-picker-single', type="text", value=currentYYMM, placeholder="YYYY-MM", debounce=True,style={'fontSize':16}),
            html.Br(),
            html.Button("Click to download spreadsheet", id="batt-temp-month-file"),
            dcc.Download(id="download-batt-temp-month-file"),            
            dcc.Graph(id = 'batt_temp_month', figure={}),
            html.P("This graph is used to display the average battery temperature during each day throughout a given month. There are 4 different temperatures being tracked on this graph:"),
            html.P("Battery Temperature - Measured using a probe that is taped to the side of the battery."),
            html.P("External Temperature - Measured using a probe that is outside of the shipping container, under the PV modules."),
            html.P("Internal Temperature - Measured using a probe that is inside the inverter room."),
            html.P("PCB Temperature - Measured using a probe that is taped onto the data logger itself."),
            html.P("It is important to regularly monitor and evaluate battery temperature to ensure that they are cooled efficiently as battery life reduces at higher temperatures. Battery temperature is measured using a data logger which was installed at the beginning of March, 2022. The logger records battery temperature in 10 minute intervals which is then used to calculate daily averages."),
            html.P("During March 2022, some daily averages were calilated to be less than 5 °C which is an error caused by missing data points and is not a true reflection of battery temperature."),
            html.Br(),
            html.Hr(),
            html.H2("Average Battery Temperature Over Given Day"),
            html.H6("Please Select a Date:"),
            dcc.DatePickerSingle(
                id='my-date-picker-single-2',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day) # Changed so it selects current day, previously it was set to June the 5th 2020
                # more user friendly
            ),
            html.Br(),
            html.Button("Click to download spreadsheet", id="batt-temp-day-file"),
            dcc.Download(id="download-batt-temp-day-file"),   
            dcc.Graph(id = 'batt_temp_day', figure={}),
            html.P("This graph is used to display the average battery temperature during each hour throughout a given day."),
            html.P("This indicator allows for battery temperature to be viewed at a higher resolution than the one seen in the indicator above. This is impiortant as it allows us to see how battery temperature varies throughout the hours of the day and identify hourly trends in battery temperature. Identification of these trends could be useful in informing decisions concerning the battery cooling system. ")
            ])  
    elif tab == 'tab-5':
        return html.Div([ 
                html.Br(),
                html.Hr(),
                html.H2("Daily Communications Uptime"), 
                html.H6("Please Select a Year (This is the input for the 3 subsequent indicators) "),
                dcc.Dropdown(id="slct_year",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi=False,
                     value=str(C_year),
                     style={'width': "40%"}
                     ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="daily-uptime-file"),
                dcc.Download(id="download-daily-uptime-file"),
                dcc.Graph(id='daily_communications_uptime', figure = {}),
                html.P("This chart displays daily communications uptime over a given year."),
                html.P("This is another key data indicator to track as it allows for both planned and unplanned outages to be easily identified. The highlighted region of the graph highlights the percentage at which outages are detected (<=50%). A value of 50% was chosen as when the uptime is below tjis value, the system has experienced downtime for the majority of the day and has therefore expereinced an outage. For more information about the duration and start day of outages please see the bar chart below."),
                html.Hr(),
                html.H2("Number of Days an Outage was Detected"),
                html.Br(),
                html.Button("Click to download spreadsheet", id="no-days-outages-file"),
                dcc.Download(id="download-no-days-outages-file"),
                dcc.Graph(id = 'no_days_outages', figure={}),
                html.P("The bar chart above is used to view the number of days throughout each month in which an outage was detected."),
                html.Hr(),
                html.H2("Start Date & Length of Outages"),
                html.Br(),
                html.Button("Click to download spreadsheet", id="start-length-outages-file"),
                dcc.Download(id="download-start-length-outages-file"),
                dcc.Graph(id='daily_outages_bar', figure = {}),
                html.P("The bar chart above builds on the daily communications uptime indicator and can be used to view both the start date as well as the duration of each outage for the year selected. The purple line that has been plotted onto the chart represents the average outage duration for the given year. This is the final indicator which builds on daily communication uptime." ),               
                html.Hr(),
                html.H2("Hourly Communications Uptime"),
                html.H6("Please select start (left) and end (right) date: "),
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(2020, 6, 5),
                    max_date_allowed=date(C_year, C_month, C_day),
                    initial_visible_month=date(C_year, C_month, C_day),
                    start_date=date(C_year, C_month-1, 1), 
                    end_date=date(C_year, C_month-1, 12)
                # more user friendly
                ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="hourly-uptime-file"),
                dcc.Download(id="download-hourly-uptime-file"),
                dcc.Graph(id='hourly_communications_uptime', figure = {}),
                html.P("This chart displays the hourly communications uptime over a selected range."),
                html.P("This is similar to the daily communications uptime indicator, but allows data to be viewed in a higher resolution. This is useful as it allows for data to be observed more closely after using the indicators shown previously on this page.")
                ])
    elif tab == 'tab-6':
        return html.Div([ 
                html.Br(),
                html.Hr(),
                html.H2("Energy Production Efficiency"), 
                html.H6("Please Select a Year : "),
                dcc.Dropdown(id="slct_year",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi=False,
                     value=str(C_year),
                     style={'width': "40%"}
                     ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="generation-efficiency-file"),
                dcc.Download(id="download-generation-efficiency-file"),
                dcc.Graph(id='technical_efficiency', figure = {}),
                html.P("This chart displays the energy production efficiency as a percentage for each month over a given year. This is calculated by taking the total consumption of the grid at the output of the inverter and dividing it by the total amount of energy generated by the Solar PV Panels."),
                html.Br(),
                html.Hr(),
                html.H2("Distribution Efficiency"), 
                html.H6("Please Select a Year : "),
                dcc.Dropdown(id="slct_year2",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi=False,
                     value=str(C_year),
                     style={'width': "40%"}
                     ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="distribution-efficiency-file"),
                dcc.Download(id="download-distribution-efficiency-file"),
                dcc.Graph(id='distribution_efficiency', figure = {}),
                html.P("This chart displays the distribution  efficiency as a percentage for each month over a given year. This is done by taking the amount of demand, measured by smart metres across the village and dividing it by the total consumption of the grid which is measured within the shipping container."),
                html.Br(),
                html.Hr(),
                html.H2("Overall System Efficiency"), 
                html.H6("Please Select a Year : "),
                dcc.Dropdown(id="slct_year3",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi=False,
                     value=str(C_year),
                     style={'width': "40%"}
                     ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="overall-efficiency-file"),
                dcc.Download(id="download-overall-efficiency-file"),
                dcc.Graph(id='overall_efficiency', figure = {}),
                html.P("This chart displays the overall system efficiency as a percentage for each month over a given year. This is done by taking the amount of energy that reaches the end user which is measured using smart metres across the village. This is then divided by the total amount of energy that has been generated by the grid's solar panels."),                
                ])
    elif tab == 'tab-7':
        return html.Div([ 
                html.Br(),
                html.Hr(),
                html.H2("Potential Carbon Savings"), 
                html.H6("Please Select a Year : "),
                dcc.Dropdown(id="slct_year",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi=False,
                     value=str(C_year),
                     style={'width': "40%"}
                     ),
                html.Br(),
                html.Br(),
                html.Button("Click to download spreadsheet", id="carbon-savings-file"),
                dcc.Download(id="download-carbon-savings-file"),
                dcc.Graph(id='carbon_savings', figure = {}),
                html.P(["This chart displays an estimate of the grid's potential carbon emission savings per year. The calculation assumes that the energy generated by the mthembanji  microgrid has displaced carbon from an electricity generation system using a diesel generator. Potential carbon savings are calculated by taking the total amount of energy generated by the grid each year and multiplying this by an emission factor (2.4) dictated by our system size and load factor level. This methodology was taken from UNFCCC resources. To learn more about the methodology followed click ",
                           html.A("here",href="https://cdm.unfccc.int/methodologies/DB/9KJWQ1G0WEG6LKHX21MLPS8BQR7242") ,
                           (" under 'Renewable electricity generation for captive use and mini-grid'.")]),
                
                ]) 
        
#============================SOCIAL IMPACT TABS================================
@app.callback(
        Output('social_tabs_content', 'children'),
        Input('social_tabs', 'value'))
def render_social_tabs(tab):
    if tab == 'tab-1':
        return html.Div([
                html.Br(),
                html.Hr(),
                html.H2("Energy Access Data"),
            
                html.Br(),
                html.Div(         
                    html.Dialog("Tracking the community's Access to Energy, is the most important Social Impact indicator to track. This data allows microgrid developers to understand the true impact energy access has on developing communities."),
                    style={'fontSize':16}),
               
                dcc.Graph(id='Energy_Access_Graph_1', figure=fig_EnergySatisfaction),
                html.Div(         
                    html.Dialog("Q: Overall, on a scale of 1-5, how happy are you with your household's current level of access to energy?"),
                    style={'fontSize':14}),
                html.P("This chart displays how satified the users are with their level of access to electricity."),
                html.P(" Tracking this indicator is key to project success, grasping if the community is happy or not with the microgrid."),           
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Energy_Access_Graph_2', figure=fig_EnergySources),
                html.Div(         
                    html.Dialog("Q: What source of electricity does your home use?"),
                    style={'fontSize':14}),
                html.P("This chart displays what enegy sources are being used to power the community."),
                html.P(" Tracking this indicator shows us if the community who use the microgrid still require alternative sources to meet their energy needs."),   
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Energy_Access_Graph_3', figure=fig_Appliances),
                html.Div(         
                    html.Dialog("Q: What appliances are owned by your household?"),
                    style={'fontSize':14}),
                html.P("This chart displays the household appliances used by the community."),
                html.P(" Energy access makes it possible for the community to use modern household luxuries such as TVs and even modern necessities like refrigerators."),   
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Energy_Access_Graph_4', figure=fig_LightSources ),
                html.Div(         
                    html.Dialog("Q: What lighting source does your household use?"),
                    style={'fontSize':14}),
                html.P("This chart displays what sources are being used to power lighting in homes."),
                html.P(" This provides more insight into how the community is using the microgrid energy or if they are still reliant on other sources."),   
                html.Hr(),
                ])   
    elif tab == 'tab-2':
       return html.Div([
               html.Br(),
               html.Hr(),
               html.H2("Tariff and Service Data"),
                
               html.Br(),
               html.Div(         
                   html.Dialog("Tariff and Service satisfaction is an important indicator to track to ensure the continued success of the project. This data allows the Microgrid team to make informed decisions regarding the pricing and service offered to the community. These questions were asked to the 55 houshlods connected to the Microgrid."),
                   style={'fontSize':16}),
               html.Div(         
                   html.Dialog("QUESTIONS: since the installation of the microgrid..."),
                   style={'fontSize':14}),
              
               dcc.Graph(id='Tariff_Graph_1', figure=fig_CostSatisfaction),
               html.Div(         
                    html.Dialog("Q: On a scale of 1-5, how happy are you with how much you pay for your tariff??"),
                    style={'fontSize':14}),
               html.P("This chart displays how satified the users are with how much they are paying for their electricity."),
               html.P(" Tracking this indicator may highlight any potential problems with pricing, a key indicator of SDG7 is 'affordability' which directly impacts the success of the project."),   
               html.Hr(),
               html.Br(),
               dcc.Graph(id='Tariff_Graph_2', figure=fig_PaymentMethod ),
               html.Div(         
                    html.Dialog("Q: On a scale of 1-5, how happy are you with the method of paying for your tariff??"),
                    style={'fontSize':14}),
               html.P("This chart displays how satified the users are with HOW they pay for their energy."),
               html.P(" Tracking this indicator helps inform the business model and the service provided. Paying for energy should not be confusing and this indicator helps us make sure it is not."),   
               html.Hr(),
               html.Br(),
               dcc.Graph(id='Tariff_Graph_3', figure=fig_Recommendation ),
               html.Div(         
                    html.Dialog("Q: On a scale of 1 - 5, how likely would you be to recommend the minigrid to a friend? ?"),
                    style={'fontSize':14}),
               html.P("This chart displays how likely the current microgrid users are to reccomend the service to a neighbour or friend."),
               html.P(" Tracking this indicator is another way of grasping the communities opinion and satisfaction with the microgrid and service."),   
               html.Hr(),
               ])
    elif tab == 'tab-3':
        return html.Div([
                html.Br(),
                html.Hr(),
                html.H2("Health, Education and Communitcation Data"),
               
                html.Br(),
                html.Div(         
                    html.Dialog("Access to adequate energy can impact health and education by either directly powering medical equipment and devices used in the classroom or simple poweeing lights for nightimes study, or allowing people to charge their phones for medical information."),
                    style={'fontSize':16}),
               
                dcc.Graph(id='H&E_graph_1', figure=fig_StudyingHours),
                html.Div(         
                    html.Dialog("Q: How many hours do children do school work in the home per WEEK?"),
                    style={'fontSize':14}),
                html.Hr(),
               
                dcc.Graph(id='H&E_graph_2', figure=fig_SmartPhoneSatisfaction),
                html.Div(         
                    html.Dialog("Q: Overall, on a scale of 1 - 5, how happy are you with your current level of access to mobile phones and their performance?"),
                    style={'fontSize':14}),
                html.Hr(),

                dcc.Graph(id='H&E_graph_4', figure=fig_HealthInfo),
                html.Div(         
                    html.Dialog("Q: Where do you get your healthcare information from? "),
                    style={'fontSize':14}),
                html.Hr(),
               
            #    """
            #     dcc.Graph(id='H&E_graph_3', figure=fig_NoSchool),
            #     html.Div(         
            #         html.Dialog("Q: How many school aged children in your household do not go to school??"),
            #         style={'fontSize':14}),
            #     html.Hr(),
            #    """          
                ])
    elif tab == 'tab-4':
        return html.Div([
                html.Br(),
                html.Hr(),
                html.H2("Employment and Finance Data"),
                
                html.Br(),
                html.Div(         
                    html.Dialog("Monitoring the Microgrid's social impact on finance and employment allows us to see if any economic development is happening."),
                    style={'fontSize':16}),
                
                dcc.Graph(id='E&P_graph_1', figure=fig_BusinessMonth),
                html.P("This chart track how many businesses there are in Mthembanji, each month since the installation of the Solar Microgrid"),
                html.P(" Energy access can cause economic development and open doors to new business opportunities. This indicator tracks this each month to see the effect a modern energy supply has."),   
                html.Hr(),
                dcc.Graph(id='E&P_graph_2', figure=fig_Finances),
                html.Div(         
                    html.Dialog("Q: Overall, on a scale of 1 - 5, how secure do you feel your household's finances are??"),
                    style={'fontSize':14}),
                html.P("This chart displays the average monthly incomes and expenditures of microgrid users."),
                html.P("Tracking this indicator allows us to monitor is energy access is leading to any economic development in the town. However, income and expenditure levels are impacted by several wider factors, so the data cannot be directly linked to the microgrid. "),   
                html.Hr(),
                html.Br(),
                dcc.Graph(id='E&P_graph_3', figure=fig_FinancialSecurity),
                html.P("This chart displays how financially secure microgrid users feel their household is."),
                html.P(" Tracking this indicator provides insight both into economic development and into the affordability of the project from the community's perspective. However, income and expenditure levels are impacted by several wider factors, so the data cannot be directly linked to the microgrid. "),    
                html.Hr(),
                dcc.Graph(id='E&F_graph_4', figure=fig_Income),
                html.Hr(),
                html.Br(),

                ])
    elif tab == 'tab-5':
        return html.Div([
                html.Br(),
                html.Hr(),
                html.H2("Women Empowerment Data"),
                
                html.Br(),
                html.Div(         
                    html.Dialog("The Social Impact of the microgrid in terms of Women Empowerment is how the Solar Microgrid has changed the women, who use its, lives. The 28 women in Mthembanji who are connected to the Microgrid were asked a series of questions to see if their situation has changed since its installation."),
                    style={'fontSize':16}),
                html.Br(),
                html.Div(         
                    html.Dialog("QUESTIONS: since the installation of the microgrid..."),
                    style={'fontSize':14}),
                
                dcc.Graph(id='Women_Power_Graph_1', figure=fig_WomenFreetime),
                    html.Div(         
                    html.Dialog("Q: how has the ammount of freetime you have changed?"),
                    style={'fontSize':14}),
                html.P("This chart displays how the women of the town feel the microgrid has changed the ammount of freetime they have."),
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Women_Power_Graph_2', figure=fig_WomenIndependance),
                    html.Div(         
                    html.Dialog("Q: how has your of independance and decision-making power changed?"),
                    style={'fontSize':14}),
                html.P("This chart displays how the women of the town feel the microgrid has changed the ammount of independance and decision making power they have in the household."),
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Women_Power_Graph_3', figure=fig_WomenRespectHOME),
                    html.Div(         
                    html.Dialog("Q: how has the ammount of respect you get in the household changed?"),
                    style={'fontSize':14}),
                html.P("This chart displays how the women of the town feel the microgrid has changed the ammount of respect they recieve in the HOUSEHOLD."),
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Women_Power_Graph_4', figure=fig_WomenRespectCOMM),
                html.Div(         
                    html.Dialog("Q: how has the ammount of respect you get in the community changed?"),
                    style={'fontSize':14}),
                html.P("This chart displays how the women of the town feel the microgrid has changed the ammount of respect they recieve in the COMMUNITY"),
                html.Hr(),
                html.Br(),
                dcc.Graph(id='Women_Power_Graph_5', figure=fig_HomeSecurity),
                html.Div(         
                    html.Dialog("Q: how has your security in the home changed?"),
                    style={'fontSize':14}),
                html.P("This chart displays how the women of the town feel the microgrid has changed how secure they feel in their home."),
                html.Hr(),
                ])
    
#==============================================================================
        
# @app.callback(
#         Output('maintenance_content', 'children'),
#         Input('maintenance_tabs', 'value'))

# def render_maintenance_tabs(tab):
#     if tab == 'tab-1':
#         return html.Div([
#                 html.Br(),
#                 html.Hr(),
#                 html.H2("Maintenance content to go here"),
#                 html.Button("Click to download SOP-011: Site Visit Maintenance Report Template", id="file"),
#                 dcc.Download(id="download-file"),
#                 html.Hr(),
#                 html.P("Below are protoypes developed of how the maintenance tab could look like. The map feature is similar to the initial idea of last year's design where they developed it on Anvil. However, the suggested prototype builds upon that further by allowing you to 'interact' with the map by viewing the current status of the site(s)."),
#                 html.P("Maintenance logs could be suggested going forward where the site manager(s) can upload any comments/images from their most recent site visits and address any issues that may occur."),
#                 html.Img(src='https://cdn.discordapp.com/attachments/369088493990969344/948319393962655774/unknown.png',style={'height':'50%', 'width':'50%'}),
#                 html.Img(src='https://cdn.discordapp.com/attachments/369088493990969344/948327687796191252/unknown.png',style={'height':'50%', 'width':'50%'}),
#                 html.Hr(),
#                 html.Img(src='https://cdn.discordapp.com/attachments/369088493990969344/948327010105708584/unknown.png',style={'height':'50%', 'width':'50%'}),
#                 html.Img(src='https://cdn.discordapp.com/attachments/369088493990969344/948327424779767918/unknown.png',style={'height':'50%', 'width':'50%'}),
#                 html.Hr(),
#                 ])
# @app.callback(
#         Output('technical_tabs_2_content', 'children'),
#         Input('technical_tabs_2', 'value'))

# def render_tech_tabs_2(tab):
#     if tab == 'tab-1':
#         return html.Div([
#                 html.Br(),
#                 html.Hr(),
#                 html.H2("Total power of PV systems"), 

#                 dcc.Graph(id='holder_graph_1', figure=holder_fig),
#                 html.P("This chart displays the current power from the PV (PhotoVoltaic) solar systems."),
#                 html.P("This is a key data indicator to track as it displays the maximas and minimas of the amount of power from the PV systems, allowing for one to visualize how much stress/load the system is under during peak times (around morning time), also it is interesting to inspect/see that from 23rd to 25th, the graph was displaying anomalous data, this is due to the fact that storm Ana struck the surrounding areas, hence the data."),
#                 ])
#     elif tab == 'tab-2':
#         return html.Div([
#                 html.Br(),
#                 html.Hr(),
#                 html.H2("WIP"), # ======================================================================================================================= WIP ======================================================= #
#                 html.P("This section is currently work in progress."),
#                 dcc.Graph(id='holder_graph_1', figure=holder_fig),
#                 html.Hr(),
#                 ])

#===========================HOME TABS==================================

@app.callback(
    Output('home_content', 'children'),
    Input('home_tabs', 'value'))

def render_home_tab(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Br(),
            html.H3(("Background Information"),style={'backgroundColor': '#FFFFFF'}),
                    html.P("Collecting and analysing data to understand microgrid performance is essential for informing effective maintenance schedules, business planning and technical designs for future microgrids. It can also inform policy interventions and help build a knowledgebase to accelerate the microgrid sector both nationally and globally. "),
                    html.P(["Currently, two operational microgrids have been installed as a part of the ",
                           html.A("EASE",href="https://ease.eee.strath.ac.uk/") ,
                           (" Project; Mthembanji installed in July 2020 and Kudembe in September 2022. Since installation, both sites have been collecting data through smart meters, remote monitoring devices and social impact surveys. An objective of EASE is to utilise project learning to inform the microgrid sector in Malawi, specifically through analysis and sharing of data.")]),
                    html.H3("Why is Microgrid data important?"),
                    html.P("Many solar microgrid projects have faced sustainability challenges due to insufficient  maintenance or inefficient business models due to a lack of quality data collection and analysis. Microgrids that implement innovative smart metering and remote monitoring address these challenges, allowing developers to make informed decisions to ensure systems are operating  at optimum economic and technical efficiency in order to remain financially and practically viable. Analysing data also helps to fine-tune existing business models, by informing tariffs to ensure access to electricity is affordable for microgrid customers, while still maintaining sufficient income to be financially viable, offering confidence for potential investors. Perhaps most importantly, data analysis can help inform the technical design of other microgrids and therefore has the potential for impact on multiple sites."),
                    html.P("Data visualisation and sharing also enables funders, investors, researchers, and policymakers to monitor and understand microgrid performance, allowing use of the data to inform policy, investments, targeted research and other interventions in the microgrid enabling environment to accelerate their deployment.  In short, data analysis enables better informed and more efficient microgrid deployment, accelerating energy access and contributing to achieving SDG7."),
                
                #SDG image
                html.Div([
                html.Br(),
                html.Img(src='https://www.its.ac.id/sustainability/wp-content/uploads/sites/120/2020/08/SDG_7-1024x1024.png',style={'height': '15%', 'width': '15%','border-radius':'10%'}),
                ], style={'textAlign': 'left'}),
                html.Div([
                html.P("SDG 7 is to 'Ensure access to affordable, reliable, sustainable and modern energy for all'"),
                ], style={'backgroundColor': '#FFFFFF', 'textAlign':'left'}),
                html.Br(),
                
                html.Div(),
                    html.H3("What data are we monitoring?"),
                    html.P("Alongside information related to the wider EASE project monitoring and evaluation framework, data is being collected from the microgrid in themes of technical, economic, and social impact, summarised below:"),
                    html.B("Techincal Data:"),
                    html.P("Relating the to the functionality of the generation and distribution systems, a variety of data on technical performance is being collected through remote monitoring of the PV, batteries and inverters, along with measurements and observations of the system collected through scheduled maintenance visits on site."),
                    html.P(""),
            
                #inside image    
                html.Div([
                html.Img(src='https://www.sma-sunny.com/wp-content/uploads/2020/09/Inside-the-container-1024x767.jpeg',style={'height':'30%', 'width':'25%', 'border-radius':'0%'}),
                ], style={'textAlign': 'left'}),
                html.Div(
                    html.P("Inside the container"), style={'textAlign':'left', 'color': '#616161','margin-left':'80px'}),
                
                
                html.Div([
                    html.B("Demand and Economic data:"),
                    html.P("relating the to the functionality of the generation and distribution systems, a variety of data on technical performance is being collected through remote monitoring of the PV, batteries and inverters, along with measurements and observations of the system collected through scheduled maintenance visits on site."),
                    html.P(""),
                    html.B("Social Impact data:"),
                    html.P("A Key Performance Indicator framework is being used to track data relating to the impact the microgrid is having on the community, in themes such as health and education, employment and finance, and female empowerment."),
                ]),
                
                html.Div(
                    html.P("This dashboard aims to provide information on the pilot microgrids in Mthembanji and Kudembe, Malawi. The key material to be displayed through this dashboard is the demand, technical, and social impact data. All these key parameters provide invaluable information about the functioning of the microgrid along with its long-term feasibility and the direct impact which it has on the inhabitants in Mthembanji and Kudembe."),
                    style={'fontSize':16}),
                
                html.Div(         
                    html.P("The two microgrids in Malawi play a critical role in providing insight and information for future deployments of microgrids in Malawi and other developing countries. This is critically important because, if successful, functionally, and financially viable microgrid systems could offer a solution in the drive to provide clean and reliable energy for those in the most remote and underdeveloped areas. Therefor, helping to achieve the UN Sustainable Development Goal 7."),
                    style={'fontSize':16}),
                    html.Hr()]),
        
#MTHEMBANJI TAB     
    if tab == 'tab-2':
        return html.Div([
            html.Br(),
                html.Div(
                    html.H3("The Mthembanji Microgrid"),style={'backgroundColor': '#FFFFFF', 'textAlign': 'left'}),
            html.Hr(),   
            html.Div([
                html.Img(src='https://www.sma-sunny.com/wp-content/uploads/2020/09/kv-micro-grids-malawi.jpg',style={'height':'70%', 'width':'70%',}),
                ], style={'textAlign': 'center'}),

            html.Hr(),
            html.Div([
                html.H3("Brief Overview"),
                html.Ul([
                    html.Li("Installed July 2020"),
                    html.Li("60 Customers"),
                    html.Li("11.5kW Pv generation"),
                    html.Li("19.8kWh Battery capacity"),
                    html.Li(html.P(["48V ",
                            html.A("TESVOLT",href="https://www.tesvolt.com/en/") ,
                            (" Lithium Ion Batteries")])),
                    html.Br(),
                    ]),  
                ]),
            
            html.Div([
                html.H3("About"),  
                html.P("The Mthembanji microgrid consists of a large shipping container with 2 large solar PV panels mounted either side of the container. Inside consists of inverters, controls and ancillary components, with an insulated, air-conditioned room housing the lithium-ion batteries at a controlled temperature. Maintaining the ideal battery operating temperature is incredibly important to prolong battery lifetimes. Monitoring the temperature also helps with designing cooling systems adequate for current and future temperatures (expected to rise due to climate change) essential for technical design. "),
                html.P("Depth of discharge levels are pre-programmed, with the batteries cutting out at 20% and automatically powering up when this is reached. Experiences of Tesvolt of Mthembanji have been positive, with few technical issues experienced. "),
                html.P("Electricity from the generation hub is distributed through overhead wires on 9m wooden poles through 50mm2 aluminium cables to customer premises. The distribution grid is analogous to that of a 240V single phase Low Voltage feeder from a secondary substation on the Malawi ESCOM grid. The decision for low voltage single phase reduced capital costs but has limited the customer base to a 600m radius from the generation hub and prevented the use of 3 phase motors for agricultural use. Smart meters mounted on the distribution poles automatically disconnect customers when their balance runs low, as well as setting power limits to protect the system from misuse."),
                html.Img(src='https://i.postimg.cc/503t9m3Y/a-ditribution-pole-copy-2.jpg', style = {'width': '20%'}),
            html.Div(
                    html.P("Distribution pole"), style={'textAlign':'left', 'color': '#616161','margin-left':'60px'}),
                html.P(""),
                html.P("The containerised  solution offers security from theft, easy access and additional space to store tools, equipment or products, while being easy to transport and locally available in Malawi. "),
                html.Hr()]),
            ]),
        
#KUDEMBE TAB     
    elif tab == 'tab-3':
        return html.Div([
            html.Br(),
                html.Div(
                    html.H3("The Kudembe Microgrid"),style={'backgroundColor': '#FFFFFF'}),
            
            html.Hr(),
             html.Div([
                html.Img(src='https://i.postimg.cc/VLgDPPHC/Screenshot-2023-03-08-at-13-46-39.png',style={'height':'40%', 'width':'40%'}),
                ], style={'textAlign': 'center'}),
            
            html.Hr(),
            html.Div([
                html.H3("Brief Overview"),
                html.Ul([
                    html.Li("Installed September 2022"),
                    html.Li("50 Customers"),
                    html.Li("10.92kW Pv generation"),
                    html.Li("20kWh Battery capacity"),
                    html.Li(html.P(["48V ",
                            html.A("BYD",href="https://www.bydbatterybox.com") ,
                            (" Lithium Ion Batteries")])),      
                    html.Br(),
                    ]),  
                ]),
            
            html.Div(
                html.H3("About")),  
            html.Div([
                html.P("Identical to Mthembanji, the Kudembe microgrid consists of a large shipping container with 2 large solar PV panels mounted either side of the container. Inside consists of inverters, controls and ancillary components, with an insulated, air-conditioned room housing the lithium-ion batteries at a controlled temperature. Maintaining the ideal battery operating temperature is incredibly important to prolong battery lifetimes. Monitoring the temperature also helps with designing cooling systems adequate for current and future temperatures (expected to rise due to climate change) essential for technical design"),
                html.P("Depth of discharge levels are pre-programmed, with the batteries cutting out at 20% and automatically powering up when this is reached. Experiences of Tesvolt of Mthembanji have been positive, with few technical issues experienced."),
                html.P("Electricity from the generation hub is distributed through overhead wires on 9m wooden poles through 50mm squared aluminium cables to customer premises. The distribution grid is analogous to that of a 240V single phase Low Voltage feeder from a secondary substation on the Malawi ESCOM grid. The decision for low voltage single phase reduced capital costs but has limited the customer base to a 600m radius from the generation hub and prevented the use of 3 phase motors for agricultural use. Smart meters mounted on the distribution poles automatically disconnect customers when their balance runs low, as well as setting power limits to protect the system from misuse."),
                html.P("A single source justification route was chosen to allow BNG to supply and install both generation and distribution systems for Kudembe. While impressed with the workmanship and ability demonstrated in Mthembanji, there was also an impetus to build local capacity and extend the value chain closer to Malawi, while reducing transport and insurance costs from transportation from South Africa. Unfortunately, while the shipping container was available locally, all other materials were purchased from South Africa which caused delays in importation due to lack of foreign currency availability in Malawi."),
                html.Hr()
        ]),
        ]),

#============================DEMAND TABS================================

@app.callback(
        Output('tabs-example-content', 'children'),
        Input('tabs-example', 'value'))

def render_content(tab):
#===TAB 1 (Revenue Data) 
    if tab == 'tab-1':
        return html.Div([
            html.Hr(),
            html.H2("Monthly Revenue for Given Year"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_1_1',
                options=[
                    {'label': 'Mthembanji', 'value': 2},
                    {'label': 'Kudembe', 'value': 3},
                ],
                value = 2,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please Select a Year: "),# New quality of life improvements
            dcc.Dropdown(id="slct_year_1_1",
                options=[{"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         {"label": "2023", "value": "2023"},
                         ],
                placeholder="Select a year",
                searchable = False,
                multi=False,
                value=str(C_year),
                style={'width': "40%"}
            ),
            html.Br(),
            dcc.RadioItems(id = 'slct_user_1_1',
                options=[
                    {'label': 'All Users', 'value': 1},
                    {'label': 'Residential', 'value': 2},
                    {'label': 'Businesses', 'value':3},
                    {'label': 'Institutional', 'value':4},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ), 
            html.Br(),
            html.Div([
            dcc.RadioItems(id = 'TorA',
                options=[
                    {'label': 'Total Revenue', 'value': 1},
                    {'label': 'ARPU', 'value': 60}
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),]),
            html.Br(),
            html.P("Please allow up to 15 seconds for graphs to load when viewing data for residential and business users."),
            html.Button("Click to download spreadsheet", id="revenue-file"),
            dcc.Download(id="download-revenue-file"),
            dcc.Graph(id='my_graph_1', figure={}),
            html.P(["This bar chart displays either the total monthly revenue generated across a given year or the ARPU (average revenue per user) across a given year. You may also choose a user category to view data specific to that category ( ",
                   html.Span("Residential" ,
                             id = "residential_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ),
                   ",",
                   html.Span("Businesses" ,
                             id = "businesses_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ), 
                   ",",
                   html.Span("Institutional" ,
                             id = "institutional_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ),                   
                   " ). ",]),
            dbc.Tooltip(
                "51 out of 60 customers",
                target="residential_tooltip",
                placement="bottom"),
            dbc.Tooltip(
                "7 out of 60 customers",
                target="businesses_tooltip",
                placement="bottom"),  
            dbc.Tooltip(
                "2 out of 60 customers",
                target="institutional_tooltip",
                placement = "bottom"),                      
                html.P("This is useful data to analyse as it provides information of how much monthly revenue the microgrid generated throughout the year or how much revenue the average customer generated. This data could be useful for developing a business plan as it enables evaluation of how much revenue the microgrid generates and how much an average customer generates. This format is also particularly useful as it enables easy visual analysis of how the total monthly revenue and ARPU vary month to month or seasonally throughout a given year, hence enabling trends to be established and analysed."),
            html.Br(),
            html.Hr(),
        ])
#===TAB2 (Monthly Demand) 
    elif tab == 'tab-2':
        return html.Div([            
            html.Hr(),
            html.H2("Monthly Demand for Given Year"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_2_1',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value = 1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please Select a Year: "),# New quality of life improvements
            dcc.Dropdown(id="slct_year",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         {"label": "2023", "value": "2023"}
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi = False,
                     value = str(C_year),
                     style = {'width': "40%"}
                     ),
            html.Br(),
            dcc.RadioItems(id = 'slct_user_2_1',
                options=[
                    {'label': 'All Users', 'value': 1},
                    {'label': 'Residential', 'value': 2},
                    {'label': 'Business', 'value': 3},
                    {'label': 'Institution', 'value': 4},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            dcc.RadioItems(id = 'TorU_2_1',
                options=[
                    {'label': 'Total', 'value': 1},
                    {'label': 'Average', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.P("Please allow up to 15 seconds for graphs to load when viewing data for residential and business users."),
            html.Br(),
            html.Button("Click to download spreadsheet", id="month-demand-file"),
            dcc.Download(id="download-month-demand-file"),
            dcc.Graph(id = 'my_graph_4', figure = {}),   
            html.Br(),
             html.P(["This chart is used to display the monthly usage of the entire microgrid over a given year of the selected user category. It also allows to view data sepeartely for each user category ( " , 
                   html.Span("Residential" ,
                             id = "residential_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ),
                   ",",
                   html.Span("Businesses" ,
                             id = "businesses_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ), 
                   ",",
                   html.Span("Institutional" ,
                             id = "institutional_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ),                   
                   " ). ",]),
            dbc.Tooltip(
                "51 out of 60 customers",
                target="residential_tooltip",
                placement="bottom"),
            dbc.Tooltip(
                "7 out of 60 customers",
                target="businesses_tooltip",
                placement="bottom"),  
            dbc.Tooltip(
                "2 out of 60 customers",
                target="institutional_tooltip",
                placement = "bottom"),
            html.P("This is useful data to display on our dashboard as it allows us to see how much energy is being consumed each month throughout a given year. This can help us identify seasonal trends i.e. increases in consumption due to more income during a particular season. A yearly graph can also give us a better idea of the increase/decrease in consumption over the years which would likely have a strong correlation with the grid's economic impact. "),
            html.Br(),
            html.Hr(),            
        ])
#===TAB3 (Load Profiles) 
    elif tab == 'tab-3':
        return html.Div([
            html.Hr(),
            html.H2("Load Profile for a Full Year"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_3_1',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please Select a Year: "),# New quality of life improvements
            dcc.Dropdown(id="slct_year_3_1",
                     options=[
                         {"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         {"label": "2023", "value": "2023"}
                         ],
                     placeholder="Select a year",
                     searchable = False,
                     multi = False,
                     value = str(C_year),
                     style = {'width': "40%"}
                     ), 
            html.Br(),
            dcc.RadioItems(id = 'slct_user_3_1',
                options=[
                    {'label': 'All Users', 'value': 1},
                    {'label': 'Residential', 'value': 2},
                    {'label': 'Businesses', 'value':3},
                    {'label': 'Institutional', 'value':4},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),    
            html.Button("Click to download 8760", id="8760-file"),
            dcc.Download(id="download-8760-file"),
            dcc.Graph(id = 'load_profile_year', figure = {}),
            html.P("This graph displays the mean, median, 75 %tile, and 25% tile for a single customer over a full year (8760 hourly data points). It is possible to view data for all customers as well as seggregated data for each customer category. The data shown was recorded from the 5th of July 2021 to the 5th of July 2022. The 8760 spreadsheet can be downloaded to view more data which is described within the 'ReadMe' sheet."),
            html.Hr(),

            html.H2("Microgrid Load Profile for Given Day"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_3_2',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please Select a Date:"),
            dcc.DatePickerSingle(id = 'my-date-picker-single',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day),
                display_format='DD/MMM/YYYY'),
            html.Br(),
            html.Br(),
            dcc.RadioItems(id = 'slct_user_2',
                options=[
                    {'label': 'All Users', 'value': 1},
                    {'label': 'Residential', 'value': 2},
                    {'label': 'Businesses', 'value':3},
                    {'label': 'Institutional', 'value':4},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            dcc.RadioItems(id = 'TorU_2',
                options=[
                    {'label': 'Total', 'value': 1},
                    {'label': 'Average', 'value': 2},                
                    ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.P("Please allow up to 15 seconds for graphs to load when viewing data for residential and business users."),
            html.Br(),
            html.Button("Click to download spreadsheet", id="day-profile-file"),
            dcc.Download(id="download-day-profile-file"),            
            dcc.Graph(id = 'my_graph_2', figure = {}),   
            html.Br(),
            html.P(["This chart displays the hourly usage of the entire microgrid or the hourly usage for the average customer on a given day. It is also possible to view data seperately based on the user category of your choosing (",
                   html.Span("Residential" ,
                             id = "residential_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ),
                   ",",
                   html.Span("Businesses" ,
                             id = "businesses_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ), 
                   ",",
                   html.Span("Institutional" ,
                             id = "institutional_tooltip" ,
                             style={"textDecoration": "underline", "cursor": "pointer"},
                             ),                   
                   " ). ",]),
            dbc.Tooltip(
                "51 out of 60 customers",
                target="residential_tooltip",
                placement="bottom"),
            dbc.Tooltip(
                "7 out of 60 customers",
                target="businesses_tooltip",
                placement="bottom"),  
            dbc.Tooltip(
                "2 out of 60 customers",
                target="institutional_tooltip",
                placement = "bottom"),      
            html.P("This is useful in order to analyse how much power the system used in hourly intervals throughout a particular day for both the entire microgrid and for the average customer connected to the microgrid. This is also a beneficial format as it gives a more wholistic view of the entire system. This may be useful to analyse the impact of a particular event (e.g., a storm) on the entire system as we can zone in on any given day. It is also effective to see the total load of the system and, hence, may be useful to compare with battery charge state and other technical data."),
            html.Br(),
            html.Hr(),

            html.H2("Microgrid Load Profile for Given Range"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_3_3',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ), 
            html.Br(),
            html.H6("Please select start (left) and end (right) date: "),
            dbc.Alert([html.I(className="bi bi-exclamation-circle-fill")," Invalid Range! Please select range that is over 1 day and less than 40 days."],id='range_alert',color= 'danger',class_name="d-flex align-items-center", is_open = False, duration = 3000),
            dcc.DatePickerRange(
            id='my-date-picker-range-3',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                start_date=date(C_year, C_month, 1),
                end_date=date(C_year, C_month, C_day),
                display_format='DD/MMM/YYYY'),
            html.Br(),            
            html.Br(),
            dcc.RadioItems(id = 'TorU',
                options=[
                    {'label': 'Total', 'value': 1},
                    {'label': 'User', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            dcc.RadioItems(id = 'slct_user_av',
                options=[
                    {'label': 'All Users', 'value': 1},
                    {'label': 'Residential', 'value': 2},
                    {'label': 'Businesses', 'value': 3},
                    {'label': 'Institutional', 'value': 4},                
                    ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.P("Please allow up to 15 seconds for graphs to load when viewing data for residential and business users."),
            html.Br(),
            html.Button("Click to download spreadsheet", id="range-profile-file"),
            dcc.Download(id="download-range-profile-file"),
            dcc.Graph(id = 'my_av_load_graph', figure={}),
            html.Br(),
            html.P("This is useful data in order to analyse what the daily peak load of the whole microgrid is each day. This enables easy analysis of how much the peak load amount varies throughout the given month. This could be useful for analysing the impact of an event (e.g., a storm) by observing how the daily peak load varies on the days of and around the event. Furthermore, this data could be useful for comparing with technical data in order to ensure the microgrid is able to supply the peak load of the system throughout the month. This data could also be useful to compare month to month or seasonally to see if the changing months or seasons has an impact on the peak loads of the system throughout the month."),
            html.P("This is useful in order to analyse how much power the system used on average throughout the given month and what the microgrid’s load profile looked like for that month and what the average customer’s load profile looked like for that given month. This may also be useful for generating a business plan and also comparing monthly or seasonally to analyse whether or not the changing months or seasons has an impact on the average usage of the microgrid."),
            html.Br(),
            html.Hr()
        ])
#===TAB4 (Peak Load Data)    
    elif tab == 'tab-4':
        return html.Div([
            html.Br(),
            html.Hr(),
            html.H2("Peak Loads for Given Month"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_4_1',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please Select a Month: "),     
            dcc.DatePickerSingle(id = 'my-date-picker-single-5',
                min_date_allowed=date(2022, 9, 21),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day),
                display_format='MMM/YYYY'),
            html.Br(),
            html.Br(),
            html.Button("Click to download spreadsheet", id="month-peak-file"),
            dcc.Download(id="download-month-peak-file"),
            dcc.Graph(id = 'my_peak_graph', figure={}),
            html.Br(),
            html.Hr(),

            html.H2("Peak Load for Given Year"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_4_2',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please Select a Year: "),# New quality of life improvements
            dcc.Dropdown(id="slct_year_4_2",
                options=[{"label": "2020", "value": "2020"},
                         {"label": "2021", "value": "2021"},
                         {"label": "2022", "value": "2022"},
                         {"label": "2023", "value": "2023"},
                         ],
                placeholder="Select a year",
                searchable = False,
                multi=False,
                value=str(C_year),
                style={'width': "40%"}
            ),
            html.Br(),
            html.Button("Click to download spreadsheet", id="year-peak-file"),
            dcc.Download(id="download-year-peak-file"),
        dcc.Graph(id='my_peak_graph_2', figure = {}),
        html.Br(),
        html.Hr(),
        html.Hr(),
        html.P("The charts above display the daily peak loads for the whole system throughout a given month or year."),
        html.P("This is useful data in order to analyse what the daily peak load of the whole microgrid is each day or month. This enables easy analysis of how much the peak load amount varies throughout the given time period. This could be useful for analysing the impact of an event (e.g., a storm) by observing how the daily peak load varies on the days of and around the event. Furthermore, this data could be useful for comparing with technical data in order to ensure the microgrid is able to supply the peak load of the system throughout the month/year. This data could also be useful to compare month to month or seasonally to see if the changing months or seasons has an impact on the peak loads of the system."),
        ])

#===TAB 5 (Connection Status) 
    elif tab == 'tab-5':
            numOn = 0
            numOff = 0
            numOn2 = 0
            numOff2 = 0

            #grabbing the connection status data from the url
            url_mth = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=110&site_id=26385"
            
            r = requests.get(url=url_mth, headers = header)
            s = r.content

            #converting json string to a panda object
            dfC_mth = pd.read_json(s)
            
            #in the range of 0 and the no of customers (items) in the object
            for index in range(0,len(dfC_mth['count'])):
                holder = dfC_mth['results'][index]
            #if the connection is on, add one to the on  counter
                if(holder['status'] == "on"):
                    numOn += 1
            #if the connection status if off, add one to the counter
                elif(holder['status'] == "off"):
                    numOff += 1
                elif(holder['status'] == "none"):
                    continue

            status_mth = ['On', 'Off'] 
            data_mth = [numOn, numOff]

            fig_mth = px.pie(values=data_mth, names=status_mth)


            #Repeat for Kudembe
            url_kud = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=110&site_id=26678"

            r2 = requests.get(url=url_kud, headers = header)
            s2 = r2.content

            dfC_kud = pd.read_json(s2)

            for index in range(0,len(dfC_kud['count'])):
                holder2 = dfC_kud['results'][index]
                if(holder2['status'] == "on"):
                    numOn2 += 1
                elif(holder2['status'] == "off"):
                    numOff2 += 1
                elif(holder2['status'] == "none"):
                    continue

            status_kud = ['On', 'Off'] 
            data_kud = [numOn2, numOff2]
            
            fig_kud = px.pie(values=data_kud, names=status_kud)

            return html.Div([
                    html.Br(),
                    html.Hr(),
                    html.H2('Current Connection Status'),
                    html.Br(),
                    html.H6("Mthembanji Connection Status"),
                    dcc.Graph(id="pie-chart-mth", figure = fig_mth),
                    html.Hr(),
                    html.Br(),
                    html.H6("Kudembe Connection Status"),
                    dcc.Graph(id="pie-chart-kud", figure = fig_kud),
                    html.Hr(),
                    html.P("This pie chart displays the current percentage of customers who have an active connection (ON) or have their connection disabled (OFF)."),
                    html.P("This is useful data to have as it enables easy establishment of the percentage of customers who are actually using their connection at this given moment and hence, provides some insight into how useful the microgrid is and what percentage of customers are actually using it."),
                    html.Br(),
                    html.Hr(),
            ])

    elif tab == 'tab-6':
        return html.Div([
            html.Br(),
            html.Hr(),
            html.H2("Customer Usage for a Given Day"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_6_1',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please select a customer from the dropdown: "),
            dcc.Dropdown(id="slct_customer",
                     options=[
                        #App Callback
                         ],    
                     placeholder="Select a customer",
                     searchable = False,
                     clearable = False,
                     multi = False,
                     value = str("001"),
                     style = {'width': "60%"}
                     ),
            html.Br(),
            html.H6("Please select a date: "),
            dcc.DatePickerSingle(
                id='my-date-picker-single-2',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day),
                display_format='MMM/YYYY'
                ),
            html.Br(), 
            html.Br(),
            html.Button("Click to download spreadsheet", id="day-cust-file"),
            dcc.Download(id="download-day-cust-file"),
            dcc.Graph(id = 'cust_on_day_graph', figure={}),
            html.Br(),
            html.P("This chart displays the hourly usage of a single customer on a given day."),
            html.P("This is useful to analyse what any customer has used throughout a particular day and may be useful to analyse the impact of a particular event (e.g., a storm) on a customer’s usage as it is possible to zone in on any given day."),
            html.Br(),
            html.Hr(),
            
            html.H2("Customer’s Average Daily Usage for Given Month"),
            html.Br(),
            html.H6("Please Select Microgrid Site:"),
            dcc.RadioItems(id = 'slct_grid_6_2',
                options=[
                    {'label': 'Mthembanji', 'value': 1},
                    {'label': 'Kudembe', 'value': 2},
                ],
                value=1,
                inputStyle={"margin-left": "15px", "margin-right":"5px"}
            ),
            html.Br(),
            html.H6("Please select a customer from the dropdown: "),
            dcc.Dropdown(id="slct_customer_2",
                     options=[
                         #App Callback
                         ],  
                     placeholder="Select a customer",
                     searchable = False,
                     clearable=False,
                     multi=False,
                     value="Zacharia Alfred",
                     style={'width': "60%"}
                     ),
            html.Br(),
            html.H6("Please Select a Month (YYYY-MM): "),
            dcc.Input(id='cus_av_month_usage_date_IP', type="text", value=currentYYMM, placeholder="YYYY-MM", debounce=True,style={'fontSize':16}),
            html.Br(),
            html.Br(),
            html.Button("Click to download spreadsheet", id="month-cust-file"),
            dcc.Download(id="download-month-cust-file"),            
            dcc.Graph(id = 'cust_month_average_graph', figure={}),    
            html.Br(),
            html.P("This chart displays the average daily usage of a single given customer over a given month. It does this by retrieving the data for each hour of each day of that given month. It then adds the usage amount for each hour for each day together (e.g., adds all the usage amount for 1AM for each day of the month together) and then divides that usage amount by the number of days in the month (this has been coded to take different months having different numbers of days and leap years into account). It does this for each hour and then displays the hourly data."),
            html.P("This is useful in order to analyse what any customer’s average daily usage looked like for a given month, hence, enabling the determination of usage patterns and trends and enabling the comparison of month-to-month data to see if there are any significant changes (possibly resulting from changing seasons)."),
            html.Br(),
            html.Hr(),
        ])

def convert_nth_day(date):
    temp = str(date)
    year = int(temp[0:4])
    month = int(temp[5:7])
    day = int(temp[8:10]) 
    nth_day = (datetime.date(year, month, day) - datetime.date(year,1,1)).days + 1
    return nth_day

def calc_difference_in_days(start_time, end_time):
    start = datetime.datetime.strptime(start_time, "%Y-%m-%d")
    end =   datetime.datetime.strptime(end_time, "%Y-%m-%d")
    diff = end.date() - start.date()
    diff_days = diff.days
    return diff_days  
       
def calc_difference_in_hours(start_time, end_time):
    start = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S+00:00")
    end =   datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S+00:00")
    diff = end - start
    diff_seconds = diff.total_seconds()
    diff_hours = diff_seconds/3600
    return diff_hours          

@app.callback(
    Output('slct_customer_2', 'options'),
    [Input('slct_grid_6_2', 'value')])

def update_dropdown_options(value):
    if value == 1:
        return [
            {"label": "001", "value": "Zacharia Alfred"},
            {"label": "002", "value": "Dalitso Bizweck"},
            {"label": "003", "value": "Bizzy Bizzy"},
            {"label": "004", "value": "Zipi Chadinga"},
            {"label": "005", "value": "Clodio Chagona"},
            {"label": "006", "value": "Stephano Chagona"},
            {"label": "007", "value": "Matilda Chagontha"},
            {"label": "008", "value": "Sainet Chemtila"},
            {"label": "009", "value": "Layton Chidavu"},
            {"label": "010", "value": "Lucia Chikapa"},
            {"label": "011", "value": "St John's Cathoric church"},
            {"label": "012", "value": "Seba Eliko"},
            {"label": "013", "value": "Vester Everson"},
            {"label": "014", "value": "Agatha Evesi"},
            {"label": "015", "value": "Wisdory Freizer"},
            {"label": "016", "value": "Lameck Galion"},
            {"label": "017", "value": "George Gilibati"},
            {"label": "018", "value": "Daudi Gondwa"},
            {"label": "019", "value": "Eliko Gonthi"},
            {"label": "020", "value": "Robert Gwafali"},
            {"label": "021", "value": "Chrisy Helemesi"},
            {"label": "022", "value": "Fedrick Jumbe"},
            {"label": "023", "value": "Jovelo Justin"},
            {"label": "024", "value": "Flescot R Kalambo"},
            {"label": "025", "value": "Davie Kamayaya"},
            {"label": "026", "value": "James Kamkwamba"},
            {"label": "027", "value": "Stampa Kamkwamba"},
            {"label": "028", "value": "Alex Kapingasa"},
            {"label": "029", "value": "Yohane Lipenga"},
            {"label": "030", "value": "Zakeyo Lipenga"},
            {"label": "031", "value": "Kelita Luciano"},
            {"label": "032", "value": "Lameck Luka"},
            {"label": "033", "value": "Richard Lyton"},
            {"label": "034", "value": "Lameki Malota"},
            {"label": "035", "value": "Noel Malota"},
            {"label": "036", "value": "Deborah Mangochi"},
            {"label": "037", "value": "Sedonia Mangochi"},
            {"label": "038", "value": "Elenata Mike"},
            {"label": "039", "value": "Agatha Miliano"},
            {"label": "040", "value": "Evinesi Miliano"},
            {"label": "041", "value": "Chinasi Mofati"},
            {"label": "042", "value": "Conrad Mpeketula"},
            {"label": "043", "value": "Alick Mphemvu"},
            {"label": "044", "value": "Linda Msowa"},
            {"label": "045", "value": "Maliko Mulanje"},
            {"label": "046", "value": "Gibson Mvula"},
            {"label": "047", "value": "Aujenia Nicolus"},
            {"label": "048", "value": "Peter Justin Nyale"},
            {"label": "049", "value": "Bizweck Record"},
            {"label": "050", "value": "Ntandamula primary school"},
            {"label": "051", "value": "Lewis Semiyano"},
            {"label": "052", "value": "Bizweck Shalifu"},
            {"label": "053", "value": "Rodreck Sipiliano"},
            {"label": "054", "value": "Kinlos Spiliano"},
            {"label": "055", "value": "Nickson Spiliano"},
            {"label": "056", "value": "Tobias Spiliano"},
            {"label": "057", "value": "Patrick Sugar"},
            {"label": "058", "value": "Stephano Tobias"},
            {"label": "059", "value": "Luciano Veleliyano"},
            {"label": "060", "value": "Konoliyo Zipi"},]
    elif value == 2:
        return [
            {"label": "001", "value": "Kalekeni Amosi"},
            {"label": "002", "value": "Chiwaula Botoman"},
            {"label": "003", "value": "Chilankhwazi CCAP Church"},
            {"label": "004", "value": "Alfred Chagomerana"},
            {"label": "005", "value": "Judith Charles Msyomera"},
            {"label": "006", "value": "Filipina Chilima"},
            {"label": "007", "value": "Yuda Chilima Kachigamba"},
            {"label": "008", "value": "Leckson Chimphanga"},
            {"label": "009", "value": "Julius Chionetsero"},
            {"label": "010", "value": "Napilira Chiwaula"},
            {"label": "011", "value": "Osman Edward"},
            {"label": "012", "value": "Daniel Esau"},
            {"label": "013", "value": "Elena Fackson"},
            {"label": "014", "value": "Kondwani Faison"},
            {"label": "015", "value": "Kenedy Fanuel"},
            {"label": "016", "value": "Godfrey Frackson"},
            {"label": "017", "value": "Jefrem Harry"},
            {"label": "018", "value": "Kalumbi Hendreson"},
            {"label": "019", "value": "Chionetsero Isaac"},
            {"label": "020", "value": "Rashid Jawadu 1"},
            {"label": "021", "value": "Rashid Jawadu 2"},
            {"label": "022", "value": "Rashid Jawadu 3"},
            {"label": "023", "value": "Monica Kachigamba"},
            {"label": "024", "value": "Yuda Kachigamba"},
            {"label": "025", "value": "Petros Kadaola"},
            {"label": "026", "value": "Nickson Kandulu"},
            {"label": "027", "value": "Esau Khudze"},
            {"label": "028", "value": "Gvh Kudembe"},
            {"label": "029", "value": "Uledi Kumbirani"},
            {"label": "030", "value": "George Mangochi"},
            {"label": "031", "value": "Julius Maulana"},
            {"label": "032", "value": "Maganizo Mawandiwe"},
            {"label": "033", "value": "Esau Mazengera"},
            {"label": "034", "value": "Chindikani Msyali"},
            {"label": "035", "value": "Charles Msyomera"},
            {"label": "036", "value": "Johans Namale"},
            {"label": "037", "value": "Chancy Nelson Chisale"},
            {"label": "038", "value": "Mailosi Nkoza"},
            {"label": "039", "value": "Mphika Primary school"},
            {"label": "040", "value": "Hezekia Pwetekani"},
            {"label": "041", "value": "Kachule Saad"},
            {"label": "042", "value": "Thauzeni Sakwiya"},
            {"label": "043", "value": "Nezesi Saliyele"},
            {"label": "044", "value": "Chisomo Sinkaika"},
            {"label": "045", "value": "Daniel Sinoya"},
            {"label": "046", "value": "Joel Tondera"},
            {"label": "047", "value": "Maliseni Tulirani"},
            {"label": "048", "value": "Felix Yona"},
            {"label": "049", "value": "Fanuel Yonah"},
            {"label": "050", "value": "Rabson Zabala"},]

@app.callback(
    Output(component_id='cust_month_average_graph', component_property='figure'),
    [Input(component_id='cus_av_month_usage_date_IP', component_property='value'),
     Input('slct_customer_2', 'value')])

def update_cust_month_average_graph(date_value, cust_name):
    string = str(cust_name)
    words = string.split()
    surname = words[-1]
    holder = words[0:-1]
    first_name = words[0]
    #first_name = ""
    #for index in range(0, len(holder)):
    #    if(index==0):
    #        first_name += str(holder[index])
    #    else:
    #        first_name += " " + str(holder[index])
    date = str(date_value)
    month = str(date[5:7])
    
    if(month == "01"):
        M = "January"
    elif(month == "02"):
        M = "February"
    elif(month == "03"):
        M = "March"
    elif(month == "04"):
        M = "April"
    elif(month == "05"):
        M = "May"
    elif(month == "06"):
        M = "June"
    elif(month == "07"):
        M = "July"
    elif(month == "08"):
        M = "August"
    elif(month == "09"):
        M = "September"
    elif(month == "10"):
        M = "October"
    elif(month == "11"):
        M = "November"
    else:
        M = "December"
        
    if(len(date)!=7):   #These lines of code are just used in case of an invalid date input from the user
        y_dont_care = [] #If the date input size is not 7, it is in valid as YYYY-MM has 7 characters
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
        return fig
    
    else:
    
        url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
    
        r = requests.get(url=url, headers = header)
        s = r.content
        df = pd.read_json(s)
        holder = df['results'][0]
        
        usage_url = holder['utilities_url'] + "1/usage/"
        
        start_time = str(date) + "-01T00:00:00"
        
        if(int(date[5:7])==12):
            if(int(date[0:4])<10):
                end_time = str(date[0:3]) + str(int(date[3])+1) + "-01-01T00:00:00"
            else:
                end_time = str(date[0:2]) + str(int(date[2:4])+1) + "-01-01T00:00:00"
        else:
            if(int(date[5:7])<10):
                end_time = str(date[0:6]) + str(int(date[6])+1) + "-01T00:00:00"
            else:
                end_time = str(date[0:5]) + str(int(date[5:7])+1) + "-01T00:00:00"
                      
        url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
        
        r2 = requests.get(url=url2, headers = header)
        s2 = r2.content
        df2 = pd.read_json(s2)
        

        
        if(len(df2))==0:
            x_dont_care = []
            y_dont_care = []
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_dont_care, y=y_dont_care,
                                    mode='lines+markers',
                                    ))
            fig.update_layout(title = "There are no meter readings for this customer on "  + M + " " + str(date[0:4]),
                              )
            return fig
    
        else:
            timestamp = []
            usage_amount = []
            time = []
            usage = []
                
            if(month == "04" or month == "06" or month == "09" or month == "11"):
                num = 30
            elif(month == "02" and int(date[0:4])%4==0):
                num = 29
            elif(month == "02" and int(date[0:4])%4!=0):
                num = 28
            else:
                num = 31
            
            for index in range(0,len(df2['timestamp'])):
                timestamp.append(str(df2['timestamp'][index]))
                usage_amount.append(df2['usage'][index])
                    
            for index in range(0,24):
                if(index<10):
                    a = "0" + str(index)
                else:
                    a = str(index)
                temp = a + ":00:00+00:00"
                #temp = str(a[0]) + str(a[1]) + ":00:00+00:00"
                amount = 0
                temptime = str(a[0]) + str(a[1]) + ":00:00"
                for count in range(0,len(timestamp)):
                    holder = timestamp[count]
                    if(temp == holder[11:26]):
                        amount += float(usage_amount[count])
                        continue
                    else:
                        continue
                usage.append(amount/num)
                time.append(temptime)


            title =  "An Individual Customer's Average Daily Load Profile Usage for " + M + " " + str(date[0:4])
    
            FillSpreadSheet(title, "Time", "Demand (kWh)", time, usage, "Ind_Customer_Month")  
                
            fig = go.Figure()
    
            fig.add_trace(go.Scatter(x=time, y=usage,
                                    mode='lines+markers',
                                    ))
                
            fig.update_layout(title = "An Individual Customer's Average Daily Load Profile Usage for " + M + " " + str(date[0:4]),
                               xaxis_title='Time',
                               yaxis_title='Demand (kWh)',
                               yaxis_range=[-0.01,max(usage)+0.01])
            
            fig.update_xaxes(
                tickangle = 45)
            
            return fig

@app.callback(
    [Output('my-date-picker-single-2', 'min_date_allowed'),
    Output('my-date-picker-single-2', 'date')],
    [Input('slct_grid_6_1', 'value')]
    )
def update_date_picker(value):
    if value == 1:
        return date(2020, 6, 5), date(C_year, C_month, C_day)
    elif value == 2:
        return date(2022, 9, 21), date(C_year, C_month, C_day)

@app.callback(
    Output('slct_customer', 'options'),
    [Input('slct_grid_6_1', 'value')])

def update_dropdown_options(value):
    if value == 1:
        return [
            {"label": "001", "value": "Zacharia Alfred"},
            {"label": "002", "value": "Dalitso Bizweck"},
            {"label": "003", "value": "Bizzy Bizzy"},
            {"label": "004", "value": "Zipi Chadinga"},
            {"label": "005", "value": "Clodio Chagona"},
            {"label": "006", "value": "Stephano Chagona"},
            {"label": "007", "value": "Matilda Chagontha"},
            {"label": "008", "value": "Sainet Chemtila"},
            {"label": "009", "value": "Layton Chidavu"},
            {"label": "010", "value": "Lucia Chikapa"},
            {"label": "011", "value": "St John's Cathoric church"},
            {"label": "012", "value": "Seba Eliko"},
            {"label": "013", "value": "Vester Everson"},
            {"label": "014", "value": "Agatha Evesi"},
            {"label": "015", "value": "Wisdory Freizer"},
            {"label": "016", "value": "Lameck Galion"},
            {"label": "017", "value": "George Gilibati"},
            {"label": "018", "value": "Daudi Gondwa"},
            {"label": "019", "value": "Eliko Gonthi"},
            {"label": "020", "value": "Robert Gwafali"},
            {"label": "021", "value": "Chrisy Helemesi"},
            {"label": "022", "value": "Fedrick Jumbe"},
            {"label": "023", "value": "Jovelo Justin"},
            {"label": "024", "value": "Flescot R Kalambo"},
            {"label": "025", "value": "Davie Kamayaya"},
            {"label": "026", "value": "James Kamkwamba"},
            {"label": "027", "value": "Stampa Kamkwamba"},
            {"label": "028", "value": "Alex Kapingasa"},
            {"label": "029", "value": "Yohane Lipenga"},
            {"label": "030", "value": "Zakeyo Lipenga"},
            {"label": "031", "value": "Kelita Luciano"},
            {"label": "032", "value": "Lameck Luka"},
            {"label": "033", "value": "Richard Lyton"},
            {"label": "034", "value": "Lameki Malota"},
            {"label": "035", "value": "Noel Malota"},
            {"label": "036", "value": "Deborah Mangochi"},
            {"label": "037", "value": "Sedonia Mangochi"},
            {"label": "038", "value": "Elenata Mike"},
            {"label": "039", "value": "Agatha Miliano"},
            {"label": "040", "value": "Evinesi Miliano"},
            {"label": "041", "value": "Chinasi Mofati"},
            {"label": "042", "value": "Conrad Mpeketula"},
            {"label": "043", "value": "Alick Mphemvu"},
            {"label": "044", "value": "Linda Msowa"},
            {"label": "045", "value": "Maliko Mulanje"},
            {"label": "046", "value": "Gibson Mvula"},
            {"label": "047", "value": "Aujenia Nicolus"},
            {"label": "048", "value": "Peter Justin Nyale"},
            {"label": "049", "value": "Bizweck Record"},
            {"label": "050", "value": "Ntandamula primary school"},
            {"label": "051", "value": "Lewis Semiyano"},
            {"label": "052", "value": "Bizweck Shalifu"},
            {"label": "053", "value": "Rodreck Sipiliano"},
            {"label": "054", "value": "Kinlos Spiliano"},
            {"label": "055", "value": "Nickson Spiliano"},
            {"label": "056", "value": "Tobias Spiliano"},
            {"label": "057", "value": "Patrick Sugar"},
            {"label": "058", "value": "Stephano Tobias"},
            {"label": "059", "value": "Luciano Veleliyano"},
            {"label": "060", "value": "Konoliyo Zipi"},]
    elif value == 2:
        return [
            {"label": "001", "value": "Kalekeni Amosi"},
            {"label": "002", "value": "Chiwaula Botoman"},
            {"label": "003", "value": "Chilankhwazi CCAP Church"},
            {"label": "004", "value": "Alfred Chagomerana"},
            {"label": "005", "value": "Judith Charles Msyomera"},
            {"label": "006", "value": "Filipina Chilima"},
            {"label": "007", "value": "Yuda Chilima Kachigamba"},
            {"label": "008", "value": "Leckson Chimphanga"},
            {"label": "009", "value": "Julius Chionetsero"},
            {"label": "010", "value": "Napilira Chiwaula"},
            {"label": "011", "value": "Osman Edward"},
            {"label": "012", "value": "Daniel Esau"},
            {"label": "013", "value": "Elena Fackson"},
            {"label": "014", "value": "Kondwani Faison"},
            {"label": "015", "value": "Kenedy Fanuel"},
            {"label": "016", "value": "Godfrey Frackson"},
            {"label": "017", "value": "Jefrem Harry"},
            {"label": "018", "value": "Kalumbi Hendreson"},
            {"label": "019", "value": "Chionetsero Isaac"},
            {"label": "020", "value": "Rashid Jawadu 1"},
            {"label": "021", "value": "Rashid Jawadu 2"},
            {"label": "022", "value": "Rashid Jawadu 3"},
            {"label": "023", "value": "Monica Kachigamba"},
            {"label": "024", "value": "Yuda Kachigamba"},
            {"label": "025", "value": "Petros Kadaola"},
            {"label": "026", "value": "Nickson Kandulu"},
            {"label": "027", "value": "Esau Khudze"},
            {"label": "028", "value": "Gvh Kudembe"},
            {"label": "029", "value": "Uledi Kumbirani"},
            {"label": "030", "value": "George Mangochi"},
            {"label": "031", "value": "Julius Maulana"},
            {"label": "032", "value": "Maganizo Mawandiwe"},
            {"label": "033", "value": "Esau Mazengera"},
            {"label": "034", "value": "Chindikani Msyali"},
            {"label": "035", "value": "Charles Msyomera"},
            {"label": "036", "value": "Johans Namale"},
            {"label": "037", "value": "Chancy Nelson Chisale"},
            {"label": "038", "value": "Mailosi Nkoza"},
            {"label": "039", "value": "Mphika Primary school"},
            {"label": "040", "value": "Hezekia Pwetekani"},
            {"label": "041", "value": "Kachule Saad"},
            {"label": "042", "value": "Thauzeni Sakwiya"},
            {"label": "043", "value": "Nezesi Saliyele"},
            {"label": "044", "value": "Chisomo Sinkaika"},
            {"label": "045", "value": "Daniel Sinoya"},
            {"label": "046", "value": "Joel Tondera"},
            {"label": "047", "value": "Maliseni Tulirani"},
            {"label": "048", "value": "Felix Yona"},
            {"label": "049", "value": "Fanuel Yonah"},
            {"label": "050", "value": "Rabson Zabala"},]

@app.callback(
    Output(component_id='cust_on_day_graph', component_property='figure'),
    [Input(component_id='my-date-picker-single-2', component_property='date'),
     Input('slct_customer', 'value')])

def update_cust_on_day_graph(date_value, cust_name): 
    
    string = str(cust_name) #These lines are used to split the customers name into first and surname
    words = string.split() #They need to be split so that the url will change based on what customer has been selected by the user
    surname = words[-1]
    holder = words[0:-1]
    first_name = ""
    for index in range(0, len(holder)):
        if(index==0):
            first_name += str(holder[index])
        else:
            first_name += " " + str(holder[index])
    date = date_value

    url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
    
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)
    holder = df['results'][0]
    
    usage_url = holder['utilities_url'] + "1/usage/"
    
    start_time = date + "T00:00:00"
    
    if((int(date[5:7])==1 or int(date[5:7])==3 or int(date[5:7])==5 or int(date[5:7])==7 or
        int(date[5:7])==8 or int(date[5:7])==10) and int(date[8:10])==31):
        if(int(date[5:7])<9):
                end_time = date[0:6] + str(int(date[6])+1) + "-01T00:00:00"
        else:
                end_time = date[0:5] + str(int(date[5:7])+1) + "-01T00:00:00"
    elif((int(date[5:7])==4 or int(date[5:7])==6 or int(date[5:7])==9 or int(date[5:7])==11) and int(date[8:10])==30):    
        if(int(date[5:7])<9):
                end_time = date[0:6] + str(int(date[6])+1) + "-01T00:00:00"
        else:
                end_time = date[0:5] + str(int(date[5:7])+1) + "-01T00:00:00"
    elif(int(date[0:4])%4==0 and int(date[5:7])==2 and int(date[8:10])==29):
        end_time = date[0:6] + str(int(date[6])+1) + "-01T00:00:00"
    elif(int(date[0:4])%4!=0 and int(date[5:7])==2 and int(date[8:10])==28):
        end_time = date[0:6] + str(int(date[6])+1) + "-01T00:00:00"
    elif(int(date[5:7])==12 and int(date[8:10])==31):
        end_time = str(int(date[0:4])+1) + "-01-01T00:00:00"
    else:
        if(int(date[8:10])<9):
                end_time = date[0:9] + str(int(date[9])+1) + "T00:00:00"
        else:
                end_time = date[0:8] + str(int(date[8:10])+1) + "T00:00:00"
                  
    url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
    
    r2 = requests.get(url=url2, headers = header)
    s2 = r2.content
    df2 = pd.read_json(s2)
    
    timestamp = []
    usage_amount = []
    time = []
    
    if(len(df2)==0):
        x_dont_care = []
        y_dont_care = []
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_dont_care, y=y_dont_care,
                                mode='lines+markers',
                                ))
        fig.update_layout(title = "There are no meter readings for this customer on" + str(date),
                          )
        return fig
    else:
        for index in range(0,len(df2['timestamp'])):
            timestamp.append(str(df2['timestamp'][index]))
            usage_amount.append(df2['usage'][index])
            
        for index in range(0,len(timestamp)):
            temp = timestamp[index]
            time.append(temp[11:19])
        
    title =  "An Individual Customer's usage on " + date
    
    FillSpreadSheet(title, "Time", "Demand (kWh)", time, usage_amount, "Ind_Customer_Day")  
        
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=usage_amount,
                            mode='lines+markers',
                            ))
        
    fig.update_layout(title ="An Individual Customer's usage on " + date,
                       xaxis_title=url2,
                       yaxis_title='Demand (kWh)',
                       yaxis_range=[-0.01,max(usage_amount)+0.01])
    
    fig.update_xaxes(
        tickangle = 45)
    
    return fig
    
@app.callback(
    [Output('my-date-picker-range-3', 'min_date_allowed'),
    Output('my-date-picker-range-3', 'date')],
    [Input('slct_grid_3_3', 'value')]
    )
def update_date_picker(value):
    if value == 1:
        return date(2020, 6, 5), date(C_year, C_month, C_day)
    elif value == 2:
        return date(2022, 9, 21), date(C_year, C_month, C_day)

@app.callback(
    Output(component_id='my_av_load_graph', component_property='figure'),
    Output('range_alert','is_open'),
    [Input(component_id='my-date-picker-range-3', component_property='start_date'),
     Input('my-date-picker-range-3','end_date'),
     Input('slct_grid_3_3', 'value'),
     Input('slct_user_av', 'value'),
     Input('TorU','value')],
    [State('range_alert','is_open')])


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
    
    if (num==0) or (num>40):
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
    dfC = pd.read_json(s)
    
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
        df2 = pd.read_json(s2)
                                
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
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            
            if df2.empty:
                continue
            
            count+=1
            
            #This is (business + institutions) usage - to be taken away
            for index in range(0,len(df2['timestamp'])):
                take_away_usage[index] += df2['usage'][index]
                
                
        total_url= "https://api.steama.co/sites/26385/utilities/1/usage/" + "?start_time=" + start_time + "&end_time=" + end_time

            
        r3 = requests.get(url=total_url, headers = header)
        s3 = r3.content
        df3 = pd.read_json(s3)
         
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
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            
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
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            
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
    
    return fig

@app.callback(
    [Output('my-date-picker-single-5', 'min_date_allowed'),
    Output('my-date-picker-single-5', 'date')],
    [Input('slct_grid_4_1', 'value')]
    )
def update_date_picker(value):
    if value == 1:
        return date(2020, 6, 5), date(C_year, C_month, C_day)
    elif value == 2:
        return date(2022, 9, 21), date(C_year, C_month, C_day)
         
@app.callback(
    Output(component_id='my_peak_graph', component_property='figure'),
    Input(component_id='my-date-picker-single-5', component_property='date'),
    Input('slct_grid_4_1', 'value'))

def update_peak_graph(date_value, site):
    
    date = str(date_value)
    month = date[5:7]
    site = site
    
    start_time = str(date) + "-01T00:00:00"
    site_name = " "


    if(int(date[5:7])==12):
        end_time = str(int(date[0:4])+1) + "-01-01T00:00:00"
    else:
        if(int(date[5:7])<9):
            end_time = str(date[0:6]) + str(int(date[6])+1) + "-01T00:00:00"
        else:
            end_time = str(date[0:5]) + str(int(date[5:7])+1) + "-01T00:00:00"
    
    #Changing the start time so that only month and year included so that start time is the start of the month
    start_time = str(date[0:7]) + "-01T00:00:00"    

    if(site == 1):
        url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
        site_name = "Mthembanji"
    elif(site == 2):
        url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time 
        site_name = "Kudembe"                          
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)
        
    if(month == "01"):
        M = "January"
    elif(month == "02"):
        M = "February"
    elif(month == "03"):
        M = "March"
    elif(month == "04"):
        M = "April"
    elif(month == "05"):
        M = "May"
    elif(month == "06"):
        M = "June"
    elif(month == "07"):
        M = "July"
    elif(month == "08"):
        M = "August"
    elif(month == "09"):
        M = "September"
    elif(month == "10"):
        M = "October"
    elif(month == "11"):
        M = "November"
    else:
        M = "December"
            
    if(month == "04" or month == "06" or month == "09" or month == "11"):
        num = 30
    elif(month == "02" and int(date[0:4])%4==0):
        num = 29
    elif(month == "02" and int(date[0:4])%4!=0):
        num = 28
    else:
        num = 31
    
    if(len(df)==0):
        y_dont_care = []
        x_dont_care = []
        for index in range(1,num+1):
            y_dont_care.append(0)
            x_dont_care.append(index)
                
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_dont_care, y=y_dont_care,
                            mode='lines+markers',
                            ))
 
        fig.update_layout(title = "Peak Loads for " + str(M) + " " + str(date[0:4]) + " (" + str(site_name) + ")",
                          xaxis_title='Date',
                          yaxis_title='Peak Demand (kWh)')  
        return fig
            
    else:
        timestamp = []
        usage_amount = []
        
        for index in range(0,len(df['timestamp'])):
            timestamp.append(str(df['timestamp'][index]))
            usage_amount.append(df['usage'][index])
                
        temp = []
        peaks = []
        clock = []
        clock2 = []
        x = []
        temporary = str(timestamp[0])
        i = int(temporary[8:10])
        date_index = i
        
        for j in range(0,24):
            hold = str(j) + ":00:00"
            clock2.append(datetime.datetime.strptime(hold, '%H:%M:%S').time())
        
        while(i<=num):
                
            for index in range(0,len(timestamp)):
                temptime = timestamp[index]
                if(i==int(temptime[8:10])):
                    temp.append(usage_amount[index])
                else:
                    continue
            
            if(len(temp)==0):
                temp.clear()
                i+=1
                date_index+=1
            else:
                peaks.append(max(temp))   
                
                for counter in range(0,len(timestamp)):
                    holder = str(timestamp[counter])
                    if(usage_amount[counter]==max(temp) and int(holder[8:10])==i):
                        date_time_obj = datetime.datetime.strptime(holder[11:19], '%H:%M:%S')
                        clock.append(date_time_obj.time())
                        x.append(date_index)
                        date_index+=1
                        break
                    else:
                        continue  
                
                i+=1
                temp.clear()  

        title = "Peak Loads for " + str(M) + " " + str(date[0:4]) + " (" + str(site_name) + ")"
    
        FillSpreadSheet(title, "Day", "Peak Demand (kWh)", x, peaks, "Peaks_Month") 
                
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=x, y=peaks,
                            mode='lines+markers',
                            ))
            
        fig.update_layout(title ="Peak Loads for " + str(M) + " " + str(date[0:4]) + " (" + str(site_name) + ")",
                          xaxis_title='Day',
                          yaxis_title='Peak Demand (kWh)', 
                          xaxis = dict(
                        tickmode = 'linear',
                        tick0 = 1,
                        dtick = 1),
                          xaxis_range=[1,num],
                          yaxis_range=[-0.02,max(peaks)+0.02])
        return fig

@app.callback(
    Output('slct_year_4_2', 'options'),
    [Input('slct_grid_4_2', 'value')])
def update_dropdown(slct_grid_4_2):
    if slct_grid_4_2 == 1:
        return [
            {"label": "2020", "value": "2020"},
            {"label": "2021", "value": "2021"},
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]
    else:
        return [
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]

@app.callback(
    Output(component_id='my_peak_graph_2', component_property = 'figure'),
    Input(component_id ='slct_year_4_2', component_property ='value'),
    Input('slct_grid_4_2', 'value'))

def update_peak_graph_2(date, site):

    date = str(date)
    site = site
    site_name = ""
    
    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00" 
    
    timestamp = []
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]  
    usage = []
    
    if(site == 1):
        site_name = "Mthembanji"
        url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
    elif(site == 2):
        site_name = "Kudembe"
        url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time

    r = requests.get(url, headers = header)
    s = r.content
    df = pd.read_json(s)
            
    for index in range(0,len(df['timestamp'])):
                        usage.append(df['usage'][index])
                        timestamp.append(df['timestamp'][index])
    
    peaks=[]
    
    for i in range(1,13):
        temp=[0]*365
        for index in range (0, len(timestamp)):
            temptime = str(timestamp[index])
            if(i==int(temptime[5:7])):
                temp.append(float(usage[index]))
        max_value = max(temp)
        peaks.append(max_value)
        
    title = "Peak Loads for " + str(start_time[0:4]) + " (" + str(site_name) + ")"
    
    FillSpreadSheet(title, "Month", "Peak Demand (kWh)", time, peaks, "Peaks_Year")    
    
    fig = go.Figure()
        
    fig.add_trace(go.Scatter(x=time, y=peaks,
                            mode='lines+markers',
                            ))
            
    fig.update_layout(title ="Peak Loads for " + str(start_time[0:4]) + " (" + str(site_name) + ")",
                        xaxis_title='Month',
                        yaxis_title='Peak Demand (kWh)', 
                        xaxis = dict(
                        tickmode = 'linear',
                        tick0 = 1,
                        dtick = 1),
                        yaxis_range=[-0.02,max(peaks)+0.02])
    return fig

@app.callback(
    Output('slct_year_1_1', 'options'),
    [Input('slct_grid_1_1', 'value')])
def update_dropdown(slct_grid_1_1):
    if slct_grid_1_1 == 3:
        return [
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]
    else:
        return [
            {"label": "2020", "value": "2020"},
            {"label": "2021", "value": "2021"},
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]
# revenue xxx 
@app.callback(
    Output(component_id='my_graph_1', component_property='figure'),
    [Input(component_id='slct_year_1_1', component_property='value'),
     Input('slct_user_1_1','value'),
     Input('TorA','value'),
     Input('slct_grid_1_1','value')])

def update_graph(option_slctd, bttn1, bttn2, site):
    
    div = bttn1
    div2 = bttn2
    site = site

    if(div2==1):
        T = "Total Revenue "
        L = "Total Revenue (USD)"
    else:
        T = "ARPU "
        L = "ARPU (USD)"
        
    if (div==1):
        T2="All Users"
    elif(div==2):
        T2="Residential Users"
    elif (div==3):
        T2="Business Users"
    else:
        T2="Institutional Users"
    
    url_ER = "https://api.steama.co/exchange-rates/"                     
    r = requests.get(url=url_ER, headers = header)
    s = r.content
    df_ER = pd.read_json(s)

    for index in range(len(df_ER['rate'])):
        if(df_ER['source'][index]=='MWK' and df_ER['target'][index]=='USD'):
            ER = df_ER['rate'][index]
            break
        else:
            continue
    
    date = option_slctd

    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00" 
   
    #request to customer list
    #url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=110"
    if site == 2:
        url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=61&&site&site_id=26385"
    elif site == 3:
        url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=50&&site&site_id=26678"
            
    r = requests.get(url=url, headers = header)
    s = r.content
    #converting json string to a panda object
    dfC = pd.read_json(s)
    
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
    all_cust_fnames= cust_fnames_bus+cust_fnames_ins+cust_fnames_res
    

    leap_year_check = int(date)
    
    if (leap_year_check % 4 == 0):
        daily_revenue = [0]*366
        total_daily_revenue=[0]*366
        take_away_revenue=[0]*366
    else:
        daily_revenue = [0]*365
        total_daily_revenue=[0]*365
        take_away_revenue=[0]*365
        
   
    count=0
    timestamp = []
    monthly_revenue=[]
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    
    
    #This data frame is required to append the timestamp array
    #This is to ensure that the timestamp array does not have 0s
    #This can occur if that last get request is to a customer that has missing timestamp readings
    #This link however does not have missing timestamps

    if(site == 2):
        site_url = "https://api.steama.co/sites/26385/revenue/" + "?start_time=" + start_time + "&end_time=" + end_time 
        rT = requests.get(url=site_url, headers = header)
        sT = rT.content
        dfT = pd.read_json(sT)
        site_name = "Mthembanji"
    elif(site == 3):
        site_url = "https://api.steama.co/sites/26678/revenue/" + "?start_time=" + start_time + "&end_time=" + end_time
        rT = requests.get(url=site_url, headers = header) 
        sT = rT.content
        dfT = pd.read_json(sT)     
        site_name = "Kudembe"               
    
    if (div==1):
        if(site == 2):
            url = "https://api.steama.co/sites/26385/revenue/" + "?start_time=" + start_time + "&end_time=" + end_time 
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            site_name = "Mthembanji"
        elif(site == 3):
            url = "https://api.steama.co/sites/26678/revenue/" + "?start_time=" + start_time + "&end_time=" + end_time  
            r = requests.get(url=url, headers = header) 
            s = r.content
            df = pd.read_json(s)    
            site_name = "Kudembe"               
        
        for index in range(0,len(df['timestamp'])):
            if (div2==1):
                daily_revenue[index] += df['revenue'][index]
            else:
                daily_revenue[index] += (df['revenue'][index])/len(all_cust_fnames) #60 or 50
                
            
    elif (div==2):
        
        for index in range (0,len(cust_fnames_bus_ins)):
            
            first_name=cust_fnames_bus_ins[index]
            surname=cust_snames_bus_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name


            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['revenue_url']
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)

            if df2.empty:
                continue
            
            count+=1 
            
            for index in range(0,len(df2['timestamp'])):
                nth_day = convert_nth_day(df2['timestamp'][index])
                take_away_revenue[nth_day - 1 ]+=(df2['revenue'][index])
           
        if(site == 2):
            url3 = "https://api.steama.co/sites/26385/revenue/" + "?start_time=" + start_time + "&end_time=" + end_time 
            r3 = requests.get(url=url3, headers = header)
            s3 = r3.content
            df3 = pd.read_json(s3)
            site_name = "Mthembanji"
        elif(site == 3):
            url3 = "https://api.steama.co/sites/26678/revenue/" + "?start_time=" + start_time + "&end_time=" + end_time 
            r3 = requests.get(url=url3, headers = header)   
            s3 = r3.content
            df3 = pd.read_json(s3)   
            site_name = "Kudembe"                
        
        for index in range(0,len(df3['timestamp'])):
            total_daily_revenue[index]+=df3['revenue'][index]
            
        #Now taking away
        for index in range(0,len(df3['timestamp'])):
            if (div2==1):
                daily_revenue[index]+=total_daily_revenue[index] - take_away_revenue[index]
            else:
                daily_revenue[index]+=(total_daily_revenue[index] - take_away_revenue[index])/count


    elif (div==3):
        for index in range(0,len(cust_fnames_bus)):
            first_name=cust_fnames_bus[index]
            surname=cust_snames_bus[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name


            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]

            usage_url = holder['revenue_url']
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            
            if df2.empty:
                continue
            
            count+=1 
            
            for index in range(0,len(df2['timestamp'])):
                nth_day = convert_nth_day(df2['timestamp'][index])
                if (div2==1):
                    daily_revenue[nth_day - 1 ]+=(df2['revenue'][index])
                else:
                    daily_revenue[nth_day - 1]+=((df2['revenue'][index])/count)
    
    else:
        for index in range(0,len(cust_fnames_ins)):
            first_name=cust_fnames_ins[index]
            surname=cust_snames_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name


            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            

            usage_url = holder['revenue_url']
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)

            if df2.empty:
                continue
            
            count+=1 
            
            for index in range(0,len(df2['timestamp'])):
                nth_day = convert_nth_day(df2['timestamp'][index])
                if (div2==1):
                    daily_revenue[nth_day - 1]+=(df2['revenue'][index])
                else:
                    daily_revenue[nth_day - 1]+=((df2['revenue'][index])/count)   
    
    
    for index in range(0,len(dfT['timestamp'])):
            timestamp.append(str(dfT['timestamp'][index])) 
            
    for i in range(1,13):
        
        amount = 0

        # if site == 2 and date == "2020" and (div == 3 or div == 4):
        #     holder = 192
        if site == 3 and date == "2022" and (div == 3 or div == 4):
            holder = 271
        else:
            holder = 0

        for index in range(0,len(timestamp)):
            temptime = timestamp[index]
            if(i==int(temptime[5:7])):
                amount += (float(daily_revenue[index + holder])*ER)
            else:
                continue     
        
        if(amount==0):
            monthly_revenue.append(0) 
        else:    
            monthly_revenue.append(amount)
            amount = 0
    
    
    title = T + " for " + T2 + " (" + str(site_name) + ")"
    
    
    FillSpreadSheet(title, "Month", "Revenue (USD)", time, monthly_revenue, "Revenue")

    
    dff = pd.DataFrame(
        {"Month" : time,
         L : monthly_revenue,
        })    
    
    fig = px.bar(dff, x="Month", y=L, title = T + "for " + T2 + " During " + str(date) + " (" + str(site_name) + ")")
    
    return fig

# Callback due to changing inputs (user selecting options)
# Inputs are - user selecting date + user category + Total/Average

@app.callback(
    [Output('my-date-picker-single', 'min_date_allowed'),
    Output('my-date-picker-single', 'date')],
    [Input('slct_grid_3_2', 'value')]
    )
def update_date_picker(value):
    if value == 1:
        return date(2020, 6, 5), date(C_year, C_month, C_day)
    elif value == 2:
        return date(2022, 9, 21), date(C_year, C_month, C_day)

@app.callback(
    Output(component_id='my_graph_2', component_property='figure'),
    [Input(component_id='my-date-picker-single', component_property='date'),
     Input('slct_grid_3_2','value'),    #Select which grid to work with
     Input('slct_user_2','value'), 
     Input('TorU_2','value')])

def update_output(date_value, site, bttn1, bttn2):
    
    #Stores value of radioitem - allows checking what option is selected
    site = site
    div = bttn1
    div2 = bttn2
    
    #for graph title later
    if (div2==1):
        L="Total "
    else:
        L="Average "
        
    #stores date in string variable
    date = str(date_value)
    
    #looks complex - this code is just extracting and formatting end time to make get request later
    start_time = date + "T00:00:00"
    if((int(date[5:7])==1 or int(date[5:7])==3 or int(date[5:7])==5 or int(date[5:7])==7 or
        int(date[5:7])==8 or int(date[5:7])==10) and int(date[8:10])==31):
        if(int(date[5:7])<9):
                end_time = date[0:6] + str(int(date[6])+1) + "-01T00:00:00"
        else:
                end_time = date[0:5] + str(int(date[5:7])+1) + "-01T00:00:00"
    elif(int(date[5:7])==12 and int(date[8:10])==31):
        end_time = str(int(date[0:4])+1) + "-01-01T00:00:00"
    elif((int(date[5:7])==4 or int(date[5:7])==6 or int(date[5:7])==9 or int(date[5:7])==11) and int(date[8:10])==30):    
        if(int(date[5:7])<9):
                end_time = date[0:6] + str(int(date[6])+1) + "-01T00:00:00"
        else:
                end_time = date[0:5] + str(int(date[5:7])+1) + "-01T00:00:00"
    elif(int(date[0:4])%4==0 and int(date[5:7])==2 and int(date[8:10])==29):
        end_time = date[0:6] + "3-01T00:00:00"
    elif(int(date[0:4])%4!=0 and int(date[5:7])==2 and int(date[8:10])==28):
        end_time = date[0:6] + "3-01T00:00:00"
    else:
        if(int(date[8:10])<9):
                end_time = date[0:9] + str(int(date[9])+1) + "T00:00:00"
        else:
                end_time = date[0:8] + str(int(date[8:10])+1) + "T00:00:00"
                                                    
    #request to customer list
    url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=110"
            
    r = requests.get(url=url, headers = header)
    s = r.content
    #converting json string to a panda object
    dfC = pd.read_json(s)
    
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
    total_hourly_usage=[0]*24
    take_away_usage = [0]*24
    hourly_usage = [0]*24
    timestamp = []
    time = [] 
    count=0
   
    if(div==1):
        T = "All Users "
        #Select the API for the correct site
        if (site == 1):
            url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Mthembanji"
        elif (site == 2):
            url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Kudembe"

        r = requests.get(url=url, headers = header)
        s = r.content
        df2 = pd.read_json(s)
        
        #iterates through n number of times (n - number of readings )
        for index in range(0,len(df2['timestamp'])):
            if (div2==1):
                hourly_usage[index]+=(df2['usage'][index]) 
            else:
                hourly_usage[index]+=(df2['usage'][index])/len(all_cust_fnames) #divides by no. of user to get avg

    
    elif (div==2):

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"

        T = "Residential Users "
        
        #Get requests will be made to ins & bus customers then taken away from total 
        #Residential = Total - (Businesses + Institutional)
        #Less get requests -> faster
        for index in range(0,len(cust_fnames_bus_ins)):
            first_name=cust_fnames_bus_ins[index]
            surname=cust_snames_bus_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            
            if df2.empty:
                continue
            
            count+=1             
            #This is (business + institutions) usage - to be taken away
            for index in range(0,len(df2['timestamp'])):
                take_away_usage[index] += df2['usage'][index]
                
                
        total_url= "https://api.steama.co/sites/26385/utilities/1/usage/" + "?start_time=" + start_time + "&end_time=" + end_time

            
        r3 = requests.get(url=total_url, headers = header)
        s3 = r3.content
        df3 = pd.read_json(s3)
         
        #Filling total usage array          
        for index in range(0,len(df3['timestamp'])):
                        total_hourly_usage[index]+=(df3['usage'][index])
        
        #Now taking away
        for index in range(0,len(df2['timestamp'])):
            if (div2==1):
                hourly_usage[index]=total_hourly_usage[index] - take_away_usage[index]
            else:
                hourly_usage[index]=(total_hourly_usage[index] - take_away_usage[index])/count
    
    # Similar process for businesses & institutions
    # Get requests to business/institution users and filling arrays
    # No taking away this time
    elif (div==3):

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"

        T = "Business Users "
        for index in range(0,len(cust_fnames_bus)):
            first_name=cust_fnames_bus[index]
            surname=cust_snames_bus[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            
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

        T= "Institutional Users " 
        
        for index in range(0,len(cust_fnames_ins)):
            first_name=cust_fnames_ins[index]
            surname=cust_snames_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)
            if df2.empty:
                continue
            
            count+=1 
            
            for index in range(0,len(df2['timestamp'])):
                if (div2==1):
                    hourly_usage[index] += df2['usage'][index]
                else:
                    hourly_usage[index] += df2['usage'][index]/count
    
    #Append used here instead of +=
    #This is because we only need to change array once, no iteration
    for index in range(0,len(df2['timestamp'])):
                timestamp.append(str(df2['timestamp'][index]))

    #Formatting time array for suitable axis
    for index in range(0,24):
                if(index<10):
                    a = "0" + str(index)
                else:
                    a = str(index)
                temp = a + ":00:00+00:00"
                time.append(temp[0:8])
                
    title = L + "Load Profile for " + T + "on " + str(date) + " (" + str(site_name) + ")"
    
    FillSpreadSheet(title, "Time", "Demand (kWh)", time, hourly_usage, "Load_Profile_Day")
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=hourly_usage,
                        mode='lines+markers',
                        ))
    
    fig.update_layout(title = L + "Load Profile for " + T + "on " + str(date) + " (" + str(site_name) + ")",
                   xaxis_title='Time',
                   yaxis_title='Demand (kWh)')
    
    return fig

@app.callback(
    Output(component_id='load_profile_year', component_property='figure'),
    [Input('slct_user_3_1','value'),
    Input('slct_grid_3_1','value')])

def Load_year(bttn, site):
    div = bttn
    site = site
    
    df = pd.read_excel('read.xlsx')
    
    hour=[]
    mean=[]
    median=[]
    lower=[]
    upper=[]

    hour = df['Hour'].tolist()
    
    if (div==1):
        mean = df['Tot_Mean'].tolist()
        median = df['Tot_Median'].tolist()
        lower = df['Tot_Low'].tolist()
        upper = df['Tot_High'].tolist()
        category = "All"
    elif (div==2):
        mean = df['Res_Mean'].tolist()
        median = df['Res_Median'].tolist()
        lower = df['Res_Low'].tolist()
        upper = df['Res_High'].tolist()  
        category = "Resdiential"
    elif (div==3):
        mean = df['Bus_Mean'].tolist()
        median = df['Bus_Median'].tolist()
        lower = df['Bus_Low'].tolist()
        upper = df['Bus_High'].tolist()
        category = "Business"
    else:
        mean = df['Ins_Mean'].tolist()
        median = df['Ins_Median'].tolist()
        lower = df['Ins_Low'].tolist()
        upper = df['Ins_High'].tolist()
        category = "Institutional"
        
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=hour, y=mean,
                        mode='lines+markers', name = 'Mean'
                        ))

    fig.add_trace(go.Scatter(x=hour, y=median,
                        mode='lines+markers', name = 'Median'
                        ))

    fig.add_trace(go.Scatter(x=hour, y=lower, 
                        mode='lines+markers', name = 'Lower Sensitivity'
                        ))

    fig.add_trace(go.Scatter(x=hour,y=upper,
                        mode='lines+markers', name = 'Upper Sensitivity'
                        ))
    
    
    fig.update_layout(title ="Load Profile for " + category + " Customers Over a Full Year",
                   xaxis_title='Time',
                   yaxis_title='Demand (kWh)')
    
    return fig           
#Lots of similarity w/ hourly graph
#Main differences include array size as well as sorting the daily readings into monthly readings

@app.callback(
    Output('slct_year', 'options'),
    [Input('slct_grid_2_1', 'value')])
def update_dropdown(slct_grid_2_1):
    if slct_grid_2_1 == 1:
        return [
            {"label": "2020", "value": "2020"},
            {"label": "2021", "value": "2021"},
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]
    else:
        return [
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]
#demand xxx
@app.callback(
    Output(component_id='my_graph_4', component_property='figure'),
    [Input(component_id='slct_year', component_property='value'),
     Input('slct_user_2_1','value'),
     Input('TorU_2_1', 'value'),
     Input('slct_grid_2_1','value')])

def update_output_2(date_value, bttn1, bttn2, site):
    
    #storing year selected by user - string
    date = date_value 
    #formatting date for get request
    # start_time = str(date) + "-01-01T00:00:00"
    # end_time = str(int(date)+1) + "-01-01T00:00:00"
    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00"
    
    div = bttn1
    div2 = bttn2
    site = site
    
    #Changing variable based on option selected - to be used in title
    if (div == 1):
        User_Category = "All Users"
    elif (div == 2):
        User_Category = "Residential Users"
    elif (div == 3):
        User_Category = "Business Users"
    else:
        User_Category = "Institutional Users"
        
    if (div2 == 1):
        Label = "Total"
    else:
        Label="Average"
    

    if site == 1:
        url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=61&&site&site_id=26385"
    elif site == 2:
        url = "https://api.steama.co/customers/?fields=status,foo/?page=1&page_size=50&&site&site_id=26678"
            
    r = requests.get(url = url, headers = header)
    s = r.content
    #converting json string to a panda object
    dfC = pd.read_json(s)
    
    cust_fnames_res=[]
    cust_fnames_bus=[]
    cust_fnames_ins=[]
    
    cust_snames_res=[]
    cust_snames_bus=[]
    cust_snames_ins=[]
    
    
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
                    
    cust_fnames_bus_ins=cust_fnames_bus+cust_fnames_ins
    cust_snames_bus_ins=cust_snames_bus+cust_snames_ins
    
    all_cust_fnames= cust_fnames_bus_ins+cust_fnames_res
    
    leap_year_check = int(date)
    
    if(leap_year_check % 4 ==0):
        daily_usage = [0]*366
        total_daily_usage=[0]*366
        take_away_usage=[0]*366
    else:
        daily_usage = [0]*365
        total_daily_usage=[0]*365
        take_away_usage=[0]*365
   
    
    timestamp = []
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]  
    monthly_usage=[] 
    count=0
    
    if (div==1):
        if site == 1 and date == "2020":
            start_time = "2020-06-05T00:00:00+00:00"
            end_time = "2021-01-01T00:00:00"
        elif site == 2 and date == "2022":
            start_time = "2022-09-21T00:00:00"
            end_time = "2023-01-01T00:00:00"
        if(site == 1):
            url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Mthembanji"
        elif(site == 2):
            url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Kudembe"
            
        r = requests.get(url = url, headers = header)
        s = r.content
        df2 = pd.read_json(s)
      
        for index in range(0,len(df2['timestamp'])):
            if (div2==1):
                daily_usage[index]+=(df2['usage'][index])
            else:
                daily_usage[index]+=(df2['usage'][index])/len(all_cust_fnames)
    
    if (div==2):      
        if site == 1 and date == "2020":
            start_time = "2020-06-05T00:00:00+00:00"
            end_time = "2021-01-01T00:00:00"
        elif site == 2 and date == "2022":
            start_time = "2022-09-21T00:00:00"
            end_time = "2023-01-01T00:00:00"
        for index in range(0,len(cust_fnames_bus_ins)):
            first_name=cust_fnames_bus_ins[index]
            surname=cust_snames_bus_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url = url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)

            if df2.empty:
                continue
            
            count+=1 
            
            for index in range(0,len(df2['timestamp'])):
                nth_day = convert_nth_day(df2['timestamp'][index])
                take_away_usage[nth_day - 1]+=(df2['usage'][index])
        
        if(site == 1):
            total_url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Mthembanji"
        elif(site == 2):
            total_url = "https://api.steama.co/sites/26678/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
            site_name = "Kudembe"

        r3 = requests.get(url = total_url, headers = header)
        s3 = r3.content
        df3 = pd.read_json(s3)
            
        for index in range(0,len(df3['timestamp'])):
                        total_daily_usage[index]+=(df3['usage'][index])
                        
        for index in range(0,len(df2['timestamp'])):
            if (div2==1):
                daily_usage[index]=total_daily_usage[index] - take_away_usage[index]
            else:
                daily_usage[index]=(total_daily_usage[index] - take_away_usage[index])/count
            
                
    if (div==3):
        if site == 1 and date == "2020":
            start_time = "2020-06-05T00:00:00+00:00"
            end_time = "2021-01-01T00:00:00"
        elif site == 2 and date == "2022":
            start_time = "2022-09-21T00:00:00"
            end_time = "2023-01-01T00:00:00"

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"
       
        for index in range(0,len(cust_fnames_bus)):
            first_name=cust_fnames_bus[index]
            surname=cust_snames_bus[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time
            
            r2 = requests.get(url=url2, headers=header)
            s2 = r2.content
            df2 = pd.read_json(s2)
 
            if df2.empty:
                continue
            
            count+=1 
            
            for index in range(0,len(df2['timestamp'])):
                nth_day = convert_nth_day(df2['timestamp'][index])
                if (div2==1):
                    daily_usage[nth_day - 1]+=(df2['usage'][index])
                else:
                    daily_usage[nth_day - 1]+=((df2['usage'][index])/count)


    else:
        if site == 1 and date == "2020":
            start_time = "2020-06-05T00:00:00+00:00"
            end_time = "2021-01-01T00:00:00"
        elif site == 2 and date == "2022":
            start_time = "2022-09-21T00:00:00"
            end_time = "2023-01-01T00:00:00"

        if(site == 1):
            site_name = "Mthembanji"
        elif(site == 2):
            site_name = "Kudembe"

        for index in range(0,len(cust_fnames_ins)):
            first_name=cust_fnames_ins[index]
            surname=cust_snames_ins[index]
            
            url = "https://api.steama.co/customers/?last_name=" + surname + "&first_name=" + first_name
                
            r = requests.get(url=url, headers = header)
            s = r.content
            df = pd.read_json(s)
            holder = df['results'][0]
            
            usage_url = holder['utilities_url'] + "1/usage/"
            url2 = usage_url + "?start_time=" + start_time + "&end_time=" + end_time          
            
            r2 = requests.get(url=url2, headers = header)
            s2 = r2.content
            df2 = pd.read_json(s2)

            if df2.empty:
                continue
            
            count+=1
            
            for index in range(0,len(df2['timestamp'])):
                nth_day = convert_nth_day(df2['timestamp'][index])
                if (div2==1):
                    daily_usage[nth_day - 1]+=(df2['usage'][index])
                else:
                    daily_usage[nth_day - 1]+=((df2['usage'][index])/count)
                

    for index in range(0,len(df2['timestamp'])):
                timestamp.append(str(df2['timestamp'][index]))

    for i in range(1,13):
        
        amount = 0

        if site == 1 and date == "2020" and (div == 3 or div == 4):
            holder = 156
        elif site == 2 and date == "2022" and (div == 3 or div == 4):
            holder = 262
        else:
            holder = 0

        for index in range(0,len(timestamp)):
            temptime = timestamp[index]
            if(i==int(temptime[5:7])):
                amount += (float(daily_usage[index + holder]))
            else:
                continue    

        if(amount==0):
            monthly_usage.append(0) 
        else:    
            monthly_usage.append(amount)
            amount = 0 
            
    title =  Label + " Demand for " + User_Category + " customers for " + str(date) + " (" + str(site_name) + ")"
    FillSpreadSheet(title, "Month", "Demand (kWh)", time, monthly_usage,"Monthly_Demand")
     
    fig = go.Figure()
    
    #######Extra code to plot data as a bar chart /// may be better alternative 
    dff = pd.DataFrame(
        {"Month" : time,
         "Demand (kWh)" : monthly_usage,
        })    
    
    fig = px.bar(dff, x="Month", y="Demand (kWh)", title = Label + " Demand for " + User_Category + " customers for " + str(date) + " (" + str(site_name) + ")")
        
    return fig

@app.callback(
       Output(component_id='my_graph_5', component_property='figure'),
       Input(component_id='my-date-picker-range', component_property='start_date'),
       Input(component_id='my-date-picker-range', component_property='end_date'))

def stateofCharge(start_date,end_date): 
       TOKEN = refreshtoken(r1)
# GET DATA VIA LOOP
       stateOfCharge = []
       
       # start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """

       for i in range(int(start_date[8:10]),int(end_date[8:10])):
              if i < 10: # If date less than 10 to suit YYYY-MM-DD Format
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-0{2}&WithTotal=false".format(start_date[0:4],start_date[5:7],i)
              else:
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=false".format(start_date[0:4],start_date[5:7],i)

              headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
              r = session.get(r,headers=headers2)
              data = r.json()
              stateOfCharge.append(data['set'][i]['batteryStateOfCharge'])
              """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
              Totalconsumption.append(data['set'][i]['totalConsumption']) """
              # print(data['set'][i]['batteryStateOfCharge'])
       # end = time.time()

       # print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (BATTERY STATE OF CHARGE)")
       # print(stateOfCharge)
       date = []
       for i in range(int(start_date[8:10]),int(end_date[8:10])):
           if i < 10:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))
           else:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))
              
              
       title =  'Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
       FillSpreadSheet(title, 'Date' ,'State of Charge (%)', date, stateOfCharge, "SOC_Range")
    
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = date,
                    y = stateOfCharge,
                    mode = 'lines+markers', 
                    name = 'State of Charge'
                ))

       fig.update_layout(
                    title ='Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='{0} days selected'.format((int(end_date[8:10])-int(start_date[8:10]))),
                    yaxis_title='State of Charge (%)',
                    autotypenumbers='convert types',
                    )
       
       return fig 

@app.callback(
       Output(component_id='my_graph_5_1', component_property='figure'),
       Input('slct_user_2','value'))
       

def TotalConsumptionMonth(slct_user_2): 
    TOKEN = refreshtoken(r1)
    #refreshtoken(r1) # Use refresh token as bearer token expires every 5 minutes (SMA sunny portal)  
    # GET DATA VIA LOOP
    TotalConsumption = [0,0,0,0,0,0,0,0,0,0,0,0]
    # start = time.time()
    """print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
    print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
    print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """
    # Only single Get API request required for one year

    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(slct_user_2)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if slct_user_2 == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalConsumption[6+i] = ((value['totalConsumption']/1000))
        elif data is None:
            TotalConsumption[i] = 0
        else: 
            TotalConsumption[i] = ((value['totalConsumption']/1000))
        i = i+1
    """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
    Totalconsumption.append(data['set'][i]['totalConsumption']) """
    # print(data['set'][i]['batteryStateOfCharge'])
    # end = time.time()

    # print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (TOTAL CONSUMPTION)")
    # print(stateOfCharge)
    date = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    
    
    
    title =  'Monthly Consumption (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
    FillSpreadSheet(title, 'Months' ,'Total Consumption (kWh)', date, TotalConsumption,"Consumpton_Year")    
    
    
    fig = px.bar(
        df,
        x = date,
        y = TotalConsumption)
            
    fig.update_layout(
                    title ='Monthly Consumption (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='Months',
                    yaxis_title='Total Consumption (kWh)',
                    autotypenumbers='convert types',
                    )
    
    return fig

@app.callback(
       Output(component_id='my_graph_6', component_property='figure'),
       Input(component_id='my-date-picker-range-2', component_property='start_date'),
       Input(component_id='my-date-picker-range-2', component_property='end_date'))

def stateofCharge(start_date,end_date): 
# GET DATA VIA LOOP
       TOKEN = refreshtoken(r1)
       batteryDischarging = []
       Totalconsumption = []

       # start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """

       for i in range(int(start_date[8:10]),int(end_date[8:10])):
              if i < 10: # If date less than 10 to suit YYYY-MM-DD Format
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-0{2}&WithTotal=false".format(start_date[0:4],start_date[5:7],i)
              else:
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=false".format(start_date[0:4],start_date[5:7],i)

              headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
              r = session.get(r,headers=headers2)
              data = r.json()
              #batteryDischarging.append(data['set'][i]['batteryDischarging'])
              Totalconsumption.append(data['set'][i]['totalConsumption'])
              # print(data['set'][i]['batteryStateOfCharge'])
       # end = time.time()

       # print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (TOTAL CONSUMPTION)")
       # print(Totalconsumption)
       date = []
       for i in range(int(start_date[8:10]),int(end_date[8:10])):
           if i < 10:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))
           else:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))  
              
              
       title =  'Consumption (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
       FillSpreadSheet(title, 'Date' ,'Total Consumption (kWh)', date, Totalconsumption, "Consumption_Range") 
               
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = date,
                    y = Totalconsumption,
                    mode = 'lines+markers',
                                    
                ))
       fig.update_layout(
                    title ='Consumption (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='{0} days selected'.format((int(end_date[8:10])-int(start_date[8:10]))),
                    yaxis_title='Total Consumption (kWh)',
                    autotypenumbers='convert types',
                    )
    
       return fig 

@app.callback(
       Output(component_id='graph_6_1', component_property='figure'),
       Input(component_id='my-date-picker-single-charge', component_property='date'))

def stateofChargeByMin(date): 
       TOKEN = refreshtoken(r1)
# GET DATA VIA LOOP
       stateOfCharge = []
       
       #start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """


       r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=false".format(date[0:4],date[5:7],date[8:10]) 
             

       headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
       r = session.get(r,headers=headers2)
       data = r.json()
       #print(data)

       for value in data['set']:
           if data is None:
               stateOfCharge.append(0)
           else:
               stateOfCharge.append((value['batteryStateOfCharge']))
               #print(value['batteryStateOfCharge'])




       """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
       Totalconsumption.append(data['set'][i]['totalConsumption']) """
       # print(data['set'][i]['batteryStateOfCharge'])
       #end = time.time()

       #print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (BATTERY STATE OF CHARGE 2)")
       #print(stateOfCharge)
       timeframe = []
       for i in range(len(stateOfCharge)):
           timeframe.append(data['set'][i]['time'])  
           
       title =  'Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
       FillSpreadSheet(title, 'Hours' ,'State of Charge(%)', timeframe, stateOfCharge,"SOC_Day") 
           
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = timeframe,
                    y = stateOfCharge,
                    mode = 'lines+markers', 
                    name = 'State of Charge'
                ))

       fig.update_layout(
                    title ='Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='Hours',
                    yaxis_title='State of Charge (%)',
                    autotypenumbers='convert types',
                    )
       
       return fig 

@app.callback(
       Output(component_id='graph_7', component_property='figure'),
       Input(component_id='my-date-picker-single-gen', component_property='date'))

def TotalGenerationDay(date):
     
# GET DATA VIA LOOP
       TOKEN = refreshtoken(r1)
       totalGen = []
       
       #start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """


       r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=false".format(date[0:4],date[5:7],date[8:10]) 
             

       headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
       r = session.get(r,headers=headers2)
       data = r.json()

       #print(data)
       #print(data['set'])
       for value in data['set']:
              totalGen.append(value.get('totalGeneration',0))

       """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
       Totalconsumption.append(data['set'][i]['totalConsumption']) """
       # print(data['set'][i]['batteryStateOfCharge'])   
       #end = time.time()
       #print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (BATTERY STATE OF CHARGE 3)")
       #print(totalGen)
       timeframe = []
       for i in range(len(totalGen)):
              timeframe.append(data['set'][i]['time'])  
              
       title =  'Daily Generation of Microgrid (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
       FillSpreadSheet(title, 'Hours' ,'Generation (kWh)', timeframe, totalGen,"Generation_Day")

               
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = timeframe,
                    y = totalGen,
                    mode = 'lines+markers', 
                    name = 'Generation'
                ))

       fig.update_layout(
                    title ='Daily Generation of Microgrid (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='Hours',
                    yaxis_title='Generation (kWh)',
                    autotypenumbers='convert types',
                    )
       
       return fig 

@app.callback(
    Output('slct_year_3_1', 'options'),
    [Input('slct_grid_3_1', 'value')])
def update_dropdown(slct_grid_3_1):
    if slct_grid_3_1 == 1:
        return [
            {"label": "2020", "value": "2020"},
            {"label": "2021", "value": "2021"},
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]
    else:
        return [
            {"label": "2022", "value": "2022"},
            {"label": "2023", "value": "2023"}
        ]

@app.callback(
       Output(component_id='my_graph_7_1', component_property='figure'),
       Input('slct_year_3_1','value'),
       Input('slct_grid_3_1','value'))
       

def TotalGenerationMonth(slct_year_3_1, site): 
    TOKEN = refreshtoken(r1)
    site = site
    #refreshtoken(r1) # Use refresh token as bearer token expires every 5 minutes (SMA sunny portal)  
    # GET DATA VIA LOOP
    TotalGeneration = [0,0,0,0,0,0,0,0,0,0,0,0]
    # start = time.time()
    """print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
    print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
    print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """
    # Only single Get API request required for one year

    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(slct_year_3_1)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if(site == 1):
            if slct_year_3_1 == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
                TotalGeneration[6+i] = ((value['totalGeneration']/1000))
            elif data is None:
                TotalGeneration[i] = 0
            else: 
                TotalGeneration[i] = ((value['totalGeneration']/1000))
            i = i+1
        elif(site == 2):
            if slct_year_3_1 == 2022: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
                TotalGeneration[6+i] = ((value['totalGeneration']/1000))
            elif data is None:
                TotalGeneration[i] = 0
            else: 
                TotalGeneration[i] = ((value['totalGeneration']/1000))
            i = i+1
    """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
    Totalconsumption.append(data['set'][i]['totalConsumption']) """
    # print(data['set'][i]['batteryStateOfCharge'])
    # end = time.time()

    # print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (TOTAL CONSUMPTION)")
    # print(stateOfCharge)
    date = ["January","February","March","April","May","June","July","August","September","October","November","December"]


    title =  'Monthly Generation (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
    FillSpreadSheet(title, 'Months' ,'Total Generation (kWh)', date, TotalGeneration, "Generation_Year")     
    
    
    fig = px.bar(
        df,
        x = date,
        y = TotalGeneration)
            
    fig.update_layout(
                    title ='Monthly Generation (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='Months',
                    yaxis_title='Total Generation (kWh)',
                    autotypenumbers='convert types',
                    )
    
    return fig

@app.callback(
       Output(component_id='my_graph_6_2', component_property='figure'),
       Input('slct_user_5','value'))
       

def BatStateofChargeMonth(slct_user_5): 
    TOKEN = refreshtoken(r1)
    #refreshtoken(r1) # Use refresh token as bearer token expires every 5 minutes (SMA sunny portal)  
    # GET DATA VIA LOOP
    TotalBatCharging = [0,0,0,0,0,0,0,0,0,0,0,0]
    TotalBatDischarging = [0,0,0,0,0,0,0,0,0,0,0,0]
    # start = time.time()
    """print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
    print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
    print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """
    # Only single Get API request required for one year

    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(slct_user_5)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if slct_user_5 == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalBatCharging[6+i] = (value['batteryCharging']/1000)
            TotalBatDischarging[6+i] = (value['batteryDischarging']/1000)
        elif data is None:
            TotalBatCharging[i] = 0
            TotalBatDischarging[i] = 0
        else: 
            TotalBatCharging[i] = (value['batteryCharging']/1000)
            TotalBatDischarging[i] = (value['batteryDischarging']/1000)
        i = i+1
    """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
    Totalconsumption.append(data['set'][i]['totalConsumption']) """
    # print(data['set'][i]['batteryStateOfCharge'])
    # end = time.time()

    # print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (TOTAL CONSUMPTION)")
    # print(stateOfCharge)
    date = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    
    #title =  'Monthly Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
    #FillSpreadSheet(title, 'Months' ,'Power drawn/feed in by battery counter reading (kWh)', date, [TotalBatCharging,TotalBatDischarging])  

    title =  'Monthly Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId'])
    FillSpreadSheet2(title, 'Month', 'Power Feed in (kWh)' ,'Power Drawn (kWh)', date, TotalBatCharging, TotalBatDischarging, "SOC_Year")     
    
    
    fig = px.bar(
        df,
        x = date,
        y = [TotalBatCharging,TotalBatDischarging],
        barmode = 'group',
        )
    
    fig.update_layout(
                    title ='Monthly Battery State of Charge (Plant {0}):'.format(data_initial['plants'][0]['plantId']),
                    xaxis_title='Months',
                    yaxis_title='Power drawn/feed in by battery counter reading (kWh)',
                    autotypenumbers='convert types',
                    showlegend=True
                    )
    fig['data'][0]['name']='Feed-in' 
    fig['data'][1]['name']='Power drawn by'   
 
    return fig


@app.callback(
    Output(component_id='daily_communications_uptime', component_property='figure'),
    Output(component_id='daily_outages_bar', component_property='figure'),
    Output(component_id='no_days_outages', component_property='figure'),
    [Input(component_id='slct_year', component_property='value')])

def dailyUptime(date_value):
    
    date=date_value 

    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00"
    
    timestamp=[]
    uptime=[]
    
    
    url= "https://api.steama.co/bitharvesters/100144/comms_uptime/" + "?start_time=" + start_time + "&end_time=" + end_time

    r = requests.get(url, headers = header)
    s = r.content
    df = pd.read_json(s)
    
    #filling arrays for all uptime data points
    for index in range(0,len(df['timestamp'])):
                            uptime.append(df['uptime'][index]*100) #convert to %
                            timestamp.append(str(df['timestamp'][index]))
    
    
    #arrays for data points which are considered as outages                   
    timestamp_outages=[]
    uptime_outages=[]
    for index in range(0,len(df['timestamp'])):
                        if (df['uptime'][index]<=0.5): #if less than 0.5
                            uptime_outages.append(df['uptime'][index])
                            timestamp_outages.append(str(df['timestamp'][index])[0:10])
                            
    #Used to calculate the length of each outage - outages that occur on consecutive days are grouped                    
    length_array=[]
    index=0
    limit = 1
    length=1

    for index2 in range (0, len(uptime_outages)-1):

        temp=calc_difference_in_days(timestamp_outages[index],timestamp_outages[index2 + 1])
        if (temp <= limit):
            length+=1
            index2+=1
            limit +=1              
        else:
            length_array.append(length)
            index+=length
            index2+=1
            limit = 1
            length=1
  
    length_array.append(length)   
    
    total_length=0
    for index in range(0,len(length_array)):
        total_length+=length_array[index]
    
    average_length = round(float(total_length/len(length_array)),2)
        
    
    #used to extract the start time of each power outage
    start_times=[]
    
    point=0
    for index in range(0,len(length_array)):  
        if (index==0):
            temp = timestamp_outages[index]
            year = str(temp[0:4])
            month = str(temp[5:7])
            day = str(temp[8:10])
            start_times.append(day + "/" + month + "/" + year)
        else:
            point+=length_array[index - 1]
            temp = timestamp_outages[point]
            year = str(temp[0:4])
            month = str(temp[5:7])
            day = str(temp[8:10])
            start_times.append(day + "/" + month + "/" + year)
            
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    no_of_days=[]
        
    for i in range(1,13):
        count=0
        for index in range (0, len(timestamp_outages)):
            temptime = str(timestamp_outages[index])
            if(i==int(temptime[5:7])):
                count+=1
        no_of_days.append(count)  

          
    title =  "Start Dates and Duration of Outages for " + str(date)
    FillSpreadSheet(title, "Outage Start Date","Duration (days)", start_times , length_array, "Start_Length_Outages")            
    bar = go.Figure()
                       
    dff = pd.DataFrame(
        {"Outage Start Date" : start_times,
         "Duration (days)" : length_array,
        })    
    
    bar = px.bar(dff, x="Outage Start Date", y="Duration (days)", title = "Start Dates and Duration of Outages for " + str(date), text=length_array)                                
    bar.add_hline(y=average_length, line_dash= "dot", line_color = "purple", line_width=4, annotation_text = "average = " + str(average_length) , annotation_font_size=16, annotation_font_color="purple")


    title =  "Number of Days of Outages throughout " + str(date)
    FillSpreadSheet(title, 'Month' ,"Number of Days", months, no_of_days, "No_Days_Outages")  
    
    bar_2 = go.Figure()
                       
    dff = pd.DataFrame(
        {"Month" : months,
         "Number of Days" : no_of_days,
        })    
    
    bar_2 = px.bar(dff, x="Month", y="Number of Days", title = "Number of Days of Outages throughout " + str(date), text=no_of_days)     


    title =  "Communications Uptime for " + str(date)
    FillSpreadSheet(title, 'Days' ,'Uptime (%)', timestamp , uptime, "Daily_Uptime")   
    
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=timestamp, y=uptime,
                        mode='lines+markers',
                        ))
    fig.add_hrect(
    y0="50", y1="0",
    fillcolor="LightSalmon", opacity=0.5,
    layer="below", line_width=0,
    )
    
    fig.update_layout(title = "Communications Uptime for " + str(date),
                   xaxis_title='Month',
                   yaxis_title='Uptime (%)')
    
    return fig, bar, bar_2                           


@app.callback(
    Output(component_id='hourly_communications_uptime', component_property='figure'),
    [Input(component_id='my-date-picker-range', component_property='start_date'),
     Input('my-date-picker-range','end_date')])
     
def hourlyUptime(start_date_value, end_date_value):
    start_date = str(start_date_value)
    end_date = str(end_date_value)
    
    
    num = calc_difference_in_days(start_date,end_date)
    
    if (num==0) or (num>40):
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
        return fig
    
    else:
        pass
    
    
    start_date = str(start_date_value) + "T00:00:00"
    end_date = str(end_date_value) + "T00:00:00"    
    url= "https://api.steama.co/bitharvesters/100144/comms_uptime/" + "?start_time=" + start_date + "&end_time=" + end_date

    r = requests.get(url, headers = header)
    s = r.content
    df = pd.read_json(s)
    
    
    uptime=[]
    timestamp=[]
    #filling arrays for all uptime data points
    for index in range(0,len(df['timestamp'])):
                            uptime.append(df['uptime'][index]*100) #convert to %
                            timestamp.append(str(df['timestamp'][index])) 
                        
    timestamp_outages=[]
    uptime_outages=[]
    for index in range(0,len(df['timestamp'])):
                        if (df['uptime'][index]<=0.0416): #if less than 0.5
                            uptime_outages.append(df['uptime'][index])
                            timestamp_outages.append(str(df['timestamp'][index]))
                            
    #Used to calculate the length of each outage - outages that occur on consecutive days are grouped                    
    length_array=[]
    index=0
    limit = 1
    length=1

    for index2 in range (0, len(uptime_outages)-1):

        temp=calc_difference_in_hours(timestamp_outages[index],timestamp_outages[index2 + 1])
        if (temp <= limit):
            length+=1
            index2+=1
            limit +=1              
        else:
            length_array.append(length)
            index+=length
            index2+=1
            limit = 1
            length=1
  
    length_array.append(length)   

    
    #used to extract the start time of each power outage
    start_times=[]
    
    point=0
    for index in range(0,len(length_array)):  
        if (index==0):
            start_times.append(timestamp_outages[index])
        else:
            point+=length_array[index - 1]
            start_times.append(timestamp_outages[point])

    title =  "Communications Uptime from " + start_date_value + " to " + end_date_value
    FillSpreadSheet(title, 'Time' ,'Uptime (%)', timestamp , uptime, "Hourly_Uptime")   
                                
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=timestamp, y=uptime,
                        mode='lines+markers',
                        ))
    
    fig.update_layout(title = "Communications Uptime from " + start_date_value + " to " + end_date_value,
                   xaxis_title='Time',
                   yaxis_title='Uptime (%)')
    
    return fig                 

@app.callback(
    Output(component_id='batt_temp_month', component_property='figure'),
    Input(component_id='my-date-picker-single', component_property='value'))

def batt_temp_month (date_value):
 
    date = str(date_value)
    month = date[5:7]
    year = date[0:4]

    if(int(date[5:7])==12):
        end_time = str(int(date[0:4])+1) + "-01-01T00:00:00"
    else:
        if(int(date[5:7])<9):
            end_time = str(date[0:6]) + str(int(date[6])+1) + "-01T00:00:00"
        else:
            end_time = str(date[0:5]) + str(int(date[5:7])+1) + "-01T00:00:00"
    
    #Changing the start time so that only month and year included so that start time is the start of the month
    start_time = str(date[0:7]) + "-01T00:00:00"   
    
    if(month == "01"):
        M = "January"
    elif(month == "02"):
        M = "February"
    elif(month == "03"):
        M = "March"
    elif(month == "04"):
        M = "April"
    elif(month == "05"):
        M = "May"
    elif(month == "06"):
        M = "June"
    elif(month == "07"):
        M = "July"
    elif(month == "08"):
        M = "August"
    elif(month == "09"):
        M = "September"
    elif(month == "10"):
        M = "October"
    elif(month == "11"):
        M = "November"
    else:
        M = "December"
            
    if(month == "04" or month == "06" or month == "09" or month == "11"):
        num = 30
    elif(month == "02" and int(date[0:4])%4==0):
        num = 29
    elif(month == "02" and int(date[0:4])%4!=0):
        num = 28
    else:
        num = 31    
        
    if(len(date)!=7):   #These lines of code are just used in case of an invalid date input from the user
        y_dont_care = [] #If the date input size is not 7, it is in valid as YYYY-MM has 7 characters
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
                       yaxis_title='Temperature (°C)')  
        return fig


    readings = db.reference('UsersData/mRxIA4XvqYTmhIEjqfk8ycC02vq1/readings')
    part_readings = readings.order_by_child('timestamp').start_at(start_time).end_at(end_time).get()

    
    timestamp=[]
    temp_batt=[]
    temp_ext=[]
    temp_int=[]
    temp_pcb=[]
    

    for key,value in part_readings.items():
        if (float(value['temp_PCB']) > 100): ##some fake values detected in pcb temp (temp being recorded at 500000)
            temp_batt.append(value['temp_Batt1']) #if detected append all other temps as normal
            temp_ext.append(value['temp_ext'])
            temp_int.append(value['temp_int'])
            temp_pcb.append(28) ##append pcb to 28 - rough avg temp that will have minimal effect on daily average
            timestamp.append(key)
        else:
            temp_batt.append(value['temp_Batt1'])
            temp_ext.append(value['temp_ext'])
            temp_int.append(value['temp_int'])
            temp_pcb.append(value['temp_PCB'])
            timestamp.append(key)
        
    total_temp_batt=[0]*num
    total_temp_ext=[0]*num
    total_temp_int=[0]*num
    total_temp_pcb=[0]*num
    no_of_data_points=[0]*num
    #0 1 2 3 4 5 6 7 8 9  10
    #1 2 3 4 5 6 7 8 9 10 11
    
    days=[]
    
    for index in range(0,num):
        days.append(str(index+1))
        
    
    for index in range (0,num):
        if (index<9):
            current_day = year + "-" + month + "-0" + str(index+1)
        else:
            current_day = year + "-" + month + "-" + str(index+1)
        
        temp_batt_running_total = 0
        temp_ext_running_total = 0
        temp_int_running_total = 0
        temp_pcb_running_total = 0
        data_points_count = 0
        
        for index2 in range(0, len(timestamp)):
            if (current_day == timestamp[index2][0:10]):
                temp_batt_running_total += float(temp_batt[index2])
                temp_ext_running_total += float(temp_ext[index2])
                temp_int_running_total += float(temp_int[index2])
                temp_pcb_running_total += float(temp_pcb[index2])
                data_points_count+=1
        total_temp_batt[index] += temp_batt_running_total
        total_temp_ext[index] += temp_ext_running_total
        total_temp_int[index] += temp_int_running_total
        total_temp_pcb[index] += temp_pcb_running_total
        no_of_data_points[index] += data_points_count

    daily_temp_batt=[]
    daily_temp_ext=[]
    daily_temp_int=[]
    daily_temp_pcb=[]
    
    for index in range(0,len(total_temp_batt)):
        if (no_of_data_points[index]==0):
            daily_temp_batt.append(0)
            daily_temp_ext.append(0)
            daily_temp_int.append(0)
            daily_temp_pcb.append(0)
        else:
            daily_temp_batt.append(total_temp_batt[index]/no_of_data_points[index])
            daily_temp_ext.append(total_temp_ext[index]/no_of_data_points[index])
            daily_temp_int.append(total_temp_int[index]/no_of_data_points[index])
            daily_temp_pcb.append(total_temp_pcb[index]/no_of_data_points[index])


    title =  "Average Battery Temperature for " + M + " " + year
    FillSpreadSheet1(title, 'Days' ,'Batt Temp', 'Ext Temp','Int Temp', 'PCB Temp',  days , daily_temp_batt, daily_temp_ext, daily_temp_ext, daily_temp_pcb, "Batt_Temp_Month")   
    
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=days, y=daily_temp_batt,
                        mode='lines+markers', name = 'Battery'
                        ))
    fig.add_trace(go.Scatter(x=days, y=daily_temp_ext,
                        mode='lines+markers', name = 'External'
                        ))

    fig.add_trace(go.Scatter(x=days, y=daily_temp_int,
                        mode='lines+markers', name = 'Internal'
                        ))

    fig.add_trace(go.Scatter(x=days, y=daily_temp_pcb,
                        mode='lines+markers', name = 'PCB'
                        ))
    
    fig.update_layout(title = "Average Battery Temperature for " + M + " " + year,
                   xaxis_title='Days of The Month',
                   yaxis_title='Temperature (°C)')
    
    return fig   
    
@app.callback(
    Output(component_id='batt_temp_day', component_property='figure'),
    Input(component_id='my-date-picker-single-2', component_property='date'))

def batt_temp_day(date_value):
    start_date=date_value[0:10]

    if((int(start_date[5:7])==1 or int(start_date[5:7])==3 or int(start_date[5:7])==5 or int(start_date[5:7])==7 or
        int(start_date[5:7])==8 or int(start_date[5:7])==10) and int(start_date[8:10])==31):
        if(int(start_date[5:7])<9):
                end_date = start_date[0:6] + str(int(start_date[6])+1) + "-01T00:00:00"
        else:
                end_date = start_date[0:5] + str(int(start_date[5:7])+1) + "-01T00:00:00"
    elif((int(start_date[5:7])==4 or int(start_date[5:7])==6 or int(start_date[5:7])==9 or int(start_date[5:7])==11) and int(start_date[8:10])==30):    
        if(int(start_date[5:7])<9):
                end_date = start_date[0:6] + str(int(start_date[6])+1) + "-01T00:00:00"
        else:
                end_date = start_date[0:5] + str(int(start_date[5:7])+1) + "-01T00:00:00"
    elif(int(start_date[0:4])%4==0 and int(start_date[5:7])==2 and int(start_date[8:10])==29):
        end_date = start_date[0:6] + str(int(start_date[6])+1) + "-01T00:00:00"
    elif(int(start_date[0:4])%4!=0 and int(start_date[5:7])==2 and int(start_date[8:10])==28):
        end_date = start_date[0:6] + str(int(start_date[6])+1) + "-01T00:00:00"
    elif(int(start_date[5:7])==12 and int(start_date[8:10])==31):
        end_date = str(int(start_date[0:4])+1) + "-01-01T00:00:00"
    else:
        if(int(start_date[8:10])<9):
                end_date = start_date[0:9] + str(int(start_date[9])+1) + "T00:00:00"
        else:
                end_date = start_date[0:8] + str(int(start_date[8:10])+1) + "T00:00:00"
                
    readings = db.reference('UsersData/mRxIA4XvqYTmhIEjqfk8ycC02vq1/readings')
    part_readings = readings.order_by_child('timestamp').start_at(start_date).end_at(end_date).get()
    
    timestamp=[]
    temp_batt=[]
    temp_ext=[]
    temp_int=[]
    temp_pcb=[]
    
    
    for key,value in part_readings.items():
        if (float(value['temp_PCB']) > 100):
            temp_batt.append(value['temp_Batt1'])
            temp_ext.append(value['temp_ext'])
            temp_int.append(value['temp_int'])
            temp_pcb.append(value['temp_PCB'])
            timestamp.append(key)
        else:
            temp_batt.append(value['temp_Batt1'])
            temp_ext.append(value['temp_ext'])
            temp_int.append(value['temp_int'])
            temp_pcb.append(value['temp_PCB'])            
            timestamp.append(key)
        
    total_temp_batt=[0]*24
    total_temp_ext=[0]*24
    total_temp_int=[0]*24
    total_temp_pcb=[0]*24
    no_of_data_points=[0]*24

    for index in range (0,24):
        if (index<10):
            current_hour = start_date + "T0" + str(index) 
        else:
            current_hour = start_date + "T" + str(index)
        
        temp_batt_running_total = 0
        temp_ext_running_total = 0
        temp_int_running_total = 0
        temp_pcb_running_total = 0
        data_points_count = 0
    
        for index2 in range(0, len(timestamp)):
            if (current_hour == timestamp[index2][0:13]):
                temp_batt_running_total += float(temp_batt[index2])
                temp_ext_running_total += float(temp_ext[index2])
                temp_int_running_total += float(temp_int[index2])
                temp_pcb_running_total += float(temp_pcb[index2])
                data_points_count+=1
        
        total_temp_batt[index] += temp_batt_running_total
        total_temp_ext[index] += temp_ext_running_total
        total_temp_int[index] += temp_int_running_total
        total_temp_pcb[index] += temp_pcb_running_total
        no_of_data_points[index] += data_points_count


    hourly_temp_batt=[]
    hourly_temp_ext=[]
    hourly_temp_int=[]
    hourly_temp_pcb=[]
  
    for index in range(0,len(total_temp_batt)):
         if (no_of_data_points[index]==0):
            hourly_temp_batt.append(0)
            hourly_temp_ext.append(0)
            hourly_temp_int.append(0)
            hourly_temp_pcb.append(0)
         else:
            hourly_temp_batt.append(total_temp_batt[index]/no_of_data_points[index])
            hourly_temp_ext.append(total_temp_ext[index]/no_of_data_points[index])
            hourly_temp_int.append(total_temp_int[index]/no_of_data_points[index])
            hourly_temp_pcb.append(total_temp_pcb[index]/no_of_data_points[index])
    
    hours = []
    
    for index in range(0,24):
        if (index<10):
            hours.append("0" + str(index) + ":00:00")
        else:
            hours.append(str(index) + ":00:00")


    title =  "Average Battery Temperature for " + start_date
    FillSpreadSheet1(title, 'Hour' ,'Batt Temp (°C)', 'Ext Temp (°C)','Int Temp (°C)', 'PCB Temp (°C)',  hours , hourly_temp_batt, hourly_temp_ext, hourly_temp_ext, hourly_temp_pcb, "Batt_Temp_Day") 

            
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=hours, y=hourly_temp_batt,
                        mode='lines+markers', name = 'Battery'
                        ))
    
    fig.add_trace(go.Scatter(x=hours, y=hourly_temp_ext,
                        mode='lines+markers', name = 'External'
                        ))
    
    fig.add_trace(go.Scatter(x=hours, y=hourly_temp_int,
                        mode='lines+markers', name = 'Internal'
                        ))
    
    fig.add_trace(go.Scatter(x=hours, y=hourly_temp_pcb,
                        mode='lines+markers', name = 'PCB'
                        ))
    
    fig.update_layout(title = "Average Battery Temperature for " + start_date,
                   xaxis_title='Hours of The Day',
                   yaxis_title='Temperature (°C)')
    return fig

@app.callback(
    Output(component_id='technical_efficiency', component_property='figure'),
    [Input(component_id='slct_year', component_property='value')])

def TechnicalEfficiency(date_value):
    date=date_value 
    
    
    TOKEN = refreshtoken(r1)

    TotalConsumption = [0,0,0,0,0,0,0,0,0,0,0,0]


    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(date_value)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if int(date_value) == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalConsumption[6+i] = ((value['totalConsumption']/1000))
        elif data is None:
            TotalConsumption[i] = 0
        else: 
            TotalConsumption[i] = ((value['totalConsumption']/1000))
        i = i+1 


    TotalGeneration = [0,0,0,0,0,0,0,0,0,0,0,0]


    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(date_value)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if int(date_value) == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalGeneration[6+i] = ((value['totalGeneration']/1000))
        elif data is None:
            TotalGeneration[i] = 0
        else: 
            TotalGeneration[i] = ((value['totalGeneration']/1000))
        i = i+1
        
    monthly_tech_efficiency = []
    
    for index in range(0,len(TotalConsumption)):
        if (TotalGeneration[index] == 0 or TotalConsumption[index]==0):
            monthly_tech_efficiency.append(0)
        else:
            monthly_tech_efficiency.append((TotalConsumption[index]/TotalGeneration[index])*100)
    
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    
    title =  "Energy Production Efficiency for  " + str(date_value)
    FillSpreadSheet(title, 'Month' ,'Efficiency (%)', time , monthly_tech_efficiency, "Generation_Efficiency")    
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=monthly_tech_efficiency,
                        mode='lines+markers'
                        )) 
    
    fig.update_layout(title = "Energy Production Efficiency for  " + str(date_value),
                   xaxis_title='Month',
                   yaxis_title='Efficiency (%)')
    return fig   

        
@app.callback(
    Output(component_id='distribution_efficiency', component_property='figure'),
    [Input(component_id='slct_year2', component_property='value')])

def DistributionEfficiency(date_value):
    date=date_value 
    
    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00"
      
    daily_usage=[]

    timestamp = []
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]  
    monthly_usage=[] 
    
    url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)

    for index in range(0,len(df['timestamp'])):
        timestamp.append(str(df['timestamp'][index]))
        daily_usage.append(df['usage'][index])
    
    for i in range(1,13):
        
        amount = 0
        
        for index in range(0,len(timestamp)):
            temptime = timestamp[index]
            if(i==int(temptime[5:7])):
                amount += (float(daily_usage[index]))
            else:
                continue    

        if(amount==0):
            monthly_usage.append(0) 
        else:    
            monthly_usage.append(amount)
            amount = 0 
            
            
    TOKEN = refreshtoken(r1)

    TotalConsumption = [0,0,0,0,0,0,0,0,0,0,0,0]


    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(date_value)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if int(date_value) == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalConsumption[6+i] = ((value['totalConsumption']/1000))
        elif data is None:
            TotalConsumption[i] = 0
        else: 
            TotalConsumption[i] = ((value['totalConsumption']/1000))
        i = i+1            
    
    
    monthly_dist_efficiency = []
    for index in range(0,len(monthly_usage)):
        if (monthly_usage[index] == 0 or TotalConsumption[index]==0):
            monthly_dist_efficiency.append(0)
        else:
            monthly_dist_efficiency.append((monthly_usage[index]/TotalConsumption[index])*100)


    title =  "Distribution Efficiency for  " + str(date_value)
    FillSpreadSheet(title, 'Month' ,'Efficiency (%)', time , monthly_dist_efficiency, "Distribution_Efficiency") 
        
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=monthly_dist_efficiency,
                        mode='lines+markers'
                        )) 
    
    fig.update_layout(title = "Distribution Efficiency for  " + str(date_value),
                   xaxis_title='Month',
                   yaxis_title='Efficiency (%)')
    return fig  

@app.callback(
    Output(component_id='overall_efficiency', component_property='figure'),
    [Input(component_id='slct_year3', component_property='value')])

def OverallEfficiency(date_value):
    date=date_value 
    
    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00"
      
    daily_usage=[]

    timestamp = []
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]  
    monthly_usage=[] 
    
    url = "https://api.steama.co/sites/26385/utilities/1/usage/?start_time=" + start_time + "&end_time=" + end_time
    r = requests.get(url=url, headers = header)
    s = r.content
    df = pd.read_json(s)

    for index in range(0,len(df['timestamp'])):
        timestamp.append(str(df['timestamp'][index]))
        daily_usage.append(df['usage'][index])
    
    for i in range(1,13):
        
        amount = 0
        
        for index in range(0,len(timestamp)):
            temptime = timestamp[index]
            if(i==int(temptime[5:7])):
                amount += (float(daily_usage[index]))
            else:
                continue    

        if(amount==0):
            monthly_usage.append(0) 
        else:    
            monthly_usage.append(amount)
            amount = 0       

    TotalGeneration = [0,0,0,0,0,0,0,0,0,0,0,0]


    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(date_value)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if int(date_value) == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalGeneration[6+i] = ((value['totalGeneration']/1000))
        elif data is None:
            TotalGeneration[i] = 0
        else: 
            TotalGeneration[i] = ((value['totalGeneration']/1000))
        i = i+1
        
    monthly_overall_efficiency = []
    
    for index in range(0,len(TotalGeneration)):
        if (TotalGeneration[index] == 0 or monthly_usage[index]==0):
            monthly_overall_efficiency.append(0)
        else:
            monthly_overall_efficiency.append((monthly_usage[index]/TotalGeneration[index])*100)
    
    title =  "Overall System Efficiency for  " + str(date_value)
    FillSpreadSheet(title, 'Month' ,'Efficiency (%)', time , monthly_overall_efficiency, "Overall_Efficiency") 

        
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=monthly_overall_efficiency,
                        mode='lines+markers'
                        )) 
    
    fig.update_layout(title = "Overall System Efficiency for  " + str(date_value),
                   xaxis_title='Month',
                   yaxis_title='Efficiency (%)')
    return fig  

@app.callback(
    Output(component_id='carbon_savings', component_property='figure'),
    [Input(component_id='slct_year', component_property='value')])

def CarbonSavings(date_value):
    date=date_value 
    
    start_time = str(date) + "-01-01T00:00:00"
    end_time = str(int(date)+1) + "-01-01T00:00:00"
      
    daily_usage=[]

    timestamp = []
    time = ["January","February","March","April","May","June","July","August","September","October","November","December"]  

     

    TotalGeneration = [0,0,0,0,0,0,0,0,0,0,0,0]


    r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(date_value)

    headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
    r = session.get(r,headers=headers2)
    data = r.json()
    i = 0
    for value in data['set']:
        if int(date_value) == 2020: # Solar microgrid only started operation from July, before then no data so exception needs to be considered for 2020
            TotalGeneration[6+i] = ((value['totalGeneration']/1000000)) #in MWh
        elif data is None:
            TotalGeneration[i] = 0
        else: 
            TotalGeneration[i] = ((value['totalGeneration']/1000000))
        i = i+1
        
        
    Emission_Reductions=[]
    EF = 2.4 #emission factor
    
    for index in range(0,len(TotalGeneration)):
        Emission_Reductions.append(TotalGeneration[index] * EF)
    
    title =  "Emission Reductions for  " + str(date_value)
    FillSpreadSheet(title, 'Month' ,'Emission Reductions (t CO2e/m)', time , Emission_Reductions, "Carbon_Savings") 

    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=Emission_Reductions,
                        mode='lines+markers'
                        )) 
    
    fig.update_layout(title = "Emission Reductions for  " + str(date_value),
                   xaxis_title='Month',
                   yaxis_title='Emission Reductions (t CO2e/m)')
    
    return fig  
     
@app.callback(
    Output("download-maintenance-file", "data"),
    Input("maintenance-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile(n_clicks):
    print(APP_ROOT, r'SOP-011_Site_Visit_Maintenance_Report.docx')
    return file.send_file(os.path.join(APP_ROOT, r'SOP-011_Site_Visit_Maintenance_Report.docx'))

@app.callback(
    Output("download-revenue-file", "data"),
    Input("revenue-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Revenue.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Revenue.xlsx'))

@app.callback(
    Output("download-month-demand-file", "data"),
    Input("month-demand-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Monthly_Demand.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Monthly_Demand.xlsx'))

@app.callback(
    Output("download-day-profile-file", "data"),
    Input("day-profile-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Load_Profile_Day.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Load_Profile_Day.xlsx'))

@app.callback(
    Output("download-range-profile-file", "data"),
    Input("range-profile-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Load_Profile_Range.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Load_Profile_Range.xlsx'))

@app.callback(
    Output("download-month-peak-file", "data"),
    Input("month-peak-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Peaks_Month.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Peaks_Month.xlsx'))

@app.callback(
    Output("download-year-peak-file", "data"),
    Input("year-peak-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Peaks_Year.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Peaks_Year.xlsx'))

@app.callback(
    Output("download-day-cust-file", "data"),
    Input("day-cust-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Ind_Customer_Day.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Ind_Customer_Day.xlsx'))

@app.callback(
    Output("download-month-cust-file", "data"),
    Input("month-cust-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Ind_Customer_Month.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Ind_Customer_Month.xlsx'))

@app.callback(
    Output("download-consumption-range-file", "data"),
    Input("consumption-range-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Consumption_Range.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Consumption_Range.xlsx'))

@app.callback(
    Output("download-consumption-year-file", "data"),
    Input("consumption-year-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Consumption_Year.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Consumption_Year.xlsx'))

@app.callback(
    Output("download-generation-day-file", "data"),
    Input("generation-day-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Generation_Day.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Generation_Day.xlsx'))

@app.callback(
    Output("download-generation-year-file", "data"),
    Input("generation-year-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Generation_Year.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Generation_Year.xlsx'))

@app.callback(
    Output("download-soc-range-file", "data"),
    Input("soc-range-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'SOC_Range.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'SOC_Range.xlsx'))

@app.callback(
    Output("download-soc-day-file", "data"),
    Input("soc-day-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'SOC_Day.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'SOC_Day.xlsx'))

@app.callback(
    Output("download-soc-year-file", "data"),
    Input("soc-year-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'SOC_Year.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'SOC_Year.xlsx'))

@app.callback(
    Output("download-daily-uptime-file", "data"),
    Input("daily-uptime-file", "n_clicks"),   
    prevent_initial_call=True,
    
)

def downloadfile1(n_clicks):
    print(APP_ROOT, r'Daily_Uptime.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Daily_Uptime.xlsx'))

@app.callback(
    Output("download-no-days-outages-file", "data"),
    Input("no-days-outages-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'No_Days_Outages.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'No_Days_Outages.xlsx'))

@app.callback(
    Output("download-start-length-outages-file", "data"),
    Input("start-length-outages-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Start_Length_Outages.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Start_Length_Outages.xlsx'))

@app.callback(
    Output("download-hourly-uptime-file", "data"),
    Input("hourly-uptime-file", "n_clicks"),   
    prevent_initial_call=True,
    
)

def downloadfile1(n_clicks):
    print(APP_ROOT, r'Hourly_Uptime.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Hourly_Uptime.xlsx'))



@app.callback(
    Output("download-generation-efficiency-file", "data"),
    Input("generation-efficiency-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Generation_Efficiency.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Generation_Efficiency.xlsx'))

@app.callback(
    Output("download-distribution-efficiency-file", "data"),
    Input("distribution-efficiency-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Distribution_Efficiency.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Distribution_Efficiency.xlsx'))

@app.callback(
    Output("download-overall-efficiency-file", "data"),
    Input("overall-efficiency-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Overall_Efficiency.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Overall_Efficiency.xlsx'))

@app.callback(
    Output("download-batt-temp-month-file", "data"),
    Input("batt-temp-month-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Batt_Temp_Month.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Batt_Temp_Month.xlsx'))

@app.callback(
    Output("download-batt-temp-day-file", "data"),
    Input("batt-temp-day-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Batt_Temp_Day.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Batt_Temp_Day.xlsx'))

@app.callback(
    Output("download-8760-file", "data"),
    Input("8760-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'8760.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'8760.xlsx'))


@app.callback(
    Output("download-carbon-savings-file", "data"),
    Input("carbon-savings-file", "n_clicks"),   
    prevent_initial_call=True,
    
)
def downloadfile1(n_clicks):
    print(APP_ROOT, r'Carbon_Savings.xlsx')
    return file.send_file(os.path.join(APP_ROOT, r'Carbon_Savings.xlsx'))



if __name__ == '__main__':
    app.run_server(debug=True)




