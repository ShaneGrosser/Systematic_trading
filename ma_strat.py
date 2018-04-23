import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import create_positions_dictionary


#sv = float(input('Set sell volume in ktherms: '))#sell volume in thousand therms
sv = 100
#bv = float(input('Set buy volume in ktherms: '))#buy volume thousand therms
bv = 100
#max_v = float(input('Set max volume in ktherms: '))
max_v = 200

df['pnl'] = np.zeros((len(df['price']),1))
df['sp'] = np.zeros((len(df['price']),1))
df['bp'] = np.zeros((len(df['price']),1))
df['c_pnl'] = np.zeros((len(df['price']),1))
df['op_pos'] = np.zeros((len(df['price']),1))
df['vw_price'] = np.zeros((len(df['price']),1))

#sd = float(input('Set number of days for MA sell price: '))
sd = 3
#bd = float(input('Set number of days for MA buy price: '))
bd = 3
#so = float(input('Set sell price offset: '))
so = 0.1
#bo = float(input('Set buy price offset: '))
bo = 0.1
for index, row in df.iterrows():
    if index == 0:
        df.loc[index,'sp'] = 999
        df.loc[index,'bp'] = -999
    else:
        df.loc[index,'sp'] = df.loc[index-sd:index-1,'price'].mean() + so
        df.loc[index,'bp'] = df.loc[index-bd:index-1,'price'].mean() - bo

quick_graph = df.set_index('UTCDate')
quick_graph.plot(title= df['contract'].iloc[0], figsize = (10,7), ylim = (df['price'].min()-1, df['price'].max()+1))
plt.show()

positions = create_positions_dictionary(df)



"""Create Pnl time series"""
df_pnl = pd.DataFrame(df.groupby('UTCDate').sum())
df_pnl = df_pnl.drop(['price','c_pnl','sp','bp','op_pos','vw_price'],axis = 1)
df_pnl.index = pd.to_datetime(df_pnl.index)

fig = plt.figure(figsize=(10, 7), dpi=200)
plt.subplot(2,1,1)
plt.plot(df_pnl, color = 'red')
plt.xlabel('date')
plt.ylabel('£')
plt.title('Strategy Pnl')
plt.xticks(fontsize = 8,rotation=60)

plt.show()

df.to_excel('P:/Coding/Strategies/NBP/dontclose.xlsx')
