# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import requests
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from datetime import date
import calendar

app = dash.Dash(__name__)

#declare API key and name of stock to get
api_key = 'Tpk_cec90dded9cd4f3b9c0295462c57fbcd'
# name = 'AAPL' #Apple

colors = {
    'background': '#272E37',
    'text': '#A9A9A9',
    'dcc': '#A9A9A9',
    'dcctext': '#FFFFE0'
    }

#FUNCTIONS TO DO RATIO ANALYSIS AND RETRIEVE PRICES
def ratio_analysis(name, api_key):
    #create dictionary of url's to make separate API requests for each financial statement
    statements = ['balance-sheet','cash-flow','income']
    urls = {statement:'https://sandbox.iexapis.com/stable/stock/{}/{}?last=12&token={}'\
    .format(name,statement,api_key) for statement in statements}

    #create dictionary containing all financial statements requested from API
    #dictionary r has 3 keys, 1 for each financial statement
    #each key holds another nested dictionary with the 12 latest statements
    #starting with the most recent
    r = {statement:requests.get(url).json() for (statement,url) in urls.items()}

    #create list of columns that are desired in final dataframe
    col_labels = ['date','gross','net','EPS','roe','current','cash','debt-equity',\
                  'debt-assets','leverage','int-cov','debt-cov','dividend-cov']

    #each element in this list will be a list of ratios calculated for a given statement
    ratios_matrix = []

    #loop through each statement
    for i in range(0,len(r['balance-sheet']['balancesheet'])):
        bs = r['balance-sheet']['balancesheet']
        cf = r['cash-flow']['cashflow']
        ic = r['income']['income']
        
        #get year and quarter of filing
        date = bs[i]['fiscalDate']
        #create 'ratios' variable that will be used to store all calculated ratios
        #for a given balance sheet
        ratios = [date]
        
        #calculate profitability ratios
        try:
            gross_prof_marg = (ic[i]['grossProfit']) /ic[i]['totalRevenue'] * 100
            net_prof_marg = ic[i]['netIncome'] / ic[i]['totalRevenue'] * 100
        except:
            gross_prof_marg = 0
            net_prof_marg = 0
        eps = ic[i]['netIncome'] / bs[i]['commonStock']
        roe = ic[i]['netIncome'] / (bs[i]['shareholderEquity']) * 100
        # update 'ratios' list with profitability ratios
        ratios.extend([gross_prof_marg, net_prof_marg, eps, roe])
        
        #calculate liquidity ratios
        try:
            current_ratio = bs[i]['currentAssets'] / bs[i]['totalCurrentLiabilities']
        except:
            current_ratio = 0
        try:
            cash_ratio = bs[i]['currentCash'] / bs[i]['totalCurrentLiabilities']
        except:
            cash_ratio = 0
        #update 'ratios' list with liquidity ratios
        ratios.extend([current_ratio, cash_ratio])
        
        #calculate solvency ratios
        try:
            total_debt = bs[i]['longTermDebt'] + bs[i]['currentLongTermDebt']
            debt_equity = total_debt / bs[i]['shareholderEquity']
            debt_assets = total_debt / bs[i]['totalAssets']
        except:
            try:
                total_debt = bs[i]['longTermDebt']
                debt_equity = total_debt / bs[i]['shareholderEquity']
                debt_assets = total_debt / bs[i]['totalAssets']
            except:
                total_debt = 0
                debt_equity = 0
                debt_assets = 0
        leverage = bs[i]['totalAssets'] / bs[i]['shareholderEquity']
        #update 'ratios' list with solvency ratios
        ratios.extend([debt_equity, debt_assets, leverage])
        
        #calculate coverage ratios
        cfo = cf[i]['cashFlow']
        try:
            interest_paid = ic[i]['interestIncome']
            tax_paid = ic[i]['incomeTax']
            int_coverage = (cfo + tax_paid + interest_paid) / interest_paid
            debt_coverage = cfo / bs[i]['longTermDebt']
            dividend_coverage = cfo / (-1 * cf[i]['dividendsPaid'])
        except:
            interest_paid = 0
            int_coverage = 0
            debt_coverage = 0
            dividend_coverage = 0
        #update 'ratios' list with coverage ratios
        ratios.extend([int_coverage, debt_coverage, dividend_coverage])
        
        #update matrix with new element containing all ratios for a given balance sheet
        ratios_matrix.append(ratios)
    #convert list into a NumPy array
    ratios_matrix = np.array(ratios_matrix)
    #convert NumPy matrix to dataframe
    ratios_df = pd.DataFrame(ratios_matrix,columns = col_labels)
    
    #proper formatting and typing
    ratios_df = ratios_df.replace('nan',np.nan)
    ratios_df['date'] = pd.to_datetime(ratios_df['date'])
    ratios_df.iloc[:,1:] = ratios_df.iloc[:,1:].apply(pd.to_numeric,errors='coerce')
    ratios_df = ratios_df.sort_values(by='date').reset_index(drop=True)
    
    return ratios_df

def get_prices(df, name):
    if '.' in name:
        name= name.replace('.','-')
    firstdate = df.date.iloc[0]
    lastdate = datetime.datetime.today().strftime('%Y-%m-%d')

    prices = yf.Ticker(name).history(start = firstdate, end = lastdate).reset_index()[['Date','Close']]
    prices.columns = ['date','close']
    ticker = name
    return prices, ticker

#app layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.H1("Dashboard Header", 
            style = {
                'text-align': 'center', 
                'font-family': 'monospace',
                'color': colors['text']}),

    html.Div([
        html.H2('1st Section', 
            style = {
                'font-family': 'monospace',
                'color': colors['text']}),
    
        dcc.Input(id='select_stock',
                 value = 'AAPL', type = 'text'),
                 # style = {'font-family': 'monospace', 
                        # 'backgroundColor': colors['dcc'],
                        # 'color': colors['dcctext']}
        dcc.Graph(
        id = 'price_chart',
        figure = {}
        ),
        dcc.Graph(
        id='metric_chart',
        figure={}
        ),
    ])
    ])
    # html.Div([
    #     html.H2('2nd Section', 
    #         style={
    #             'font-family': 'monospace',
    #             'color': colors['text']})])
    # )
    
    #     dcc.Input(id='select_metric',
    #              value = 'Select other metric', type = 'text')
    #              # style={'font-family': 'monospace', 
    #              #        'backgroundColor': colors['dcc'],
    #              #        'color': colors['dcctext']}
    #     dcc.Graph(
    #     id='example-graph2',
    #     figure={}
    #     )
    # style={'width': '32%', 'align': 'right', 'display': 'inline-block'},
    
    # html.Div(
    #     ),
    
    # html.Br(),

    # dcc.Graph(
    #     id='example-graph3',
    #     figure={}
    # )


#connect Plotly graph with Dash components
@app.callback(
    Output(component_id = 'price_chart', component_property = 'figure'),
      # Output(),
      [Input(component_id='select_stock', component_property='value')]
    )

def update_price(selected_stock):
    df = ratio_analysis(selected_stock, api_key)
    prices, ticker = get_prices(df, selected_stock)

    #plot prices
    price_fig = px.line(prices, x='date', y='close')
    price_fig.update_layout(
        plot_bgcolor = colors['background'],
        paper_bgcolor = colors['background'],
        font_family = 'monospace',
        font_color = colors['text'],
        title = {
            'text': f'{ticker}',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return price_fig

if __name__ == '__main__':
    app.run_server(debug=True)
    
    
    
    
    