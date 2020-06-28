# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 20:00:54 2020

@author: Evan
"""
#import required libraries
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

#manually enter name of stocks from the screener
names = ['CNU.TO','CAR-UN.TO','ABX.TO','GRT-UN.TO']

tickers = [yf.Ticker(name) for name in names]
returns = []

for i in range(0,len(tickers)):
    returns.append(tickers[i].history(period='ytd')['Close'])
    try:
        trailing_pe = tickers[i].info['trailingPE']
        fwd_pe = tickers[i].info['forwardPE']
        p_b = tickers[i].info['priceToBook']
        nav = tickers[i].info['navPrice']
        beta = tickers[i].info['beta']
        shares = tickers[i].info['sharesOutstanding']
        
        #estimate earnings based on P/E ratio and current trading price
        earnings = returns[i][-1] / trailing_pe
        #calculate a target price based on an ideal P/E ratio
        target_pe = 13
        target_price = target_pe * earnings
        
        print(tickers[i].info['shortName'].upper(),'\n',
          'Trailing PE:',trailing_pe,'\nForward PE:',fwd_pe,
          '\nPrice/Book:',p_b,'\nNAV:',nav,'\nBeta:',beta)

        #create array for plotting target price on graph
        time_range = [returns[i].index[0], returns[i].index[-1]]
        target_line = [target_price, target_price]
        ax0 = plt.plot(returns[i].index,returns[i], label = tickers[i].info['shortName'])
        plt.plot(time_range, target_line,label = 'Target for {}'.format(tickers[i].info['shortName']))
        plt.annotate(round(target_price,2), xy = (returns[i].index[0], target_price + 3))
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend(bbox_to_anchor = (1.85,1),loc='upper right')    
    except:
         print('No info available for {}'.format(names[i]))


