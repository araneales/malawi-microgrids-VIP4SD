"""
Created on Sun Nov 1 21:30:13 2021

@author: Aaron Shek
"""

# Ensure to run the following in your CMD terminal in Windows as admin:
"""
python3 -m pip install dash
python3 -m pip install dash-renderer
python3 -m pip install dash_html_components 
python3 -m pip install dash_core_components
python3 -m pip install plotly.express
python3 -m pip install numpy 
python3 -m pip install pandas
python3 -m pip install pandas-datareader
python3 -m pip install datetime
python3 -m pip install openpyxl

etc...
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc 
import pandas as pd
import pandas_datareader.data as web
import datetime
# Bootstrap - a technique of loading a program into a computer by means of a few initial instructions which enable the introduction of the rest of the program from an input device.
# Link 7 - https://youtu.be/0mfIK8zxUds  - Whole program is run by @app.callback() - 
if __name__ == '__main__': # Check if code is being run as a script or being imported - serves as a boilerplate 
    """
    start = datetime.datetime(2020, 1, 1) # Start measuring date time from 1/1/20 to 1/11/21
    end = datetime.datetime(2021,11,1)
    df = web.DataReader(['AMZN','GOOGL','FB','PFE','BNTX','MRNA'],'stooq',start=start,end=end) # PD datareader to get stock prices
    df = df.stack().reset_index()
    print(df[:15])

    df.to_csv("C:/Users/aaron/Desktop/Sample/mystocks.csv",index=False) # Don't overload API with requests, just pull from CSV- check max amount of pulls
    """ 
    df = pd.read_csv("C:/Users/aaron/Desktop/Sample/mystocks.csv") 
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],  # Themes for Dash Bootstrap themes CSS DARKLY https://www.bootstrapcdn.com/bootswatch/
                    meta_tags=[{'name':'viewport',
                                'content':'width=device-width, initial-scale=1.0'}] # Consider mobile devices
                    ) 
    # -------------- Layout Section: Bootstrap -------------- #
    app.layout = dbc.Container([ # Everything contained within
        # Create three different rows list

        # TITLE 
        dbc.Row([
            dbc.Col(html.H1("Stock Market Dashboard",
                            # mb-4 gives a little bit of padding - space underneath H1 title, no need for comma seperation for different properties
                            className='text-center text-primary, mb-4'), # Define any type of bootstrap styling that we want to give to it, hackerthemes.com/bootstrap-cheatsheet/
                    width=12) # 12 columns - Max
        ]),

        # DROP DOWN
        dbc.Row([
            dbc.Col([ # FIRST CHART
                dcc.Dropdown(id='my-dpdn', multi=False, value ='AMZN', # Start default with AMAZON
                            options =[{'label':x, 'value':x}
                                        for x in sorted(df['Symbols'].unique())]), # Create six different options with 6 different symbols i.e AMAZN, GOOGLE,...,MRNA for dropdown
            dcc.Graph(id='line-fig', figure={})
            ],# width={'size':5,'offset':0,'order':1}, # 5 columns - Think of website split into max. 12 verticle columns offset + 1 column
            xs=12 , sm=12, md=12, lg=5, xl=5 # x-small, small, med = 12 columns, large, xl = 5 columns
            ), 
            # SECOND CHART
            dbc.Col([ # Mutliple choices for stocks multi=True
                dcc.Dropdown(id='my-dpdn2', multi=True, value = ['BNTX', 'MRNA'], # Default values
                            options = [{'label':x, 'value':x}
                                        for x in sorted(df['Symbols'].unique())],
                            ),
            dcc.Graph(id='line-fig2', figure={})
                
            ],#,width={'size':5,'offset':0,'order':2}), # Order - decide which column components comes first, priorities 1 over 2, offset create space left to the column component
            xs=12 , sm=12, md=12, lg=5, xl=5 ), # x-small, small, med = 12 columns, large, xl = 5 columns wide
        ],justify='center'), # center, end, between, around - column justification

        # CHECKLIST BOXES (RADIO BUTTONS) + IMAGE
        dbc.Row([
            dbc.Col([ # THIRD CHART
                html.P("Select Company Stock: ", # Create style sheet with dict.
                        style={"textDecoration": "underline"}), # Values always go inside a list
                dcc.Checklist(id='my-checklist', value=['FB','BNTX','AMZN'], # Default values
                                options = [{'label':x, 'value':x}
                                    for x in sorted(df['Symbols'].unique())],
                                labelClassName="me-3"), # Me-3 instead of mr-3
                dcc.Graph(id='my-hist', figure={}),
            ], #width={'size':5,'offset':1}),
            xs=12 , sm=12, md=12, lg=5, xl=5 # x-small, small, med = 12 columns, large, xl = 5 columns
            ), 

            # IMAGE
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardBody(
                            html.P(
                                "Strathclyde University - Solar Microgrids For Sustainable Development Goals Vertically Integrated Project", # Title
                                className="card-text") # Card title and make up the bulk of the card's content.                   
                        ),
                        dbc.CardImg(
                            src="https://www.strath.ac.uk/media/1newwebsite/icons/globalgoals/goal-7.jpg", # Image
                            bottom=True),                       
                    ],
                    style={"width":"24rem"}, # 1 rem = 16 pixels
                )
            ],#width={'size':5,'offset':0}), # width={'size':5,'offset':1},
            xs=12 , sm=12, md=12, lg=5, xl=5 # x-small, small, med = 12 columns, large, xl = 5 columns
            ),               
        ],justify='center'), # Start, center, end
    ], fluid=True) 

    """
    # Callback section: connecting the components (Code copied from link 6 - https://youtu.be/hSPmj7mK6ng) Watch soon
    # ************************************************************************
    # Line chart - Single
    """
    @app.callback(
        Output('line-fig', 'figure'),
        Input('my-dpdn', 'value')
    )
    def update_graph(stock_slctd):
        dff = df[df['Symbols']==stock_slctd]
        figln = px.line(dff, x='Date', y='High')
        return figln


    # Line chart - multiple
    @app.callback(
        Output('line-fig2', 'figure'),
        Input('my-dpdn2', 'value')
    )
    def update_graph(stock_slctd):
        dff = df[df['Symbols'].isin(stock_slctd)]
        figln2 = px.line(dff, x='Date', y='Open', color='Symbols')
        return figln2


    # Histogram
    @app.callback(
        Output('my-hist', 'figure'),
        Input('my-checklist', 'value')
    )
    def update_graph(stock_slctd):
        dff = df[df['Symbols'].isin(stock_slctd)]
        dff = dff[dff['Date']=='2021-11-01']
        fighist = px.histogram(dff, x='Symbols', y='Close')
        return fighist


    app.run_server(debug=True,port=3000)
    # CTRL+C to terminate 
# Complete guide to Plotly Dash bootstrap dashboard - link 7