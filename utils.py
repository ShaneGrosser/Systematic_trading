# Really only the 'generate buy and sell price' part is related to moving averages. Should have Strategy class, then the Moving average strategy class inherits from this
# Should have class depending on market, and the price/volume relationship

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import brute
import os


def ma_strat_func(x, vol, max_v, df, measure):
    x1, x2 = x
    strat = Strategy(x1, x2, vol, max_v, df)
    strat.run_strategy()
    dict = {'final_pnl': -strat.final_pnl, 'sharpe': -strat.sharpe, 'max_drawdown': strat.max_drawdown,
            'merc1': -strat.merc1, }
    obj = dict[measure]
    return (obj)


def optimise_ma_strat(ma_slice, offset_slice, vol, max_v, df, measure):
    res = brute(ma_strat_func, (ma_slice, offset_slice), args=(vol, max_v, df, measure), disp=True, finish=None,
                full_output=True)
    matrix = pd.DataFrame(res[3])
    matrix.columns = res[2][1][0]
    matrix.index = res[2][0][:, 0]
    matrix.to_excel('%s/matrices/%s.xlsx' % (os.getcwd(), measure))
    return res, matrix


class Strategy:
    def __init__(self, ma, offset, vol, max_v, df):
        self.ma = ma
        self.offset = offset
        self.vol = vol
        self.max_v = max_v
        self.positions = {}
        self.df = df
        self.df['pnl'] = np.zeros((len(self.df['price']), 1))
        self.df['sp'] = np.zeros((len(self.df['price']), 1))
        self.df['bp'] = np.zeros((len(self.df['price']), 1))
        self.df['c_pnl'] = np.zeros((len(self.df['price']), 1))
        self.df['op_pos'] = np.zeros((len(self.df['price']), 1))
        self.df['vw_price'] = np.zeros((len(self.df['price']), 1))
        self.df['trade'] = np.zeros((len(self.df['price']), 1))
        for index, row in self.df.iterrows():
            if index == 0:
                self.df.loc[index, 'sp'] = 999
                self.df.loc[index, 'bp'] = -999
            else:
                self.df.loc[index, 'sp'] = self.df.loc[index - self.ma:index - 1, 'price'].mean() + self.offset
                self.df.loc[index, 'bp'] = self.df.loc[index - self.ma:index - 1, 'price'].mean() - self.offset
        for contract in self.df['contract'].unique():
            self.positions[contract] = [0, 0, 0]  # dictionary has [open position, vol-weighted open price, closed pnl]

    def run_strategy(self):
        for index, row in self.df.iterrows():
            op_pos = self.positions[row['contract']][0]
            vw_price = self.positions[row['contract']][1]
            c_pnl = self.positions[row['contract']][2]

            if row['price'] >= row['sp']:  # if above our limit
                if op_pos <= 0 and abs(
                        op_pos - self.vol) <= self.max_v:  # and trade will open position which will not push us over max pos
                    vw_price = ((op_pos * vw_price) - (row['price']) * self.vol) / (-self.vol + op_pos)
                    op_pos = op_pos - self.vol  # update position and price
                    self.df.loc[index, 'trade'] = 1
                elif op_pos > 0:  # if trade will close position
                    c_pnl = c_pnl + (row['price'] - vw_price) * self.vol
                    op_pos = op_pos - self.vol
                    self.df.loc[index, 'trade'] = 1

            elif row['price'] <= row['bp']:  # if below our limit
                if op_pos >= 0 and abs(
                        op_pos + self.vol) <= self.max_v:  # and trade will open position which will not push us over max pos
                    vw_price = ((op_pos * vw_price) + (row['price']) * self.vol) / (
                            self.vol + op_pos)  # update position and price
                    op_pos = op_pos + self.vol
                    self.df.loc[index, 'trade'] = 1
                elif op_pos < 0:  # if trade will close position
                    c_pnl = c_pnl + (vw_price - row['price']) * self.vol
                    op_pos = op_pos + self.vol
                    self.df.loc[index, 'trade'] = 1

            self.df.loc[index, 'pnl'] = c_pnl + op_pos * (row['price'] - vw_price)
            self.df.loc[index, 'c_pnl'] = c_pnl
            self.df.loc[index, 'op_pos'] = op_pos
            self.df.loc[index, 'vw_price'] = vw_price

            self.positions[row['contract']][0] = op_pos
            self.positions[row['contract']][1] = vw_price
            self.positions[row['contract']][2] = c_pnl

        # Strategy performance measures
        self.req_cap = self.max_v * abs(self.df['price'].mean())
        self.df['daily_pnl'] = self.df['pnl'] - self.df['pnl'].shift(1).fillna(0)
        self.df['excess_return'] = self.df['daily_pnl'] / self.req_cap - (0.03 / 365)
        self.max_drawdown = -min(self.df['daily_pnl'])
        self.final_pnl = self.df['pnl'].iloc[-1]
        self.sharpe = self.df['excess_return'].mean() / self.df['excess_return'].std()
        self.annual_ror = self.final_pnl / self.req_cap * (365 / self.df.shape[0])
        self.merc1 = self.annual_ror / (self.max_drawdown / self.req_cap)
        self.profit_factor = (self.df['daily_pnl'][self.df['daily_pnl'] > 0].sum()) / (
        -self.df['daily_pnl'][self.df['daily_pnl'] < 0].sum())
        self.trades = self.df['trade'].sum()
        self.merc2 = ((self.profit_factor - 1) * self.sharpe) * self.trades

    def calc_todays_actions(self):
        self.bp_today = self.df['price'].iloc[-1 - int(self.ma):-1].mean() - self.offset
        self.sp_today = self.df['price'].iloc[-1 - int(self.ma):-1].mean() + self.offset
        self.position_today = list(self.positions.values())[0][0]
        self.vwap_today = list(self.positions.values())[0][1]
        return self.bp_today, self.sp_today, self.position_today, self.vwap_today

    def graph(self):
        df_graph = self.df.set_index('UTCDate')
        df_graph = df_graph.loc[:, ['price', 'sp', 'bp']]
        df_graph.plot(title=self.df['contract'].iloc[0], figsize=(10, 7),
                      ylim=(self.df['price'].min() - 1, self.df['price'].max() + 1))
        plt.show()
        df_pnl = pd.DataFrame(self.df.groupby('UTCDate').sum())
        df_pnl = df_pnl.drop(['price', 'c_pnl', 'sp', 'bp', 'op_pos', 'vw_price', 'daily_pnl', 'excess_return'], axis=1)
        df_pnl.index = pd.to_datetime(df_pnl.index)
        fig = plt.figure(figsize=(10, 7), dpi=200)
        plt.subplot(2, 1, 1)
        plt.plot(df_pnl, color='red')
        plt.xlabel('date')
        plt.ylabel('price unit')
        plt.title('%s-day m-avg strat with %s offset - Pnl' % (self.ma, self.offset))
        plt.xticks(fontsize=8, rotation=60)
        plt.show()
        fig2 = plt.figure(figsize=(10, 7), dpi=200)
        plt.subplot(2, 1, 2)
        sns.distplot(self.df['daily_pnl'])
        plt.xlabel('pence pnl')
        plt.ylabel('probability')
        plt.title('%s-day m-avg strat with %s offset - Pnl distribution' % (self.ma, self.offset))
        plt.xticks(fontsize=8, rotation=60)
        plt.show()            