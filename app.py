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

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

sidepanel = dbc.Card([
    dbc.FormGroup([
        dbc.Label("Select Ticker")
        ,dcc.Dropdown(id='stock-select'
                      ,options=[{'label':i, 'value':i} for i in cluster.index]
                      ,value='ATVI' )
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
                    ,labelStyle={"margin-right": "5px"}) 
        ],row = False)
    ])
])

mainbody = [
    dcc.Graph(id="stock-vs-cluster")
    ,html.P(id = "cluster-members")
]
app.layout = dbc.Container([
        html.H1("NASDAQ 100 Cluster Explorer"),
        dbc.Row([
            dbc.Col(sidepanel, md=2),
            dbc.Col(mainbody, md=10)
        ])
],fluid=True)


@app.callback(
    [Output('stock-vs-cluster', 'figure'),
     Output('cluster-members','children')]
    ,[Input('stock-select', 'value')
     ,Input('timeframe-select', 'value')]
)
def update_figure(symbol,timeframe):
    
    # get the cluster for the given symbol and it's members
    clust_no = cluster.cluster[symbol]
    clust_members = cluster[cluster.cluster == clust_no].index
    
    # get the closing values for only the stocks in the given cluster
    p = s['Close'].loc[:,clust_members]
    
    # filter the index based on just the timeframe
    if timeframe == 'YTD':
        p = p.loc[p.index.year == date.today().year,:]
    elif timeframe == '3Y':
        p = p.loc[p.index > date.today()-pd.DateOffset(years = 3)]
    elif timeframe == '1Y':
        p = p.loc[p.index > date.today()-pd.DateOffset(years = 1)]
    elif timeframe == '6Mo':
        p = p.loc[p.index > date.today()-pd.DateOffset(months = 6)]
    elif timeframe == '3Mo':
        p = p.loc[p.index > date.today()-pd.DateOffset(months = 3)]
    elif timeframe == '1Mo':
        p = p.loc[p.index > date.today()-pd.DateOffset(months = 1)]
    else:
        p = p
    
    # get rid of any missing values
    p = p.dropna(axis = 0,subset = [symbol])
    # equalize all stocks with a sum of 100 on the first day
    c = p*((100/len(p.columns))/p.iloc[0,:])
    
    # sum the cluster stocks and join on the selected stock (100-index both)
    plot_df = pd.DataFrame(c.transpose().sum().transpose(),columns = ['cluster'])
    plot_df = plot_df.join(p[symbol]*(100/p[symbol][0])).reset_index()
    plot_df = plot_df.melt(id_vars = ['Date'])
    graph =  px.line(plot_df, x="Date", y="value", color='variable')

    # output the list of clusters in the stock
    out_text = 'Cluster Members: ' + ', '.join(clust_members)
    
    return graph, out_text

if __name__ == "__main__":
    app.run_server(debug=False, port = 8050)
