import requests
from requests.structures import CaseInsensitiveDict

# Above exclusively for requests, bottom is normal program
import os # Google cloud storage for excel
import datetime as dt
import dash
import dash_core_components as dcc # from dash import dcc 
import dash_html_components as html # from dash import html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.express as px
from datetime import date
import datetime
import time
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SPACELAB]) # Themes for Dash Bootstrap themes CSS DARKLY https://www.bootstrapcdn.com/bootswatch/

def success(status):
       if status == 200 or status == 201:
              return True
       else:
              return False

# GET API DATA USING FUNCTION EXAMPLE


today = datetime.datetime.now()
past_date = str(today - datetime.timedelta(days=30))
start_time = past_date[0:10] + "T00:00:00"

C_date = str(today)

C_year = int(C_date[0:4])
C_month = int(C_date[5:7])
C_day = int(C_date[8:10])

session = requests.session() # Reusable persistent connection

# STEP 1
STEPONEURL = "https://auth.smaapis.de/oauth2/token"
step1payload = "POST%20sandbox.smaapis.de%2Foauth2%2Ftoken=&HTTP%2F1.1=&Host%3A%20smaapis.de=&Content-Type%3A%20application%2Fx-www-form-urlencoded=&client_id=strathclyde_api&client_secret=1f773505-616b-49a0-a462-5889fa690384&grant_type=client_credentials&="
headers1 = CaseInsensitiveDict()
headers1["Content-Type"] = "application/x-www-form-urlencoded"
r1 = requests.post(STEPONEURL, data=step1payload,headers=headers1)
TOKEN = r1.json()['access_token']
REFRESHTOKEN = r1.json()['refresh_token']

# STEP 2
STEPTWOURL = "https://async-auth.smaapis.de/oauth2/v2/bc-authorize"
headers2 = {'Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
step2payload = {'loginHint':'aaron.shek.2020@uni.strath.ac.uk'}
r2 = requests.post(STEPTWOURL, json=step2payload,headers=headers2)

def function(r1):
       STEPONEURL = "https://auth.smaapis.de/oauth2/token"
       step1payload = "POST%20auth.smaapis.de%2Foauth2%2Ftoken=&HTTP%2F1.1=&Host%3A%20smaapis.de=&Content-Type%3A%20application%2Fx-www-form-urlencoded=&client_id=strathclyde_api&client_secret=1f773505-616b-49a0-a462-5889fa690384&grant_type=refresh_token&refresh_token={0}".format(r1.json()['refresh_token'])
       headers1 = CaseInsensitiveDict()
       headers1["Content-Type"] = "application/x-www-form-urlencoded"
       r1 = requests.post(STEPONEURL, data=step1payload,headers=headers1)
       TOKEN = r1.json()['access_token']
       STEPTWOURL = "https://async-auth.smaapis.de/oauth2/v2/bc-authorize"
       headers2 = {'Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
       step2payload = {'loginHint':'aaron.shek.2020@uni.strath.ac.uk'}
       r2 = requests.post(STEPTWOURL, json=step2payload,headers=headers2)
       return TOKEN


# STEP 3 - GET DATA VIA API FOR EXAMPLE
r = "https://async-auth.smaapis.de/monitoring/v1/plants"
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}
r = session.get(r,headers=headers2)
data_initial = r.json()
print(data_initial)

# STEP 3 - GET DATA VIA API FOR EXAMPLE
r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Total?WithTotal=true"
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}

r = session.get(r,headers=headers2)
print("\nStatus Code: {0}. Successful: {1}\n".format(r.status_code,success(r.status_code)))
data_initial = r.json()
print(data_initial)


# STEP 3 - GET DATA VIA API FOR EXAMPLE
if C_month < 10:
       r3 = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Month?Date={0}-0{1}&WithTotal=false".format(C_year,C_month)
else:
       r3 = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Month?Date={0}-{1}&WithTotal=false".format(C_year,C_month)
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}

r3 = session.get(r3,headers=headers2)
print("\nStatus Code: {0}. Successful: {1}\n".format(r.status_code,success(r.status_code)))
data_initial = r3.json()
#print(data_initial)
TotalConsumptionDisplay = 0
for value in data_initial['set']:
              print(value['totalGeneration'])
              TotalConsumptionDisplay = TotalConsumptionDisplay + (value['totalGeneration'])
              

print(TotalConsumptionDisplay)


TotalConsumption = []
""" for i in range(1,12):
       if i < 10: # If date less than 10 to suit YYYY-MM-DD Format
              r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Month?Date={0}-{1}&WithTotal=false".format(2021,i)
       else:
             r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Month?Date={0}-{1}&WithTotal=false".format(2021,i) """

r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Year?Date={0}&WithTotal=false".format(2021)

headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}
r = session.get(r,headers=headers2)
data = r.json()
for value in data['set']:
       TotalConsumption.append(value['totalConsumption'])

