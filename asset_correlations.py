#import required libraries
import yfinance as yf
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

#create dictionary of asset names
names={'sp500':'^GSPC','tsx':'^GSPTSE','intl':'EFA',
       '13wk':'^IRX','5yr':'^FVX','10yr':'^TNX','30yr':'^TYX',
       'tips':'TIP','gold':'GLD','goldcdn':'CGL.TO','reits':'^RMZ','barrick':'ABX.TO'}
notbonds=['sp500','tsx','intl','tips','gold','reits']
bonds=['13wk','5yr','10yr','30yr']

#write function that calls yfinance and populates dictionary
#with asset name and historical closing prices for that asset
def get_prices(names):
    dict={}
    for i in range(0,len(names)):
        dict.update({list(names.keys())[i]:
        yf.Ticker(str(list(names.values())[i])).history(period='max')['Close']})
    #create pandas dataframe with info from yfinance
    prices = pd.DataFrame(dict)
    #replace column names with asset names
    # prices.columns=list(names.keys())
    return prices
prices=get_prices(names)

#figure out which asset has the most NaN values
for i in range(0,len(prices.columns)):
    #count NaN values for each asset, return asset with most NaN's
    count=prices.iloc[:,i].isna().sum()
    if count >= count:
        max_nan=prices.columns[i]
print(max_nan,'has the most NaN values (',round(count/len(prices.iloc[:,i])*100,2),'% NaN)')

#figure out which asset has the shortest/least complete price history
def get_first_dates(stock_prices):
    dict={}
    for i in range(0,len(stock_prices.columns)):
        dict.update({stock_prices.columns[i]:stock_prices.iloc[:,i].first_valid_index()})
    first_dates = pd.DataFrame(dict,index=range(0,1))
    first_dates.rename(index={0:'first_date_listed'})
    return first_dates
first_dates=get_first_dates(prices)

#find asset with the latest (least available) price history
print('The asset with shortest price history is:\n',
      first_dates.max().idxmax(),
      '\nwith the first available price data on\n',
      first_dates.max(axis=1).values)

#drop any NaN values
prices_cleaned = prices.dropna()

returns=prices_cleaned.pct_change(fill_method='ffill').dropna()
cumul_returns=(1 + returns).cumprod()
cumul_returns.plot()

#statistic analysis of data
cumul_returns.describe()
corr=cumul_returns.corr()

cumul_returns[['goldcdn','gold']].plot()
plt.ylabel('Returns')
plt.xlabel('Year')

sns.regplot(cumul_returns['goldcdn'],cumul_returns['gold'])
pearson_coef,p_value=stats.pearsonr(cumul_returns['goldcdn'],cumul_returns['gold'])

test = returns[['sp500','tsx','intl','gold','5yr','30yr','reits']].corr()
sns.heatmap(test,annot = True,cmap = sns.diverging_palette(10,240, n=100), cbar = True)
plt.title('Correlations of Returns for Various Asset Classes')
