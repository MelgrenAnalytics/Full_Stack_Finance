import pandas as pd
import os
import sys
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

# read in the historical stock data from the csv
if not os.path.isfile('nasdaq_100.csv'):
    sys.exit('The file "nasdaq_100.csv" is not found in the "' + os.getcwd() +
             '" directory. Please run "get_data.py" then retry.')

# read in the data
s = pd.read_csv('nasdaq_100.csv',parse_dates = True
                ,header = [0,1],index_col = 0)

# create a new data frame of daily % change of each stock
c = (s['Close']-s['Open'])/s['Open']

# scale and transpose the daily % change data for clustering
cd = c.dropna(axis=0).transpose() # need stocks to be rows
scaled = scale(cd) # scale to account for some stocks being more volatile

# arrange the stocks into 5 clusters
km = KMeans(n_clusters = 5,random_state = 34)
km.fit(scaled)
cd['cluster'] = km.predict(scaled)

# save the cluster predictions to a .csv
cd['cluster'].to_csv('clusters.csv')