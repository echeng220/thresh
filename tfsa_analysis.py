#credit to codingfinance.com for inspiration
#https://www.codingfinance.com/post/2018-04-25-portfolio-beta-py/

#import required libraries
import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns

#create dictionary of security names for each portfolio
tfsa={'algonquin':'AQN.TO','scotia':'BNS.TO','BMO':'BMO.TO',
       'TD':'TD','TFI':'TFII.TO','SNC':'SNC.TO','RBC':'RY.TO',
       'restaurant':'QSR.TO','pembina':'PPL.TO','parkland':'PKI.TO','nutrien':'NTR.TO',
       'manulife':'MFC.TO','healthcare etf':'XHC.TO',
       'investment grade corp ETF':'PSB.TO','gibson':'GEI.TO',
       'enbridge':'ENB.TO','dollarama':'DOL.TO','chemtrade':'CHE-UN.TO',
       'CNR':'CNR.TO','brookfield infrastructure':'BIP-UN.TO',
       'brookfield am':'BAM-A.TO',
       'ultra short bonds':'ZST-L.TO','india etf':'ZID.TO',
       'us banks':'ZUB.TO','intl etf':'XAW.TO'}
rrsp={'tsx index':'XIU.TO','sp500 etf':'XSP.TO','cdn div etf':'XDV.TO',
      'ultra short bonds':'ZST-L.TO','nasdaq etf':'ZQQ.TO'}
uscash={'carrier':'CARR','otis':'OTIS','google':'GOOGL','united/raytheon':'RTX'}
cdncash={'TD':'TD','cdn etf':'VCN.TO','intl etf':'XAW.TO'}
portfolios={'TFSA':tfsa,'RRSP':rrsp,'US Cash':uscash,'CAD Cash':cdncash}

#create dictionary for benchmark data and risk-free return proxy
bench={'sp500':'^GSPC'}
tbill={'13wk':'^IRX'}

#create list of weights of each security in the porfolios
tfsa_weights=[0.028,0.0095,0.005,0.0175,0.0103,0.0021,0.0088,0.013,0.0026,0.0038,0.015,
         0.0211,0.0951,0.2199,0.0105,0.0144,0.0035,0.0529,0.0058,0.0083,
         0.0043,0.0329,0.0549,0.0244,0.0776]
rrsp_weights=[0.024,0.2851,0.0534,0.0625,0.3176]
us_weights=[0.0339,0.0436,0.7126,0.1071]
cdn_weights=[0.1563,0.2062,0.4529]
port_weights=[tfsa_weights,rrsp_weights,us_weights,cdn_weights]

def intersection(list1,list2):
    common = [value for value in list1 if value  in list2]
    return common

#write function that calls yfinance and populates dictionary
#with security name and historical closing prices for that asset
def get_prices(names):
    dict={}
    for i in range(0,len(names)):
        dict.update({list(names.keys())[i]:
        yf.Ticker(str(list(names.values())[i])).history(start='2018-06-01',
        end='2020-05-30')['Close']})
    #create pandas dataframe with info from yfinance
    prices = pd.DataFrame(dict)
    return prices

def port_stats(names,weights,bench,riskfree):
    global prices,benchmark,rf,returns,port_returns,benchmark_returns
    global cumul_returns,cumul_bench_returns
    prices=get_prices(names)
    benchmark=get_prices(bench)
    rf=get_prices(riskfree)

    #calculate returns for each security in the portfolio & benchmark
    returns=prices.pct_change(fill_method='ffill').dropna()
    benchmark_returns=benchmark.pct_change(fill_method='ffill').dropna()
    
    #calculate portfolio return and cumulative portfolio return
    port_returns=(returns*weights).sum(axis=1)
    cumul_returns=(1+port_returns).cumprod()
    cumul_bench_returns=(1+benchmark_returns).cumprod()
    
    common_dates = intersection(port_returns.index,benchmark_returns.index)
    port_returns=port_returns.loc[common_dates]
    benchmark_returns=benchmark_returns.loc[common_dates]

    #perform a more detailed linear regression to find alpha, beta
    lm = LinearRegression()
    x = benchmark_returns
    y = port_returns
    lm.fit(x,y)
    print('Portfolio beta: ',round(float(lm.coef_),5))
    print('\n Portfolio alpha:',"{:.8f}".format(float(lm.intercept_)))

    #calculate effective annual yield of portfolio, compare to benchmark
    hpy = (prices.iloc[-1,:].sum() - prices.iloc[0,:].sum()) / prices.iloc[0,:].sum()
    eay = ((1 + hpy) ** (365 / port_returns.shape[0])) - 1

    bench_hpy = (benchmark['sp500'][-1] - benchmark['sp500'][0]) / benchmark['sp500'][0]
    bench_eay = ((1 + bench_hpy) ** (365 / benchmark_returns.shape[0])) - 1

    print('\nHolding period return: ',round(hpy*100,2),'%')
    print('Effective annual yield: ',round(eay*100,2),'%')
    print('Benchmark holding period return: ',round(bench_hpy*100,2),'%')
    print('Benchmark effective annual yield: ',round(bench_eay*100,2),'%')

    #calculate portfolio Sharpe ratio
    rf_rate = rf['13wk'][-1]/100
    sharpe = (eay - rf_rate) / port_returns.std()
    print('Portfolio Sharpe ratio: ',round(sharpe,2))
    return 

port_stats(tfsa,tfsa_weights,bench,tbill)

#write a function to visualize return data
def plot_returns(cumul_returns,cumul_bench_returns):
    #visualize cumulative returns over time
    ax0 = cumul_returns.plot()
    ax1 = cumul_bench_returns.plot(alpha = 0.5, ax = ax0)
    ax0.set_xlabel('Date')
    ax0.set_ylabel('Returns')
    ax0.legend(['portfolio','s&p500'],loc = 'upper left')
    plt.show()
    
    #generate linear regression plot of portfolio vs benchmark
    ax_reg = sns.regplot(benchmark_returns, port_returns)
    plt.xlabel("Benchmark Returns")
    plt.ylabel("Portfolio Returns")
    plt.title("Portfolio Returns vs Benchmark Returns")
    plt.show()
    return

plot_returns(cumul_returns,cumul_bench_returns) 
