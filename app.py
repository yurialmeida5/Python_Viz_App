import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px

# Load dataset
data = pd.read_csv("https://github.com/bencearato/data/blob/master/shark_attacks.csv?raw=True", encoding='ISO-8859-1')

# Data Cleanning - Remove Unnescessary columns and Rows
data = data.drop(["Case Number.1","Case Number.2","Time",
                  "href formula",'pdf','original order'], axis=1)
data.dropna(how='all', inplace=True)
data.dropna(inplace=True, subset=['Case Number'])
data = data[data['Case Number'] != 'xx']

# Correct Year column
try:
    data['Year_']=[d[0:4] for d in data['Case Number']]
except:
    data['Year_']='00'
try:
    data['Month']=[d[5:7] for d in data['Case Number']]
except:
    data['Month']='00'
try:
    data['Day']=[d[8:10] for d in data['Case Number']]
except:
    data['Day']='00'
data.loc[data['Year_'].str.contains('(?i)ND'),'Year_']='00'
data.loc[data['Year_'].str.contains('ND'),'Day']='00'
data.loc[data['Year_'].str.contains('ND'),'Month']='00'
data['Year_'] = data['Year_'].replace(['0.02','0.03','0.04','0.07'],0)
data['Year_'] = data['Year_'].astype(int)
data = data[['Case Number','Year_', 'Year','Type','Country','Fatal (Y/N)']]
data.rename(columns={'Case Number' : 'case_number', 'Day' : 'day', 'Country' : 'country' , 'Fatal (Y/N)' : 'fatal' , 'Type' : 'type' }, inplace=True)

# Set up manually some of the years
data.loc[52,'Year'] = 2017
data.loc[2533,'Year']= 1989
data.loc[3746,'Year']= 1961
data.loc[4283,'Year']= 1851
data.loc[4397,'Year']= 1948
data.loc[5069,'Year']= 1923
data.loc[5129,'Year']= 1900
data.loc[5885,'Year']= 1836
data.loc[5923,'Year']= 1806
data.loc[5936,'Year']= 1784

# Prepare Fatal Column

data['fatal'] = data['fatal'].str.strip()
data['fatal'] = data['fatal'].fillna('U')
data['fatal'] = data['fatal'].str.replace('n', 'N')
data['fatal'] = data['fatal'].str.replace('#VALUE!', 'U')
data['fatal'] = data['fatal'].str.replace('F', 'Y')
data['fatal'] = data['fatal'].str.replace('UNKNOWN', 'U')
# Rename a non-fatal attack
data.loc[646,'fatal']= 'N'
data['fatal'] = data['fatal'].replace({'U': 'UNKNOWN', 'Y' : 'YES' , 'N' : 'NO'})


# Prepare Country Column 
data['country'] =  data['country'].fillna('UNKNOWN')
# Country Column
data['country'] = data['country'].replace({'England':'UNITED KINGDOM', 'ENGLAND' : 'UNITED KINGDOM', 'Fiji' : 'FIJI', 'UNITED ARAB EMIRATES (UAE)' : 'UNITED ARAB EMIRATES' , 'NORTH ATLANTIC OCEAN ' : 'UNKNOWN' , 'MID-PACIFC OCEAN' : 'UNKNOWN' , 
 'CENTRAL PACIFIC' : 'UNKNOWN', 'INDIAN OCEAN?' : 'UNKNOWN' , 'Coast of AFRICA' : 'UNKNOWN' , 'Between PORTUGAL & INDIA' : 'UNKNOWN' , 'FEDERATED STATES OF MICRONESIA' : 'MICRONESIA' , 'RED SEA?' : 'UNKNOWN' ,  'RED SEA' : 'UNKNOWN' , 'ASIA?' : 'UNKNOWN',
 'CEYLON (SRI LANKA)' : 'SRI LANKA' , 'Seychelles' : 'SEYCHELLES' , 'MEDITERRANEAN SEA' : 'UNKNOWN' , 'DIEGO GARCIA' : 'UNKNOWN', 'MID ATLANTIC OCEAN' : 'UNKNOWN' , 'NORTH SEA' : 'UNKNOWN' , 'SOUTH ATLANTIC OCEAN' : 'UNKNOWN' , 'MID ATLANTIC OCEAN' : 'UNKNOWN' ,
  'SIERRA LEONE?' :  'SIERRA LEONE' , 'INDIAN OCEAN' : 'UNKNOWN' , 'OCEAN' : 'UNKNOWN' , 'NORTH SEA' : 'UNKNOWN' , 'THE BALKANS' : 'UNKNOWN' , 'PACIFIC OCEAN ' : 'UNKNOWN', 'NORTH ATLANTIC OCEAN' : 'UNKNOWN' , 'NORTH PACIFIC OCEAN' : 'UNKNOWN' , 'SOUTH PACIFIC OCEAN' : 'UNKNOWN',
  ' PHILIPPINES' : 'PHILIPPINES', 'SOUTHWEST PACIFIC OCEAN' : 'UNKNOWN',  'OKINAWA' : 'JAPAN' , 'SOUTH CHINA SEA' : 'CHINA' , 'EGYPT ' : 'EGYPT' , 'COLUMBIA' : 'USA' , 'WESTERN SAMOA' : 'SAMOA' , 'AMERICAN SAMOA' : 'SAMOA' , 'RED SEA / INDIAN OCEAN' : 'UNKNOWN', 'PERSIAN GULF' : 'UNKNOWN',
  'NORTHERN ARABIAN SEA' : 'UNKNOWN' , 'ST. MAARTIN' : 'ST. MARTIN' , 'NEW GUINEA' : 'PAPUA NEW GUINEA' ,  'GRAND CAYMAN'  : 'CAYMAN ISLANDS' , 'JAVA' :  'INDONESIA' , 'SUDAN?' : 'SUDAN' , 'YEMEN ' : 'YEMEN' })
