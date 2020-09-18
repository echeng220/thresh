# -*- coding: utf-8 -*-
"""
Automated fundamental analysis with IEX Cloud API
Created on Sat Jun 20 22:40:04 2020
@author: Evan
"""
#import required libraries
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from datetime import date
import calendar

#declare API key and name of stock to get
api_key = 'Tpk_cec90dded9cd4f3b9c0295462c57fbcd'
name = 'AAPL' #Apple
name2 = 'JPM'  #raytheon

def ratio_analysis(name,api_key):
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

testdf = ratio_analysis(name,api_key)
# testdf2 = ratio_analysis(name2,api_key)
# testdf

def get_prices(df,name):
    firstdate = df.date.iloc[0]
    lastdate = datetime.datetime.today().strftime('%Y-%m-%d')

    prices = yf.Ticker(name).history(start = firstdate, end = lastdate).reset_index()[['Date','Close']]
    prices.columns = ['date','close']
    ticker = name
    return prices, ticker

prices, ticker = get_prices(testdf,name)
# prices2, ticker2 = get_prices(testdf2,name2)

def plot_profit(prices, ticker, df):
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price [$]')
    ax1.plot(prices.date, prices.close, alpha = 0.3, color = 'dimgrey')
    ax1.set_ylim([0,1.1*max(prices.close)])
    ax1.fill_between(prices.date, 0, prices.close,color='dimgrey',alpha = 0.05)
    fig.autofmt_xdate()

    ax2 = ax1.twinx()
    plt.plot(df.date,df.gross,label='Gross Profit',color='lightcoral')
    plt.plot(df.date,df.net,label='Net Profit',color='mediumseagreen')
    plt.plot(df.date,df.roe,label='ROE',color='lightskyblue')
    plt.legend(bbox_to_anchor=(1,1,0.3,0.1))
    ax2.set_ylabel('Percent [%]')
    ax2.set_ylim([0,1.1*max(df.gross)])
    
    plt.title('Profitability Ratios for {}'.format(ticker))

    fig.tight_layout()
    return plt.show()

plot_profit(prices, ticker, testdf)
# plot_profit(prices2, ticker2, testdf2)

def plot_liquidity(prices, ticker, df):
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price [$]')
    ax1.plot(prices.date, prices.close, alpha = 0.3, color = 'dimgrey')
    ax1.set_ylim([0,1.1*max(prices.close)])
    ax1.fill_between(prices.date, 0, prices.close,color='dimgrey',alpha = 0.05)
    fig.autofmt_xdate()

    ax2 = ax1.twinx()
    plt.plot(df.date,df.current,label='Current Ratio',color='gold')
    plt.plot(df.date,df.cash,label='Cash Ratio',color='springgreen')
    plt.legend(bbox_to_anchor=(1.15,1,0.1,0.25))
    ax2.set_ylim([0,1.1*max(max(df.current),max(df.cash))])

    plt.title('Liquidity Ratios for {}'.format(ticker))
    
    fig.tight_layout()
    return plt.show()

plot_liquidity(prices, ticker, testdf)

def plot_solvency(prices, ticker, df):
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price [$]')
    ax1.plot(prices.date, prices.close, alpha = 0.3, color = 'dimgrey')
    ax1.set_ylim([0,1.1*max(prices.close)])
    ax1.fill_between(prices.date, 0, prices.close,color='dimgrey',alpha = 0.05)
    fig.autofmt_xdate()

    ax2 = ax1.twinx()
    plt.plot(df.date,df['debt-equity'],label='Debt-to-Equity',color='crimson')
    plt.plot(df.date,df['debt-assets'],label='Debt-to-Assets',color='darkorchid')
    plt.plot(df.date,df['leverage'],label='Leverage',color='peru')
    plt.plot(df.date,df['debt-cov'],label='Debt Coverage',color='steelblue')
    plt.legend(bbox_to_anchor=(1.15,1))
    ax2.set_ylim([0,1.1*max(max(df['debt-equity']),max(df['debt-assets']),\
                            max(df['leverage']),max(df['debt-cov']))])

    plt.title('Solvency Ratios for {}'.format(ticker))
    fig.tight_layout()
    return plt.show()

plot_solvency(prices, ticker, testdf)

def plot_coverage(prices, ticker, df):
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price [$]')
    ax1.plot(prices.date, prices.close, alpha = 0.3, color = 'dimgrey')
    ax1.set_ylim([0,1.1*max(prices.close)])
    ax1.fill_between(prices.date, 0, prices.close,color='dimgrey',alpha = 0.05)
    fig.autofmt_xdate()

    ax2 = ax1.twinx()
    plt.plot(df.date,df['int-cov'],label='Interest Coverage',color='forestgreen')
    plt.plot(df.date,df['dividend-cov'],label='Dividend Coverage',color='violet')
    plt.legend(bbox_to_anchor=(1.15,1,0.1,0.25))
    ax2.set_ylim([0,1.1*max(max(df['int-cov']), max(df['dividend-cov']))])

    plt.title('Coverage Ratios for {}'.format(ticker))
    fig.tight_layout()
    return plt.show()

