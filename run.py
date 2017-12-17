import pandas as pd
from utils import Strategy, optimise_ma_strat
from utils_email import send_email
from utils_data import get_data, create_spread

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
years = ['2015','2016']

df = get_data(months,years,'S')

#df = create_spread('S15','W15','S')

#final_pnl,sharpe,max_drawdown

#opt, matrix = optimise_ma_strat(slice(2,21,1),slice(0.1,0.5,0.05),100000,200000,df,'final_pnl')
#opt_strat = Strategy(opt[0][0],opt[0][1],100000,200000,df)
#opt_strat.run_strategy()
#opt_strat.graph()


#strat = Strategy(4,0.2,100000,200000,df)
#strat.run_strategy()
#strat.graph()

#bp,sp,pos,vwap = opt_strat.calc_todays_actions()

#send_email('nbpttf_reversion',bp,sp,pos,vwap)