data['country'] = data['country'].str.strip()

# Prepare Type Column
data['type'] = data['type'].str.strip()
data['type'] = data['type'].str.replace('Boating','Boat')
data['type'] = data['type'].str.replace('Invalid','Unknown')
data['type'].fillna('Unknown', inplace=True)

country_list = list(data.country.unique())
country_list.append('ALL')
country_list = np.sort(country_list)

fatal_list = list(data.fatal.unique())
fatal_list.append('ALL')
fatal_list = np.sort(fatal_list)

data = data[data.Year_ > 1800]

data = data.groupby(['Year_', 'fatal' ,'country', 'type']).count()['case_number'].reset_index()

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Shark Analytics: Shark Attack's World Wide!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🦈", className="header-emoji"),
                html.H1(
                    children="Shark Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze all the shark attacks worldwide starting from 1800 by Country, Region and Date",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="country", className="menu-title"),
                        dcc.Dropdown(
                            id="country-filter",
                            options=[
                                {"label": country, "value": country}
                                for country in country_list
                            ],
                            value="ALL",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="fatal", className="menu-title"),
                        dcc.Dropdown(
                            id="fatal-filter",
                            options=[
                                {"label": fatal_type, "value": fatal_type}
                                for fatal_type in fatal_list
                            ],
                            value="ALL",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="initial-date", className="menu-title"),
                        dcc.Dropdown(
                            id="initial-date-filter",
                            options=[
                                {"label": initial_date , "value": initial_date}
                                for initial_date in np.sort(data.Year_.unique())
                            ],
                            value=2000,
                            clearable=False,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="final-date", className="menu-title"),
                        dcc.Dropdown(
                            id="final-date-filter",
                            options=[
                                {"label": final_date , "value": final_date}
                                for final_date in np.sort(data.Year_.unique())
                            ],
                            value=2015,
                            clearable=False,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="attack-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                    html.Div(
                    children=dcc.Graph(
                        id="type-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


# Callback with a single input parameter, returning the same figure twice
@app.callback(
    Output('attack-chart', 'figure'),
    Output('type-chart', 'figure'),
    Input('country-filter', 'value'),
    Input('fatal-filter', 'value'),
    Input('initial-date-filter', 'value'),
    Input('final-date-filter', 'value')
)

def update1( _input1, _input2, _input3, _input4 ):

    df1 = data[(data['Year_'] >= _input3) & (data['Year_'] <= _input4)]

    if _input1 != 'ALL': 
        df1=df1.query('country==@_input1')
    
    if _input2 != 'ALL': 
        df1=df1.query('fatal==@_input2')
    
    
    fig1= px.line(df1.groupby(['Year_']).count()['case_number'].reset_index(), x="Year_", y='case_number')
    fig1.update_layout(title= "Number of Shark Attacks by Year - " +  _input1)

    fig2 = px.bar(df1.groupby(['type']).count()['case_number'].reset_index(), x ='type', y='case_number')
    fig2.update_layout(title= "Number of Shark Attacks by Type - " +  _input1)

    return fig1, fig2


if __name__ == "__main__":
    app.run_server(debug=False)