plot_coverage(prices, ticker, testdf)

def plot_metric(prices, ticker, df, metric):
    fig, ax = plt.subplots(nrows=2,ncols=1)
    plt.subplot(2,1,1)
    plt.title(f'{ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price [$]')
    plt.plot(prices.date, prices.close, alpha = 0.3, color = 'dimgrey')
    plt.fill_between(prices.date, 0, prices.close,color='dimgrey',alpha = 0.05)
    plt.ylim([0,1.1*max(prices.close)])
    fig.autofmt_xdate()
    
    plt.subplot(2,1,2)
    plt.plot(df.date,df[metric],color='forestgreen')
    plt.ylabel('{}'.format(metric))
    fig.autofmt_xdate()
    
    plt.title('{} for {}'.format(metric,ticker))
    fig.tight_layout()
    return plt.show()

plot_metric(prices, ticker, testdf, 'debt-cov')
# plot_metric(prices2, ticker2, testdf2, 'debt-cov')

# def get_pe_ratio(df,prices):
#     df = df.merge(prices, on = 'date', how = 'left')

#     for i in range(len(df.close)):
#             if np.isnan(df.close[i]):
#                 try:
#                     closest_date = df.date[i] + datetime.timedelta(days = 1)
#                     df.close[i] = float(prices[prices.date == closest_date].close)
#                 except:
#                     try:
#                         closest_date = df.date[i] - datetime.timedelta(days = 1)
#                         df.close[i] = float(prices[prices.date == closest_date].close)
#                     except:
#                         closest_date = df.date[i] - datetime.timedelta(days = 3)
#                         df.close[i] = float(prices[prices.date == closest_date].close)
#     df['P/E'] = df.close / df.EPS
#     return df

# testdf = get_pe_ratio(testdf,prices)

plot_metric(prices, ticker, testdf, 'P/E')

# testurl = 'https://sandbox.iexapis.com/stable/ref-data/exchange/tsx/symbols?token={}'.format(api_key)
# testr = requests.get(testurl).json()

# testurl2 = 'https://sandbox.iexapis.com/stable/ref-data/exchange/tsx/symbols?token={}'.format(api_key)
# testr2 = requests.get(testurl).json()

#develop function to plot yield curve

def plot_yield_curve(today=datetime.date.today()):
    treasuries = {'13w':'^IRX','5y':'^FVX','10y':'^TNX','30y':'^TYX'}
    treasury_names = list(treasuries.keys())
    treasury_symbols = list(treasuries.values())
    treasury_yields = {}

    # today = datetime.date.today()
    day_of_week = calendar.day_name[today.weekday()]

    if day_of_week == 'Saturday':
        today = today - datetime.timedelta(days = 1)
    elif day_of_week == 'Sunday':
        today = today - datetime.timedelta(days = 2)
    new_day_of_week = calendar.day_name[today.weekday()]
    
    for bill in list(treasuries.values()):
        treasury_yields.update({treasury_names[treasury_symbols.index(bill)] :\
                        yf.Ticker(bill).history(start=today).Close[0]})

    yield_curve = pd.DataFrame(treasury_yields,index=[0]).transpose().reset_index()
    yield_curve.columns=['Treasury','Yield']
    # yield_curve = pd.DataFrame(treasury_yields,index=[0]).transpose().reset_index()
    # yield_curve.columns = ['Bond','Yield']
    # sns.barplot(data=yield_curve, palette = sns.cubehelix_palette(8),edgecolor='dimgrey')
    # plt.ylabel('Yield [%]')
    # plt.xlabel('Treasury Security')
    # plt.title('Yield Curve for {}, {}'.format(new_day_of_week,today))
    return yield_curve, treasury_yields #plt.show()

yc, ty =plot_yield_curve()

# plot_yield_curve(today=datetime.date(2000,2,2))

names={'SP500':'^GSPC','EAFE':'EFA','Russell2000':'^RUT',\
       'TIPS':'TIP','Gold':'GLD','REITs':'^RMZ'}

def get_prices(names):
    
    dict={}
    for i in range(0,len(names)):
        dict.update({list(names.keys())[i]:
        yf.Ticker(str(list(names.values())[i])).history(period='6mo')['Close']})
    #create pandas dataframe with info from yfinance
    prices = pd.DataFrame(dict)

    return prices

prices=get_prices(names).dropna()
returns=prices.pct_change(fill_method='ffill').dropna()
cumul_returns=(1 + returns).cumprod()
total_returns = (cumul_returns - 1) * 100

total_returns.plot()
plt.ylabel('Cummulative Returns [%]')
plt.title('6 Month Returns of Common Benchmarks')
plt.legend(bbox_to_anchor=(1,1))