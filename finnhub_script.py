# -*- coding: utf-8 -*-
"""
Automated fundamental analysis with Finnhub API
Created on Sat Jun 20 22:40:04 2020
@author: Evan
"""
#import required libraries
import requests
import pandas as pd
import numpy as np
from pandas import json_normalize

#declare API key and name of stock to get
api_key = 'Tpk_cec90dded9cd4f3b9c0295462c57fbcd'
name = 'RTX' #Raytheon Technologies

#create dictionary of url's to make separate API requests for each financial statement
statements = ['balance-sheet','cash-flow','income']
urls = {statement:'https://sandbox.iexapis.com/stable/stock/{}/{}?last=12&token={}'\
    .format(name,statement,api_key) for statement in statements}

#create dictionary containing all financial statements requested from API
r = {statement:requests.get(url).json() for (statement,url) in urls.items()}

#prints most recent balance sheet
r['balance-sheet']['balancesheet'][0]

# company = 'https://sandbox.iexapis.com/stable/stock/RTX/company?token={}'.format(api_key)

# col_labels = ['period','current','cash','debt-equity','debt-assets','leverage', \
#               'interest','debt','dividend','gross%','net%','roe%']
# ratios_df = pd.DataFrame(columns = col_labels)

for i in range(0,len(df)-1):
    date = str(df['data'][i]['year']) + 'Q' + str(df['data'][i]['quarter'])
    ratios = [date]

    #balance sheet analysis
    bs = df['data'][i]['report']['bs']
    bs_past = df['data'][i+1]['report']['bs']
    #liquidity ratios
    current_ratio = bs['AssetsCurrent'] / bs['LiabilitiesCurrent']
    cash_ratio = (bs['CashAndCashEquivalentsAtCarryingValue'])/bs['LiabilitiesCurrent']
    # print('\nCurrent Ratio: ',round(current_ratio,2),'\nCash Ratio: ' \
    #   ,round(cash_ratio,2),'\n')
    ratios.extend([current_ratio, cash_ratio])

    #solvency ratios
    total_debt = bs['LongTermDebtAndCapitalLeaseObligations'] \
        + bs['LongTermDebtAndCapitalLeaseObligationsCurrent']
    debt_equity = total_debt / bs['StockholdersEquity']
    debt_assets = total_debt / bs['Assets']
    leverage = bs['Assets'] / bs['StockholdersEquity']
    # print('Debt-to-Equity Ratio: ', round(debt_equity,2),'\nDebt-to-Assets Ratio: '\
    #     ,round(debt_assets,2),'\nLeverage Ratio:',round(leverage,2),'\n')
    ratios.extend([debt_equity, debt_assets, leverage])
    
    #grab income statement info
    ic = df['data'][i]['report']['ic']
    ic_past = df['data'][i+1]['report']['ic']

    #grab cash flow statement info
    cf = df['data'][i]['report']['cf']
    cf_past = df['data'][i+1]['report']['cf']
    cfo = cf['NetCashProvidedByUsedInOperatingActivitiesContinuingOperations']
    interest_exp = ic['InterestExpense']
    tax_exp =ic['IncomeTaxExpenseBenefit']
    def_tax_prov = bs['DeferredTaxAssetsNetNoncurrent']
    def_tax_prov_past = bs_past['DeferredTaxAssetsNetNoncurrent']
    tax_paid = tax_exp + (def_tax_prov - def_tax_prov_past)
    int_coverage = (cfo + tax_paid + interest_exp) / interest_exp
    debt_coverage = cfo / cf['RepaymentsOfLongTermDebt']
    dividend_coverage = cfo / cf['PaymentsOfDividendsCommonStock']
    # print('Interest Coverage Ratio: ', round(int_coverage,2),'\nDebt Coverage : '\
    #   ,round(debt_coverage,2),'\nDividend Coverage Ratio:'\
    #       ,round(dividend_coverage,2),'\n')
    ratios.extend([int_coverage, debt_coverage, dividend_coverage])
    
    #profitability ratios
    gross_prof_marg = (ic['Revenues'] - ic['CostsAndExpenses']) / ic['Revenues'] * 100
    net_prof_marg = ic['NetIncomeLoss'] / ic['Revenues'] * 100
    roe = ic['NetIncomeLoss'] / ((bs['StockholdersEquity'] \
                              + bs_past['StockholdersEquity']) / 2) * 100

    # print('Gross Profit Margin: ',round(gross_prof_marg,2),\
    #   '%*\nNet Profit Margin: ',round(net_prof_marg,2),'%*\nROE: ' \
    #   ,round(roe,2),\
    #       '%*\n*Finnhub API doesn\'t indicate whether income is positive or negative')
    ratios.extend([gross_prof_marg, net_prof_marg, roe])

    ratios_matrix.append(ratios)

ratios_matrix_np = np.array(ratios_matrix)

ratios_df = pd.DataFrame(ratios_matrix_np,columns = col_labels)
ratios_df[col_labels[1:]] = ratios_df[col_labels[1:]].astype(float)
