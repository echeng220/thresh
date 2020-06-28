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
name = 'UTX' #Raytheon Technologies

#create dictionary of url's to make separate API requests for each financial statement
# statements = ['balance-sheet','cash-flow','income']
# urls = {statement:'https://sandbox.iexapis.com/stable/stock/{}/{}?last=12&token={}'\
#     .format(name,statement,api_key) for statement in statements}

#create dictionary containing all financial statements requested from API
#dictionary r has 3 keys, 1 for each financial statement
#each key holds another nested dictionary with the 12 latest statements
#starting with the most recent
# r = {statement:requests.get(url).json() for (statement,url) in urls.items()}

i = 0
#get most recent statements
bs = r['balance-sheet']['balancesheet'][i]
cf = r['cash-flow']['cashflow'][i]
ic = r['income']['income'][i]

sec_url = 'https://sandbox.iexapis.com/stable/time-series/REPORTED_FINANCIALS/UTX/10-Q?last=12&token={}'\
    .format(api_key)
r1 = requests.get(sec_url)
sec = r1.json()

col_labels = ['year','quarter','current','cash','debt-equity','debt-assets','leverage', \
              'interest','debt','dividend','gross%','net%','roe%']
ratios_df = pd.DataFrame(columns = col_labels)

ratios_matrix = []

for i in range(0,len(sec) - 1):
    #get report date
    year = sec[i]['formFiscalYear']
    quarter = sec[i]['formFiscalQuarter']
    ratios = [year,quarter]
    past_report = sec[i+1]
    
    #liquidity ratios
    current_ratio = sec[i]['AssetsCurrent'] / sec[i]['LiabilitiesCurrent']
    cash_ratio = sec[i]['CashAndCashEquivalentsAtCarryingValue'] / sec[i]['LiabilitiesCurrent']
    ratios.extend([current_ratio, cash_ratio])

    #solvency ratios
    total_debt = sec[i]['LongTermDebtAndCapitalLeaseObligations'] \
        + sec[i]['LongTermDebtAndCapitalLeaseObligationsCurrent'] \
            + sec[i]['OtherLongTermDebt']
    debt_equity = total_debt / sec[i]['StockholdersEquity']
    debt_assets = total_debt / sec[i]['Assets']
    leverage = sec[i]['Assets'] / sec[i]['StockholdersEquity']
    ratios.extend([debt_equity, debt_assets, leverage])
    
    #coverage ratio analysis
    cfo = sec[i]['NetCashProvidedByUsedInOperatingActivitiesContinuingOperations']
    interest_exp = sec[i]['InterestExpense']
    tax_exp =sec[i]['IncomeTaxExpenseBenefit']
    def_tax_prov = sec[i]['DeferredIncomeTaxExpenseBenefit']
    def_tax_prov_past = sec[i+1]['DeferredIncomeTaxExpenseBenefit']
    tax_paid = tax_exp + (def_tax_prov - def_tax_prov_past)
    int_coverage = (cfo + tax_paid + interest_exp) / interest_exp
    try:
        debt_coverage = cfo / sec[i]['RepaymentsOfLongTermDebt']
    except:
        debt_coverage = cfo / sec[i]['ProceedsFromRepaymentsOfLongTermDebtAndCapitalSecurities']
    dividend_coverage = cfo / sec[i]['PaymentsOfDividendsCommonStock']
    ratios.extend([int_coverage, debt_coverage, dividend_coverage])
    
    #profitability ratios
    try:
        gross_prof_marg = (sec[i]['Revenues'] - sec[i]['CostsAndExpenses']) \
            / sec[i]['Revenues'] * 100
        net_prof_marg = sec[i]['NetIncomeLoss'] / sec[i]['Revenues'] * 100
        roe = sec[i]['NetIncomeLoss'] / ((sec[i]['StockholdersEquity'] \
                              + sec[i]['StockholdersEquity']) / 2) * 100
    except:
        gross_prof_marg = (sec[i]['SalesRevenueNet'] - sec[i]['CostsAndExpenses']) \
            / sec[i]['SalesRevenueNet'] * 100
        net_prof_marg = sec[i]['NetIncomeLoss'] / sec[i]['SalesRevenueNet'] * 100
        roe = sec[i]['NetIncomeLoss'] / ((sec[i]['StockholdersEquity'] \
                              + sec[i]['StockholdersEquity']) / 2) * 100

    ratios.extend([gross_prof_marg, net_prof_marg, roe])

    ratios_matrix.append(ratios)

ratios_matrix_np = np.array(ratios_matrix)

ratios_df = pd.DataFrame(ratios_matrix_np,columns = col_labels)
ratios_df[col_labels[1:]] = ratios_df[col_labels[1:]].astype(float)

ratios_df