print(TotalConsumption)


 # STEP 3 - GET ALL POSSIBLE DATA
r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date=2022-02-20&WithTotal=false"
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}

r = session.get(r,headers=headers2)
print("\nStatus Code: {0}. Successful: {1}\n".format(r.status_code,success(r.status_code)))
data_initial = r.json()
#print(data_initial)


""" r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/logs?From=2020-06-05&To=2022-02-19&Level=Info"
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}

r = session.get(r,headers=headers2)
print("\nStatus Code: {0}. Successful: {1}\n".format(r.status_code,success(r.status_code)))
data_initial = r.json()
print(data_initial) """
"""
# GET DATA VIA LOOP
stateOfCharge = []
batteryDischarging = []
Totalconsumption = []
start = time.time()
for i in range(1,C_day):
       if i < 10: # If date less than 10 to suit YYYY-MM-DD Format
              r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date=2022-01-0{0}&WithTotal=true".format(i)
       else:
              r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date=2022-01-{0}&WithTotal=true".format(i)

       headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
       r = session.get(r,headers=headers2)
       data = r.json()
       stateOfCharge.append(data['set'][i]['batteryStateOfCharge'])
       batteryDischarging.append(data['set'][i]['batteryDischarging'])
       Totalconsumption.append(data['set'][i]['totalConsumption'])
       # print(data['set'][i]['batteryStateOfCharge'])
end = time.time()

print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. ") """

app.layout = html.Div([ # SHOW GRAPH IN HTML
       html.H6("Please Select a Date:"),
       dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                start_date=date(C_year, C_month, C_day),
                end_date=date(C_year, C_month, C_day) # Changed so it selects current day, previously it was set to June the 5th 2020
                # more user friendly
            ),
       dcc.Graph(id = 'graph_1', figure = {}),
       dcc.DatePickerRange(
                id='my-date-picker-range-2',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                start_date=date(C_year, C_month, C_day),
                end_date=date(C_year, C_month, C_day) # Changed so it selects current day, previously it was set to June the 5th 2020
                # more user friendly
            ),
       dcc.Graph(id = 'graph_2', figure = {}),

       dcc.DatePickerSingle(
                id='my-date-picker-single-test',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day)
            ),
       dcc.Graph(id = 'graph_3', figure = {}),
       dcc.DatePickerSingle(
                id='my-date-picker-single-test-2',
                min_date_allowed=date(2020, 6, 5),
                max_date_allowed=date(C_year, C_month, C_day),
                initial_visible_month=date(C_year, C_month, C_day),
                date=date(C_year, C_month, C_day)
            ),
       dcc.Graph(id = 'graph_4', figure = {}),

])
""" 
# ALL DATA YOU CAN RETRIEVE
r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Recent?WithTotal=true"
headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(TOKEN)}
r = session.get(r,headers=headers2)
print("\nStatus Code: {0}. Successful: {1}\n".format(r.status_code,success(r.status_code)))
data_test = r.json()
print(data_test)
"""

@app.callback(
       Output(component_id='graph_1', component_property='figure'),
       Input(component_id='my-date-picker-range', component_property='start_date'),
       Input(component_id='my-date-picker-range', component_property='end_date'))

def stateofCharge(start_date,end_date): 
       function(r1)
