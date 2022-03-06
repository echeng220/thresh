import requests
import pandas as pd
import yfinance as yf
import datetime

import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from plotly.subplots import make_subplots


API_KEY = 'Tpk_cec90dded9cd4f3b9c0295462c57fbcd'

COLORS = {
    'background': '#272E37',
    'text': '#A9A9A9',
    'dcc': '#A9A9A9',
    'dcctext': '#FFFFE0'
}

COL_LABLES = ['date','Gross Profit [%]','Net Profit [%]','EPS','ROE','Current Ratio',
    'Cash Ratio','Debt-to-Equity','Debt-to-Assets', 'Leverage','Interest Coverage',
    'Debt Coverage', 'Dividend Coverage']

BENCHMARKS = {
    'S&P 500':'^GSPC',
    'Russell 2000':'^RUT',
    '10 Year':'^TNX',
    'High Yield Corp':'HYG',
    'Gold':'GC=F'
}

INDICATORS = {'Real GDP':'A191RL1Q225SBEA','Unemployment Rate':'UNRATE'}

def get_company_name(ticker):
    info_url = f'https://sandbox.iexapis.com/stable/stock/{ticker}/company?&token={API_KEY}'
    info_r = requests.get(info_url).json()
    company = info_r['companyName']
    return company

def get_company_statements(ticker, statement):
    '''Get last 12 financial statements of a company.'''
    url = f'https://sandbox.iexapis.com/stable/stock/{ticker}/{statement}?last=12&token={API_KEY}'
    statements = requests.get(url).json()
    if statement == 'balance-sheet':
        return statements['balancesheet']
    elif statement == 'cash-flow':
        return statements['cashflow']
    elif statement == 'income':
        return statements['income']

def get_indicator(indicator):
    '''Last 24 hours of economic data.'''
    url = f'https://sandbox.iexapis.com/stable/time-series/economic/{INDICATORS[indicator]}?last=24&token={API_KEY}'
    r = requests.get(url).json()
    indicator_data = [point['value'] for point in r]
    date_data = [datetime.datetime.fromtimestamp(point['updated'] / 1000).strftime('%Y-%m-%d')\
        for point in r]
    indicator_dict = {indicator: indicator_data, 'date': date_data}
    indicator_df = pd.DataFrame(indicator_dict)
    indicator_df = indicator_df.sort_values(by='date')
    return indicator_df

def gross_profit_margin(gross_profit, total_revenue):
    try:
        return gross_profit / total_revenue * 100
    except:
        return 0

def net_profit_margin(net_income, total_revenue):
    try:
        return net_income / total_revenue * 100
    except:
        return 0

def eps(net_income, common_stock):
    try:
        return net_income / common_stock
    except:
        return 0

def current_ratio(current_assets, total_current_liabilities):
    try:
        return current_assets / total_current_liabilities
    except:
        return 0

def cash_ratio(current_cash, total_current_liabilities):
    try:
        return current_cash / total_current_liabilities
    except:
        return 0

def total_debt(long_term_debt, current_long_term_debt):
    try:
        return long_term_debt + current_long_term_debt
    except:
        if long_term_debt:
            return long_term_debt
        else:
            return 0

def debt_equity_ratio(total_debt, shareholder_equity):
    try:
        return total_debt / shareholder_equity
    except:
        return 0
        
def debt_assets_ratio(total_debt, total_assets):
    try:
        return total_debt / total_assets
    except:
        return 0

def leverage_ratio(total_assets, shareholder_equity):
    try:
        return total_assets / shareholder_equity
    except:
        return 0

def dividend_coverage(cash_flow, dividends_paid):
    try:
        return cash_flow / (-1 * dividends_paid)
    except:
        return 0

def eps(net_income, common_stock):
    try:
        return net_income / common_stock
    except:
        return 0

def roe(net_income, shareholder_equity):
    try:
        return net_income / shareholder_equity * 100
    except:
        return 0

def interest_coverage(cash_flow, tax_paid, interest_income):
    try:
        return (cash_flow + tax_paid + interest_income) / interest_income
    except:
        return 0

