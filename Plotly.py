"""
Created on Sun Oct 31 21:24:20 2021

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
python3 -m pip install openpyxl
"""

import dash # Dash is python framework created by plotly for creating interactive web applications
from dash import dcc # Replaced with originally - import dash_core_components as dcc
from dash import html # Replaced with originally - import dash_html_components as html since package is deprecated
import dash_bootstrap_components as dbc 
import plotly.graph_objs as go 
import plotly  
import plotly.express as px 
import numpy as np # External libaries
import pandas as pd 

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY]) # Themes for Dash Bootstrap themes CSS DARKLY https://www.bootstrapcdn.com/bootswatch/
# Random scatter plots
np.random.seed(50)

x_rand = np.random.randint(1,61,60) # Random integers for scatter plot
y_rand = np.random.randint(1,61,60)

orders = pd.read_excel(r'C:/Users/aaron/Desktop/Plotly/SampleData.xlsx') # Open XLSX file for sample data 

df = px.data.iris()

colors = { # Dictionary of values assigned to variables to save time and efficiency
    # -------------- Define global parameters -------------- #
    'plotColor':'#222222', # BG colour of charts/graphs
    'globalFont':'verdana',
}

app.layout = html.Div([ # The <div> tag defines a division or a section in an HTML document.
    # -------------- Heading ONE -------------- #
    html.H1("Simple Plotly example ", # Heading H1 etc. Refer to HTML5.
        style = {
            'textAlign':'center',
            'color':'#FFFFFF',
            'font-family':colors['globalFont'],
            
        }
    ),

    html.Hr(), # Used to create lines and separate parts
    html.Br(),
    html.Div("A simple example of a development framework from Plotly.", # Use comma for next line
        # -------------- Style of Div -------------- #
        style = {
            'textAlign':'center',
            'font-family':colors['globalFont'],
        }
    ), 
    # -------------- Bar chart -------------- #
    dcc.Graph(
        id = 'samplechart',
        figure = {          
            'data': [
                {'x':[5,6,7],'y':[12,15,18],'type':'bar','name':'First Chart'}, # Simple bar chart
                {'x':[1,2,3],'y':[4,5,6],'type':'bar','name':'Second Chart'},
            ],
            # -------------- Specify layout/styling for BAR CHART LOCALLY -------------- #
            'layout': {
                'color':'#FFFFFF',
                'title':'Simple Bar Chart',
                'xaxis':{'title':'X-axis','color':'#FFFFFF'},
                'yaxis':{'title':'Y-axis','color':'#FFFFFF'},
                'plot_bgcolor':colors['plotColor'],
                'paper_bgcolor':colors['plotColor'],
            },                     
        },     
    ),
    html.Hr(), 
    html.Br(), 
    # -------------- Scatter chart -------------- #    
    dcc.Graph(
        id = 'scatter_chart',
        
        figure = {            
            'data' : [
                go.Scatter(
                    x = x_rand,
                    y = y_rand,
                    mode = 'markers' # Type of graph
                )
            ],
            # -------------- Specify layout/styling for SCATTER CHART LOCALLY -------------- #
            'layout': go.Layout(
                title = 'Scatterplot of Random 60 points', # Notice how it is now equal to not using ':' like previously
                xaxis = {'title':'Random X Values','color':'#FFFFFF'},
                yaxis = {'title':'Random Y Values','color':'#FFFFFF'},               
                plot_bgcolor = colors['plotColor'],
                paper_bgcolor = colors['plotColor']
                
            )          
        }  
    ),
    html.Hr(), 
    html.Br(), 
    # -------------- Bar chart with real life data as XLS Excel file example as import -------------- #
    dcc.Graph(
        id = 'samplechartxlsxfile',
        figure = {
            
            'data': [
                {'x':orders.Item,'y':orders.Units,'type':'bar','name':'First Chart'}, # Quite simply can use excel file data for x and y axis values
            ],
            # -------------- Specify layout/styling for BAR CHART GLOBALLY -------------- #
            'layout': {
                'title':'Office Items Sold',
                'xaxis':{'title':'Items','color':'#FFFFFF'},
                'yaxis':{'title':'Number of Units Sold','color':'#FFFFFF'},
                'plot_bgcolor':colors['plotColor'],
                'paper_bgcolor':colors['plotColor'],
            },                     
        },     
    ),
    html.Hr(), 
    html.Br(), 
       # -------------- Dropdown example -------------- #
    html.Label('Choose a city: '),
    html.Br(),
    dcc.Dropdown(
        id = 'first-dropdown',
        options = [
            {'label':'San Francisco','value':'SF'},
            {'label':'New York City','value':'NYC'},
            {'label':'Chicago City','value':'CC'}, #,'disabled':True Disable option
        ],
        placeholder = 'Select a city'
        # multi = True, # Multiple selection
        # disabled = True, # Disable dropdown
    ),
])
if __name__ == '__main__': # Protects users from accidentally invoking the script when they didn't intend to. Based on Flask framework
    app.run_server(debug=False) # Ctrl+C in terminal to terminate

# Up to tut. 11 of Plotly of link 5 