# GET DATA VIA LOOP
       stateOfCharge = []
       
       start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """

       for i in range(int(start_date[8:10]),int(end_date[8:10])):
              if i < 10: # If date less than 10 to suit YYYY-MM-DD Format
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-0{2}&WithTotal=true".format(start_date[0:4],start_date[5:7],i)
              else:
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=true".format(start_date[0:4],start_date[5:7],i)

              headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}
              r = session.get(r,headers=headers2)
              data = r.json()
              stateOfCharge.append(data['set'][i]['batteryStateOfCharge'])
              """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
              Totalconsumption.append(data['set'][i]['totalConsumption']) """
              # print(data['set'][i]['batteryStateOfCharge'])
       end = time.time()

       #print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (BATTERY STATE OF CHARGE)")
       print(stateOfCharge)
       date = []
       for i in range(int(start_date[8:10]),int(end_date[8:10])):
           if i < 10:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))
           else:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))   
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = date,
                    y = stateOfCharge,
                    mode = 'lines+markers', 
                    name = 'State of Charge'
                ))

       fig.update_layout(
                    title ='Battery State of Charge (Plant {0}):'.format(5),
                    xaxis_title='{0} days selected'.format((int(end_date[8:10])-int(start_date[8:10]))),
                    yaxis_title='State of Charge (%)',
                    autotypenumbers='convert types',
                    )
       
       return fig 


@app.callback(
       Output(component_id='graph_2', component_property='figure'),
       Input(component_id='my-date-picker-range-2', component_property='start_date'),
       Input(component_id='my-date-picker-range-2', component_property='end_date'))

def stateofCharge(start_date,end_date): 
       function(r1)
# GET DATA VIA LOOP

       batteryDischarging = []
       Totalconsumption = []

       start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """

       for i in range(int(start_date[8:10]),int(end_date[8:10])):
              if i < 10: # If date less than 10 to suit YYYY-MM-DD Format
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-0{2}&WithTotal=true".format(start_date[0:4],start_date[5:7],i)
              else:
                     r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=true".format(start_date[0:4],start_date[5:7],i)

              headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}
              r = session.get(r,headers=headers2)
              data = r.json()
              #batteryDischarging.append(data['set'][i]['batteryDischarging'])
              Totalconsumption.append(data['set'][i]['totalConsumption'])
              # print(data['set'][i]['batteryStateOfCharge'])
       end = time.time()

       #print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (TOTAL CONSUMPTION)")
       print(Totalconsumption)
       date = []
       for i in range(int(start_date[8:10]),int(end_date[8:10])):
           if i < 10:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))
           else:
              date.append("{0}-{1}-{2}".format(start_date[0:4],start_date[5:7],i))   
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = date,
                    y = Totalconsumption,
                    mode = 'lines+markers',
                                    
                ))
       fig.update_layout(
                    title ='Total Consumption (Plant {0}):'.format(5),
                    xaxis_title='{0} days selected'.format((int(end_date[8:10])-int(start_date[8:10]))),
                    yaxis_title='Total Consumption (Wh)',
                    autotypenumbers='convert types',
                    )
    
       return fig 



@app.callback(
       Output(component_id='graph_3', component_property='figure'),
       Input(component_id='my-date-picker-single-test', component_property='date'))

def stateofCharge(date): 
       function(r1)
# GET DATA VIA LOOP
       stateOfCharge = []
       
       start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """


       r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=false".format(date[0:4],date[5:7],date[8:10]) 
             

       headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}
       r = session.get(r,headers=headers2)
       data = r.json()
       #print(data)
       i = 0
       for value in data['set']:
              stateOfCharge.append((value['batteryStateOfCharge']))
              #print(value['batteryStateOfCharge'])
              i = i+1


       """ batteryDischarging.append(data['set'][i]['batteryDischarging'])
       Totalconsumption.append(data['set'][i]['totalConsumption']) """
       # print(data['set'][i]['batteryStateOfCharge'])
       end = time.time()

       print("\nIt took ",end-start, " seconds to do ", i, " API GET requests. (BATTERY STATE OF CHARGE 2)")
       #print(stateOfCharge)
       timeframe = []
       for i in range(len(stateOfCharge)):
           if i < 10:
              timeframe.append(data['set'][i]['time'])
           else:
              timeframe.append(data['set'][i]['time'])   
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = timeframe,
                    y = stateOfCharge,
                    mode = 'lines+markers', 
                    name = 'State of Charge'
                ))

       fig.update_layout(
                    title ='Battery State of Charge (Plant {0}):'.format(5),
                    xaxis_title='Hours',
                    yaxis_title='State of Charge (%)',
                    autotypenumbers='convert types',
                    )
       
       return fig 


@app.callback(
       Output(component_id='graph_4', component_property='figure'),
       Input(component_id='my-date-picker-single-test-2', component_property='date'))

def TotalGenerationDay(date): 

# GET DATA VIA LOOP
       totalGen = []
       function(r1)
       #start = time.time()
       """ print("year: " + start_date[0:4]) # Access DD of YYYY-MM-DD
       print("month: " + start_date[5:7]) # Access DD of YYYY-MM-DD
       print("date: " + start_date[8:10]) # Access DD of YYYY-MM-DD """


       r = "https://async-auth.smaapis.de/monitoring/v1/plants/5340310/measurements/sets/EnergyBalance/Day?Date={0}-{1}-{2}&WithTotal=false".format(date[0:4],date[5:7],date[8:10]) 
             

       headers2 = {'Host':'smaapis.de','Content-Type': 'application/json','Authorization':'Bearer {0}'.format(function(r1))}
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
       fig = go.Figure()
       fig.add_trace(go.Scatter(
                    x = timeframe,
                    y = totalGen,
                    mode = 'lines+markers', 
                    name = 'State of Charge'
                ))

       fig.update_layout(
                    title ='Total Generation of Microgrid (Plant {0}):'.format(5),
                    xaxis_title='Hours',
                    yaxis_title='Generation (W)',
                    autotypenumbers='convert types',
                    )
       
       return fig 
# https://sandbox.smaapis.de/monitoring/index.html
if __name__ == '__main__': # Protects users from accidentally invoking the script when they didn't intend to. Based on Flask framework
    app.run_server(debug=True) # Ctrl+C in terminal to terminate

