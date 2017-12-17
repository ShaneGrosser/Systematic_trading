import quandl
import pandas as pd
from datetime import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
import holidays
from workdays import workday

quandl.ApiConfig.api_key = "cRxiJy9Zb6GBFiKkiWte"

month_code_dict = {'Jan': 'F', 'Feb': 'G', 'Mar': 'H', 'Apr': 'J', 'May': 'K', 'Jun': 'M',
                   'Jul': 'N', 'Aug': 'Q', 'Sep': 'U', 'Oct': 'V', 'Nov': 'X', 'Dec': 'Z'}
d = {'M': {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
           11: 'Nov', 12: 'Dec'},
     'Q': {1: 'Q1', 2: 'Q1', 3: 'Q1', 4: 'Q2', 5: 'Q2', 6: 'Q2', 7: 'Q3', 8: 'Q3', 9: 'Q3', 10: 'Q4', 11: 'Q4',
           12: 'Q4'},
     'S': {1: 'W', 2: 'W', 3: 'W', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'W', 11: 'W', 12: 'W'}}

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
years = ['2013', '2014', '2015', '2016', '2017']

season_dict = {'S': 6, 'Q': 3, 'M': 1}


def Wadj(month, s):
    if month in (1, 2, 3) and s == 'S':
        return -1
    else:
        return 0


def get_data(months, years, seasonality):
    df = pd.DataFrame()
    for m in months:
        for y in years:
            string = "ICE/M" + month_code_dict[m] + y + ".4"
            data = quandl.get(string)
            # data = data.rename(columns = {'Settle': m+"-"+y})
            data['ProductId'] = str(m + y)
            df = pd.concat([df, data], axis=0)
    df['contract_date'] = df['ProductId'].apply(lambda x: datetime.strptime(x, "%b%Y").date())
    df = df.drop('ProductId', axis=1)
    df['weights'] = df['contract_date'].apply(lambda x: (x + relativedelta(day=31)).day)
    df['contract'] = df['contract_date'].apply(
        lambda x: d[seasonality][x.month] + str(x.year + Wadj(x.month, seasonality))[2:])
    df['UTCDate'] = df.index
    contracts = []
    for name, group in df[['contract_date', 'contract']].drop_duplicates().groupby('contract'):
        if group.shape[0] == season_dict[seasonality]:
            contracts.append(name)
    df = pd.DataFrame(
        df.groupby(['UTCDate', 'contract']).apply(lambda x: np.average(x['Settle'], weights=x['weights'])))
    df = df.unstack()
    df = df.loc[:, 0]
    df.reset_index(inplace=True)
    df = df[['UTCDate',contracts]]
    return df


def create_spread(contract1, contract2, seasonality, start_date='2012-01-01'):
    df = get_data(months, years, seasonality)
    df['price'] = df[contract1] - df[contract2]
    df = df[['UTCDate', 'price']]
    df = df.dropna()
    df['contract'] = str(contract1 + "/" + contract2)
    df = df[df['UTCDate'] >= start_date]
    df = df[df['UTCDate'] <= expiry_date]
    return df


def contract_expiry(contract_date):
    UK = sorted(holidays.UK(state=None, years=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]).items())
    holiday_list = []
    for d, n in UK:
        holiday_list.append(d)
    date_exp = workday(contract_date, -2, holiday_list)
    return date_exp