def debt_coverage(cash_flow, long_term_debt):
    try:
        return cash_flow / long_term_debt
    except:
        return 0

def dividend_coverage(cash_flow, dividends_paid):
    try:
        return cash_flow / (-1 * dividends_paid)
    except:
        return 0

def get_prices(firstdate, ticker):
    if '.' in ticker:
        ticker = ticker.replace('.', '-')

    lastdate = datetime.datetime.today().strftime('%Y-%m-%d')

    prices = yf.Ticker(ticker).history(start=firstdate, end=lastdate).reset_index()[['Date', 'Close']]
    prices.columns = ['date', 'close']
    return prices, ticker

def get_benchmark_prices(ticker):
    prices = yf.Ticker(ticker).history(period='6mo')['Close'].values
    return prices

def benchmark_returns():
    benchmark_prices = {}
    for i in range(0,len(BENCHMARKS)):
        benchmark_prices.update({list(BENCHMARKS.keys())[i]:
        yf.Ticker(str(list(BENCHMARKS.values())[i])).history(period='6mo')['Close']})
            
    prices_df = pd.DataFrame(benchmark_prices).dropna()
    returns = prices_df.pct_change(fill_method='ffill').dropna()
    cumul_returns = (1 + returns).cumprod()
    total_returns = (cumul_returns - 1) * 100

    return total_returns

def plot_prices(prices, company):
    price_fig = px.area(prices, x='date', y='close')
    if prices['close'].iloc[0]<prices['close'].iloc[-1]:
        fill='#98FB98'
    else:
        fill='#CD5C5C'
    price_fig.update_traces(line_color=fill)
    price_fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis_title='Closing Price [$]',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_family='monospace',
        font_color=COLORS['text'],
        title = {
            'text': f'{company.ticker}: {company.name}',
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )
    return price_fig
    
