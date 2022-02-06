from datetime import datetime as dt
import calendar

import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from functions import *

def plot_benchmarks():
    total_returns = benchmark_returns()

    returns_fig = px.line(total_returns,
        x=total_returns.index,
        y=list(BENCHMARKS.keys()))

    returns_fig.update_layout(
        margin = dict(l=60, r=60, t=60, b=60),
        yaxis_title = 'Total Returns [%]',
        legend = dict(
            orientation='h',
            yanchor='bottom',
            y=-0.35,
            xanchor='left',
            x=0
        ),
        legend_title_text='BENCHMARKS:\n',
        plot_bgcolor = COLORS['background'],
        paper_bgcolor = COLORS['background'],
        font_family = 'monospace',
        font_color = COLORS['text'],
        title = {
            'text': '6 Month Returns of Common BENCHMARKS',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    return returns_fig

def plot_econ_indicators():
    """Update the economic indicator chart with the selected indicator."""

    #create dictionary containing all economic indicators requested from API
    gdp_df = get_indicator('Real GDP')
    unemployment_df = get_indicator('Unemployment Rate')
    
    econ_fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=('Real GDP (USA)', 'Unemployment Rate (USA)')
    )
    econ_fig.append_trace(
        go.Scatter(
            x=gdp_df['date'],
            y=gdp_df['Real GDP'],
            mode='lines',
            line={'color': 'darkturquoise'}
        ),
        row=1,
        col=1
    )
    econ_fig.append_trace(
        go.Scatter(
            x=unemployment_df['date'],
            y=unemployment_df['Unemployment Rate'],
            mode='lines',
            line={'color': 'dodgerblue'}
        ),
        row=1,
        col=2
    )
    econ_fig.update_layout(
        margin=dict(l=70, r=70, t=70, b=70),
        showlegend = False,
        plot_bgcolor = COLORS['background'],
        paper_bgcolor = COLORS['background'],
        font_family = 'monospace',
        font_color = COLORS['text'],
    )
    return econ_fig 

app = dash.Dash(__name__)
server = app.server

#app layout
app.layout = html.Div(
    style={'backgroundColor': COLORS['background']},
    children=[
        html.H1("thresh (v.1): A Fundamental & Macroeconomic Analysis Dashboard", 
            style = {
                'text-align': 'center', 
                'font-family': 'monospace',
                'color': COLORS['text']}),
        html.Div([
            html.H2('Fundamental Analysis', 
                style = {
                    'text-align': 'center',
                    'font-family': 'monospace',
                    'color': COLORS['text']}),
            html.Div([
                dcc.Markdown(
                    '''### Ticker Symbol:''',
                    style = {
                        'font-family': 'monospace',
                        'color': COLORS['text']
                    }
                )
            ],
            style={'width': '15%', 'display': 'inline-block'}
            ),
        
            html.Div([             
                dcc.Input(
                    id='select_stock',
                    value = 'AAPL', type = 'text'
                ),
                ],
                style={'width': '85%', 'display': 'inline-block'}
                ),
            html.Div([
                dcc.Markdown(
                    '''### Fundamental Metric:''',
                    style = {
                        'font-family': 'monospace',
                        'color': COLORS['text']
                    }
                )
            ],
            style={'width':'18%','display':'inline-block','justify-content':'center'}
            ),
            html.Div([
                dcc.Dropdown(id='metric',
                    options=[
                        {'label': col, 'value': col} for col in COL_LABLES[1:]],
                    value='Net Profit [%]',
                    style={'font-family':'monospace'}
                )
            ],
            style={'width':'81%','display':'inline-block','justify-content':'center'}
            ),
            html.Button(id='search-button',
                    children='Refresh',
                    style={
                        'backgroundColor': 'powderblue',
                        'font-family': 'monospace',
                        'margin-left': '93%'
                    }
            ),
            dcc.Graph(
                id = 'price_chart',
                figure = {}
            ),

            dcc.Graph(
                id='metric_chart',
                figure={}
            )
        ],
        style={'width': '67%', 'display': 'inline-block'}
        ), 
    
        html.Div([
            html.Div([
                html.H2(
                    'Yield Curve & Benchmark Returns', 
                    style = {
                        'text-align': 'center',
                        'font-family': 'monospace',
                        'color': COLORS['text']
                    }
                ),
                html.Div([
                    dcc.Markdown(
                        """### Date:""",
                        style = {
                            'text-align': 'center',
                            'font-family': 'monospace',
                            'color': COLORS['text']
                        }
                    )
                ],
                style={'width':'22%','display':'inline-block','justify-content':'center'}
                ),
                html.Div([
                    dcc.DatePickerSingle(
                        id='yield_curve_date',
                        min_date_allowed=dt(1965, 7, 7), 
                        max_date_allowed=datetime.date.today(),
                        initial_visible_month=datetime.date.today(),
                        date=datetime.date.today(),
                        style={
                            'font-family': 'monospace', 
                            'backgroundColor': COLORS['dcc'],
                            'color': COLORS['dcctext']
                        }
                    )
                ],
                style={'width': '77%', 'display': 'inline-block'}
                ),
            ]),
            html.Div([
                dcc.Graph(
                    id='yield_curve',
                    figure={}
                ),
                dcc.Graph(
                    id='returns_chart',
                    figure=plot_benchmarks()
                )
            ])
        ],
        style={
            'width': '33%',
            'align': 'right',
           'display': 'inline-block'
        }
        ), 
        html.Div([
            html.H2(
                'Economic Indicators',
                style={
                    'text-align': 'center',
                    'font-family': 'monospace',
                    'color': COLORS['text']
                }
            ),
            dcc.Graph(
                id='econ_graph',
                figure=plot_econ_indicators()
            )
        ]
        )
    ]
)

#connect Plotly price/analysis graphs with Dash components
@app.callback(
    Output(component_id='price_chart', component_property='figure'),
    Output(component_id='metric_chart', component_property='figure'),
    [Input(component_id='search-button', component_property='n_clicks'),
    State(component_id='select_stock', component_property='value'),
    State(component_id='metric', component_property='value')]
    )

def update_charts(n_clicks, selected_stock, selected_metric):
    """Update the price chart and fundamental analysis
    for a selected stock. Inputs are the selected stock and chosen 
    fundamentals metric."""
    if n_clicks is not None:
        company = Company(selected_stock)
    else:
        company = Company('AAPL')

    ratios_df = company.compute_ratios()

    startdate = ratios_df.iloc[0]['date']
    prices, ticker = get_prices(startdate, selected_stock)

    #plot prices
    price_fig = plot_prices(prices, company)

    #plot metrics
    metric_fig = plot_metrics(ratios_df, prices, selected_metric, company)
        

    return price_fig, metric_fig

#connect Plotly yield curve/return history with Dash components
@app.callback(
    Output(component_id='yield_curve', component_property='figure'),
    Input(component_id='yield_curve_date', component_property='date')
    )
def update_yield_curve(selected_date):
    """Update the yield curve with the selected date (default today),
    and show the previous 6 months of returns for some benchmarks."""
    
    treasuries = {'13 Week':'^IRX','5 Year':'^FVX','10 Year':'^TNX',\
                  '30 Year':'^TYX'}
    treasury_names = list(treasuries.keys())
    treasury_symbols = list(treasuries.values())
    treasury_yields = {}
    
    selected_date = dt.strptime(selected_date,'%Y-%m-%d')
    day_of_week = calendar.day_name[selected_date.weekday()]
    if 'Saturday' in day_of_week:
        selected_date = selected_date - datetime.timedelta(days = 1)
    elif 'Sunday' in day_of_week:
        selected_date = selected_date - datetime.timedelta(days = 2)
    elif 'Friday' in day_of_week:
        selected_date = selected_date - datetime.timedelta(days = 1)
    elif 'Monday' in day_of_week:
        selected_date = selected_date - datetime.timedelta(days = 4)
    day_of_week = calendar.day_name[selected_date.weekday()]
    selected_date = selected_date.strftime('%Y-%m-%d')
    
    for bill in list(treasuries.values()):
        treasury_yields.update({treasury_names[treasury_symbols.index(bill)] :\
                        yf.Ticker(bill).history(start=selected_date).Close[0]})

    yields = pd.DataFrame(treasury_yields,index=[0]).transpose().reset_index()
    yields.columns = ['Treasury Security','Yield [%]']
    yield_curve = px.bar(yields,x='Treasury Security',y='Yield [%]',\
            color='Treasury Security',color_discrete_sequence=\
                ['azure','paleturquoise','darkturquoise','dodgerblue'])
    yield_curve.update_layout(
        margin = dict(l=60, r=60, t=60, b=60),
        showlegend= False,
        plot_bgcolor = COLORS['background'],
        paper_bgcolor = COLORS['background'],
        font_family = 'monospace',
        font_color = COLORS['text'],
        title = {
            'text': f'Yield Curve for {day_of_week}, {selected_date}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return yield_curve

if __name__ == '__main__':
    app.run_server()
    