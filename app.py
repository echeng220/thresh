from datetime import datetime as dt
import calendar
from json import JSONDecodeError

import plotly.express as px  # (version 4.7.0)

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from functions import *

app = dash.Dash(__name__, eager_loading=True)
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
    """
    Update the price chart and fundamental analysis
    for a selected stock. Inputs are the selected stock and chosen 
    fundamentals metric.
    """
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
    """
    Update the yield curve with the selected date (default today),
    and show the previous 6 months of returns for some benchmarks.
    """
    
    treasuries = {'13 Week':'^IRX','5 Year':'^FVX','10 Year':'^TNX',\
                  '30 Year':'^TYX'}
    treasury_names = list(treasuries.keys())
    treasury_symbols = list(treasuries.values())
    treasury_yields = {}
    
    selected_date = dt.strptime(selected_date,'%Y-%m-%d')
    day_of_week = calendar.day_name[selected_date.weekday()]
    
    for bill in treasury_symbols:
        name = treasury_names[treasury_symbols.index(bill)]
        try:
            yield_df = yf.Ticker(bill).history(start=selected_date)
            if 'Close' in yield_df and len(yield_df.Close > 0):
                _yield = yield_df.Close[0]
            else:
                prev_date = selected_date
                _yield = None
                while not _yield:
                    prev_date = prev_date - datetime.timedelta(days = 1)
                    _yield = yf.Ticker(bill).history(start=prev_date).Close[0]
        except JSONDecodeError:
            _yield = 0
        treasury_yields.update({name: _yield})

    yields = pd.DataFrame(treasury_yields,index=[0]).transpose().reset_index()
    yields.columns = ['Treasury Security', 'Yield [%]']
    yield_curve = px.bar(
        yields,
        x='Treasury Security',
        y='Yield [%]',
        color='Treasury Security',
        color_discrete_sequence=['azure','paleturquoise','darkturquoise','dodgerblue']
    )
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
            'yanchor': 'top'
        }
    )
    return yield_curve

if __name__ == '__main__':
    app.run_server()
    