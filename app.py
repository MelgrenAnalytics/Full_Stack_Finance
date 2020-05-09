import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import date

# read in the data
s = pd.read_csv('nasdaq_100.csv',parse_dates = True
                ,header = [0,1],index_col = 0)
cluster = pd.read_csv('clusters.csv',index_col = 0)
chg = (s['Open'] - s['Close'])/s['Open']
clust_means = chg.transpose().join(cluster)
clust_means = clust_means.groupby('cluster').mean().transpose()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

sidepanel = dbc.Card([
    dbc.FormGroup([
        dbc.Label("Select Ticker")
        ,dcc.Dropdown(id='stock-select'
                      ,options=[{'label':i, 'value':i} for i in cluster.index]
                      ,value='ATVI' )
    ])
])

mainbody = [
    dcc.Graph(id="stock-vs-cluster")
    ,dbc.FormGroup([
        dbc.Label("Timeframe")
        ,dcc.RadioItems(id = 'timeframe-select'
                ,options=[
                    {'label': 'Max', 'value': 'Max'},
                    {'label': 'YTD', 'value': 'YTD'},
                    {'label': '3Y', 'value': '3Y'},
                    {'label': '1Y', 'value': '1Y'},
                    {'label': '6Mo', 'value': '6Mo'},
                    {'label': '3Mo', 'value': '3Mo'},
                    {'label': '1Mo', 'value': '1Mo'}
                ],value='Max'
                ,inputStyle={"margin-left": "20px"}) 
    ],row = True)
]
app.layout = dbc.Container([
        html.H1("NASDAQ 100 Cluster Explorer"),
        dbc.Row([
            dbc.Col(sidepanel, md=3),
            dbc.Col(mainbody, md=9)
        ])
],fluid=True)


@app.callback(
    Output('stock-vs-cluster', 'figure'),
    [Input('stock-select', 'value')
     ,Input('timeframe-select', 'value')]
)
def update_figure(symbol,timeframe):
    clust_no = cluster.cluster[symbol]
    pldf = chg[symbol].to_frame().join(clust_means[clust_no])
    pldf = pldf.rename(columns = {clust_no:'Cluster Mean'}).reset_index()
    pldf = pldf.melt(id_vars = ['Date'])
    
    # handle timeframe
    if timeframe == 'YTD':
        pldf = pldf.loc[pldf.Date.dt.year == date.today().year,:]
    elif timeframe == '3Y':
        pldf = pldf.loc[pldf.Date > date.today()-pd.DateOffset(years = 3)]
    elif timeframe == '1Y':
        pldf = pldf.loc[pldf.Date > date.today()-pd.DateOffset(years = 1)]
    elif timeframe == '6Mo':
        pldf = pldf.loc[pldf.Date > date.today()-pd.DateOffset(months = 6)]
    elif timeframe == '3Mo':
        pldf = pldf.loc[pldf.Date > date.today()-pd.DateOffset(months = 3)]
    elif timeframe == '1Mo':
        pldf = pldf.loc[pldf.Date > date.today()-pd.DateOffset(months = 1)]
    else:
        pldf = pldf
    return px.line(pldf, x="Date", y="value", color='variable')

if __name__ == "__main__":
    app.run_server(debug=False, port = 8050)