def plot_metrics(ratios_df, prices, selected_metric, company):
    metric_fig = px.line(ratios_df, x='date', y=selected_metric)
    metric_fig.update_xaxes(range=[prices['date'].iloc[0], prices['date'].iloc[-1]])
    metric_fig.update_traces(line_color='darkturquoise')
    metric_fig.update_layout(
        margin = dict(l=20, r=20, t=20, b=20),
        plot_bgcolor = COLORS['background'],
        paper_bgcolor = COLORS['background'],
        font_family = 'monospace',
        font_color = COLORS['text'],
        title = {
            'text': f'{company.name} ({company.ticker}) : {selected_metric}',
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return metric_fig

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

class BalanceSheet:
    '''
    Balance sheet and calculations.
    '''
    def __init__(self, statement):
        self.date_ = statement['fiscalDate']
        self.common_stock = statement['commonStock']
        self.shareholder_equity = statement['shareholderEquity']
        self.current_assets = statement['currentAssets']
        self.current_cash = statement['currentCash']
        self.total_current_liabilities = statement['totalCurrentLiabilities']
        self.long_term_debt = statement['longTermDebt']
        self.current_long_term_debt = statement['currentLongTermDebt']
        self.shareholder_equity = statement['shareholderEquity']
        self.total_assets = statement['totalAssets']

class CashFlow:
    '''
    Cash flow and calculations.
    '''
    def __init__(self, statement):
        self.date_ = statement['fiscalDate']
        self.cash_flow = statement['cashFlow']
        self.dividends_paid = statement['dividendsPaid']

class IncomeStatement:
    '''
    Income statement and calculations.
    '''
    def __init__(self, statement):
        self.date_ = statement['fiscalDate']
        self.gross_profit = statement['grossProfit']
        self.total_revenue = statement['totalRevenue']
        self.net_income = statement['netIncome']
        self.interest_income = statement['interestIncome']
        self.income_tax = statement['incomeTax']

class Company:
    def __init__(self, ticker):
        self.ticker = ticker
        self.name = get_company_name(ticker)
        self.balance_sheets = get_company_statements(ticker, 'balance-sheet')
        self.cash_flow_statements = get_company_statements(ticker, 'cash-flow')
        self.income_statements = get_company_statements(ticker, 'income')

        self.dates = []
        self.gross_profit_margins = []
        self.net_profit_margins = []
        self.epss = []
        self.roes = []
        self.current_ratios = []
        self.cash_ratios = []
        self.total_debts = []
        self.debt_equity_ratios = []
        self.debt_assets_ratios = []
        self.leverage_ratios = []
        self.interest_coverages = []
        self.debt_coverages = []
        self.dividend_coverages = []

        self.ratios = []
        self.ratios_dict = {}
        
    def num_of_statements_matches(self):
        if len(self.balance_sheets) == len(self.cash_flow_statements) \
            and len(self.balance_sheets) == len(self.income_statements):
            return True
        else:
            return False

    def compute_ratios(self):
        if self.num_of_statements_matches():
            num_statements = len(self.balance_sheets)

            for i in range(0, num_statements):
                balance_sheet = BalanceSheet(self.balance_sheets[i])
                income_statement = IncomeStatement(self.income_statements[i])
                cash_flow_statement = CashFlow(self.cash_flow_statements[i])

                self.dates.append(balance_sheet.date_)

                self.gross_profit_margins.append(
                    gross_profit_margin(income_statement.gross_profit, income_statement.total_revenue)
                )
                self.net_profit_margins.append(
                    gross_profit_margin(income_statement.net_income, income_statement.total_revenue)
                )
                self.epss.append(
                    eps(income_statement.net_income, balance_sheet.common_stock)
                )
                self.roes.append(
                    roe(income_statement.net_income, balance_sheet.shareholder_equity)
                )
                self.current_ratios.append(
                    current_ratio(balance_sheet.current_assets, balance_sheet.total_current_liabilities)
                )
                self.cash_ratios.append(
                    cash_ratio(balance_sheet.current_cash, balance_sheet.total_current_liabilities)
                )
                total_debt_value = total_debt(balance_sheet.long_term_debt, balance_sheet.current_long_term_debt)
                self.total_debts.append(total_debt_value)

                self.debt_equity_ratios.append(
                    debt_equity_ratio(total_debt_value, balance_sheet.shareholder_equity)
                )
                self.debt_assets_ratios.append(
                    debt_assets_ratio(total_debt_value, balance_sheet.total_assets)
                )
                self.leverage_ratios.append(
                    leverage_ratio(balance_sheet.total_assets, balance_sheet.shareholder_equity)
                )
                self.interest_coverages.append(
                    interest_coverage(cash_flow_statement.cash_flow,
                    income_statement.income_tax, income_statement.interest_income)
                )
                self.debt_coverages.append(
                    debt_coverage(cash_flow_statement.cash_flow, balance_sheet.long_term_debt)
                )
                self.dividend_coverages.append(
                    dividend_coverage(cash_flow_statement.cash_flow, cash_flow_statement.dividends_paid)
                )
            
            self.ratios = [
                self.dates,
                self.gross_profit_margins,
                self.net_profit_margins,
                self.epss,
                self.roes,
                self.current_ratios,
                self.cash_ratios,
                self.debt_equity_ratios,
                self.debt_assets_ratios,
                self.leverage_ratios,
                self.interest_coverages,
                self.debt_coverages,
                self.dividend_coverages
            ]
            self.ratios_dict = dict(zip(COL_LABLES, self.ratios))
            self.ratios_df = pd.DataFrame(self.ratios_dict)

            self.ratios_df['date'] = pd.to_datetime(self.ratios_df['date'])
            self.ratios_df.iloc[:,1:] = self.ratios_df.iloc[:,1:].apply(pd.to_numeric,errors='coerce')
            self.ratios_df = self.ratios_df.sort_values(by='date').reset_index(drop=True)
        return self.ratios_df


if __name__ == '__main__':
    ticker = 'AAPL'
    api_key = 'Tpk_cec90dded9cd4f3b9c0295462c57fbcd'
    print(get_company_name(ticker))
    company = Company(ticker)
    # df = company.compute_ratios()
    # benchmark_returns()
    ind = get_indicator('Real GDP')
    # r = get_indicator('Real GDP')
