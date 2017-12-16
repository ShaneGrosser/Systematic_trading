import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import cluster

df = pd.read_excel('P:/Coding/Technical/S18_hist.xlsx')
df = df.set_index('Date (GMT)')

price_data = df.as_matrix(columns = ['Last'])

ms = cluster.MeanShift()
ms.fit(price_data)
centers = ms.cluster_centers_
labels = ms.labels_

df2 = df
df2['line0'] = centers[0][0]
df2['line1'] = centers[1][0]



plt.plot(df2.index,price_data)
plt.plot(df2.index,df2['line0'])
plt.plot(df2.index,df2['line1'])
plt.ylabel('ppth')
plt.title('W17 with automatically generated support and resistance')
plt.show()