import pandas as pd
import numpy as np
import os
from datetime import date
from pandas_datareader.stooq import StooqDailyReader
from pandas.tseries.offsets import BDay

# List of stock symbols for the NASDAQ 100
tickers = ['ATVI', 'ADBE', 'AMD', 'ALXN', 'ALGN', 'GOOG', 'GOOGL', 'AMZN'
    ,'AMGN', 'ADI', 'ANSS', 'AAPL', 'AMAT', 'ASML', 'ADSK', 'ADP'
    ,'BIDU', 'BIIB', 'BMRN', 'BKNG', 'AVGO', 'CDNS', 'CDW', 'CERN'
    ,'CHTR', 'CHKP', 'CTAS', 'CSCO', 'CTXS', 'CTSH', 'CMCSA', 'CPRT'
    ,'CSGP', 'COST', 'CSX', 'DXCM', 'DLTR', 'EBAY', 'EA', 'EXC', 'EXPE'
    ,'FB', 'FAST', 'FISV', 'FOX', 'FOXA', 'GILD', 'IDXX', 'ILMN', 'INCY'
    ,'INTC', 'INTU', 'ISRG', 'JD', 'KLAC', 'LRCX', 'LBTYA', 'LBTYK'
    ,'LULU', 'MAR', 'MXIM', 'MELI', 'MCHP', 'MU', 'MSFT', 'MDLZ', 'MNST'
    ,'NTAP', 'NTES', 'NFLX', 'NVDA', 'NXPI', 'ORLY', 'PCAR', 'PAYX'
    ,'PYPL', 'PEP', 'QCOM', 'REGN', 'ROST', 'SGEN', 'SIRI', 'SWKS'
    ,'SPLK', 'SBUX', 'SNPS', 'TMUS', 'TTWO', 'TSLA', 'TXN', 'KHC'
    ,'TCOM', 'ULTA', 'UAL', 'VRSN', 'VRSK', 'VRTX', 'WBA', 'WDC'
    ,'WLTW', 'WDAY', 'XEL', 'XLNX'
]

# if there is no csv of historical data generate it using the stooq API
if os.path.isfile('nasdaq_100.csv'):
    
    # read in the historical stock data from the csv
    s = pd.read_csv('nasdaq_100.csv',parse_dates = True
                    ,header = [0,1],index_col = 0)
    
    # check to make sure it is up-to-date
    # determine the most recent business day (this may not work on holidays)
    last_bday = np.where((date.today() - BDay(0)) > date.today()-BDay(0)
                            ,date.today() - BDay(1),date.today())
    
    # if the last date in the data isn't the last business day, update it
    if s.index.max() < last_bday:
        
        # bring in the data since the last day in the csv and add to s
        u = StooqDailyReader(tickers,s.index.max()+BDay(1),date.today()).read()
        s = u.append(s)

else:
    
    # Read historical stock data from stooq api for all of NASDAQ 100
    s = StooqDailyReader(tickers).read()
    
# write the stock data to a csv to save time in the future
s.to_csv('nasdaq_100.csv')