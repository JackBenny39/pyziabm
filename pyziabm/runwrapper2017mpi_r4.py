import random
import time
import numpy as np
import pandas as pd

from pyziabm.runner2017mpi_r4 import Runner

def participation_to_list(h5in, outlist):
    trade_df = pd.read_hdf(h5in, 'trades')
    trade_df = trade_df.assign(trader_id = trade_df.resting_order_id.str.split('_').str[0])
    lt_df = pd.DataFrame(trade_df.groupby(['trader_id']).quantity.count())
    lt_df.rename(columns={'quantity': 'trade'}, inplace=True)
    if 'p999999' in lt_df.index:
        lt_df.drop('p999999', inplace=True)
    ltsum_df = pd.DataFrame(trade_df.groupby(['trader_id']).quantity.sum())
    ltsum_df.rename(columns={'quantity': 'trade_vol'}, inplace=True)
    ltsum_df = ltsum_df.assign(Participation = 100*ltsum_df.trade_vol/ltsum_df.trade_vol.sum())
    providers = ltsum_df.index.unique()
    market_makers = [x for x in providers if x.startswith('m')]
    market_makers.append('j0')
    ltsum_df = ltsum_df.ix[market_makers]
    part_dict = {'MCRun': j, 'MM_Participation': ltsum_df.loc['m0', 'Participation']}
    if 'j0' in providers:
        part_dict.update({'PJ_Participation': ltsum_df.loc['j0', 'Participation']})
    outlist.append(part_dict)
    
def position_to_list(h5in, outlist):
    mmcf_df = pd.read_hdf(h5in, 'mmp')
    market_makers = mmcf_df.mmid.unique()
    for mm in market_makers:
        pos_dict = {}
        pos_dict['MCRun'] = j
        pos_dict['MarketMaker'] = mm
        pos_dict['Min'] =  mmcf_df[mmcf_df.mmid == mm].position.min()
        pos_dict['Max'] =  mmcf_df[mmcf_df.mmid == mm].position.max()
        outlist.append(pos_dict)
        
def profit_to_list(h5in, outlist):
    trade_df = pd.read_hdf(h5in, 'trades')
    trade_df = trade_df.assign(trader_id = trade_df.resting_order_id.str.split('_').str[0])
    buy_trades = trade_df[trade_df.side=='buy']
    buy_trades = buy_trades.assign(BuyCashFlow = buy_trades.price*buy_trades.quantity)
    buy_trades = buy_trades.assign(BuyVol = buy_trades.groupby('trader_id').quantity.cumsum(),
                                   CumulBuyCF = buy_trades.groupby('trader_id').BuyCashFlow.cumsum()
                                  )
    buy_trades.rename(columns={'timestamp': 'buytimestamp'}, inplace=True)
    sell_trades = trade_df[trade_df.side=='sell']
    sell_trades = sell_trades.assign(SellCashFlow = -sell_trades.price*sell_trades.quantity)
    sell_trades = sell_trades.assign(SellVol = sell_trades.groupby('trader_id').quantity.cumsum(),
                                     CumulSellCF = sell_trades.groupby('trader_id').SellCashFlow.cumsum()
                                    )
    sell_trades.rename(columns={'timestamp': 'selltimestamp'}, inplace=True)
    buy_trades = buy_trades[['trader_id', 'BuyVol', 'CumulBuyCF', 'buytimestamp']]
    sell_trades = sell_trades[['trader_id', 'SellVol', 'CumulSellCF', 'selltimestamp']]
    cash_flow = pd.merge(buy_trades, sell_trades, left_on=['trader_id', 'BuyVol'], right_on=['trader_id', 'SellVol'])
    cash_flow = cash_flow.assign(NetCashFlow = cash_flow.CumulBuyCF + cash_flow.CumulSellCF)
    temp_df = cash_flow.groupby('trader_id')['NetCashFlow', 'BuyVol'].last()
    temp_df = temp_df.assign(NetCFPerShare = temp_df.NetCashFlow/temp_df.BuyVol)
    temp_df = temp_df[['NetCashFlow', 'NetCFPerShare']]
    outlist.append(temp_df)
        
def spread_to_list(h5in, outlist):
    indf = pd.read_hdf(h5in, 'tob')
    indf = indf.assign(spread = indf.best_ask - indf.best_bid)
    last_df = indf.groupby('timestamp').last()
    last_df = last_df.loc[50:]
    spread_dict = {'MCRun': j, 'Min': last_df.spread.min(), 'Max': last_df.spread.max(), 'Median': last_df.spread.median(),
                   'Mean': last_df.spread.mean()}
    outlist.append(spread_dict)
    
def tradesrets_to_list(h5in, outlist):
    indf = pd.read_hdf(h5in, 'trades')
    trades = indf.price.count()
    minprice = indf.price.min()
    maxprice = indf.price.max()
    
    indf = indf.assign(ret = 100*indf.price.pct_change())
    indf = indf.assign(abs_ret = np.abs(indf.ret))
    lags = []
    autocorr = []
    abs_autocorr = []
    for i in range(1,51):
        ac = indf.ret.autocorr(lag = i)
        aac = indf.abs_ret.autocorr(lag = i)
        lags.append(i)
        autocorr.append(ac)
        abs_autocorr.append(aac)
    ar_df = pd.DataFrame({'lag': lags, 'autocorrelation': autocorr, 'autocorrelation_abs': abs_autocorr})
    ar_df.set_index('lag', inplace=True)
    clustering_constant = np.abs(ar_df.autocorrelation_abs.sum()/ar_df.autocorrelation.sum())
    
    returns_dict = {'Trades': trades, 'MinPrice': minprice, 'MaxPrice': maxprice, 'ClusteringConstant': clustering_constant,
                    'MeanRet': indf.ret.mean(), 'StdRet': indf.ret.std(), 'SkewRet': indf.ret.skew(),
                    'KurtosisRet': indf.ret.kurtosis(), 'MCRun': j}
    outlist.append(returns_dict)
    
def canceltrade_to_list(h5in, outlist1, outlist2):
    order_df = pd.read_hdf(h5in, 'orders')
    order_df = order_df.assign(trader_id = order_df.order_id.str.split('_').str[0])
    lpsum_df = order_df.groupby(['trader_id','type']).quantity.sum().unstack(level=-1)
    lpsum_df.rename(columns={'add': 'add_vol', 'cancel': 'cancel_vol'}, inplace=True)
    
    trade_df = pd.read_hdf(h5in, 'trades')
    trade_df = trade_df.assign(trader_id = trade_df.resting_order_id.str.split('_').str[0])
    ltsum_df = pd.DataFrame(trade_df.groupby(['trader_id']).quantity.sum())
    ltsum_df.rename(columns={'quantity': 'trade_vol'}, inplace=True)
    
    both_sum = pd.merge(lpsum_df, ltsum_df, how='right', left_index=True, right_index=True)
    both_sum = both_sum.assign(trade_order_vol_pct = 100*both_sum['trade_vol']/both_sum['add_vol'],
                               cancel_order_vol_pct = 100*both_sum['cancel_vol']/both_sum['add_vol'],
                               cancel_trade_vol = both_sum['cancel_vol']/both_sum['trade_vol']
                              )
    total_dict = {}
    total_dict['total_trade_to_order_vol'] = 100*both_sum.trade_vol.sum()/both_sum.add_vol.sum()
    total_dict['total_cancel_to_trade_vol'] = both_sum.cancel_vol.sum()/both_sum.trade_vol.sum()
    total_dict['MCRun'] = j
    outlist1.append(total_dict)
    
    traders = both_sum.index.unique()
    market_makers = [x for x in traders if (x.startswith('m') or x.startswith('j'))]
    for mm in market_makers:
        cto_dict = {}
        temp = both_sum.loc[mm, :]
        cto_dict['MCRun'] = j
        cto_dict['MarketMaker'] = mm
        cto_dict['CancelToTrade'] = temp['cancel_vol']/temp['trade_vol']
        cto_dict['TradeToOrderPct'] =  100*temp['trade_vol']/temp['add_vol']
        outlist2.append(cto_dict)
        
def lists_to_h5(participation_list, position_list, profit_list, spread_list, canceltrade_list, by_mm_list, returns_list, h5out):
    participation_df = pd.DataFrame(participation_list)
    participation_df.set_index('MCRun', inplace=True)
    participation_df.to_hdf(h5out, 'participation', append=True, format='table', complevel=5, complib='blosc')
    
    position_df = pd.DataFrame(position_list)
    position_df.to_hdf(h5out, 'position', append=True, format='table', complevel=5, complib='blosc')
    
    profit_df = pd.concat(profit_list)
    profit_df.to_hdf(h5out, 'profit', append=True, format='table', complevel=5, complib='blosc')
    
    spread_df = pd.DataFrame(spread_list)
    spread_df.set_index('MCRun', inplace=True)
    spread_df.to_hdf(h5out, 'spread', append=True, format='table', complevel=5, complib='blosc')
    
    returns_df = pd.DataFrame(returns_list)
    returns_df.set_index('MCRun', inplace=True)
    returns_df.to_hdf(h5out, 'returns', append=True, format='table', complevel=5, complib='blosc')
    
    cancel_trade_df = pd.DataFrame(canceltrade_list)
    cancel_trade_df.to_hdf(h5out, 'cancel_trade', append=True, format='table', complevel=5, complib='blosc')

    by_mm_df = pd.DataFrame(by_mm_list)
    by_mm_df.to_hdf(h5out, 'by_mm', append=True, format='table', complevel=5, complib='blosc')
        
        
participation_collector = []
position_collector = []
profit_collector = []
spread_collector = []
canceltrade_collector = []
by_mm_collector = []
returns_collector = []

# User inputs
#num_mms=1
#mm_maxq=1
#mm_quotes=12
#mm_quote_range=60
#mm_delta=0.05
#num_takers=100
#taker_maxq=1
#num_providers=38
#provider_maxq=1
#q_provide=0.5
#alpha=0.0375
#mu=0.001
#delta=0.025
#lambda0=100
#wn=0.001
c_lambda=5.0
#run_steps=100000
mpi=1
#h5filename='test.h5'  
alpha_pj = 0.001
pj = False
trial_no = 1002
end = 11

h5_out = 'C:\\Users\\user\\Documents\\Agent-Based Models\\h5 files\\Trial %d\\ABMSmallCapSum.h5' % trial_no
       
start = time.time()
print(start)       
for j in range(1,end):
    random.seed(j)
    np.random.seed(j)
    h5_file = 'C:\\Users\\user\\Documents\\Agent-Based Models\\h5 files\\Trial %d\\smallcap_%d.h5' % (trial_no, j)
    if pj:
        market1 = Runner(alpha_pj=alpha_pj, h5filename=h5_file)
    else:
        market1 = Runner(c_lambda=c_lambda, mpi=mpi, h5filename=h5_file)
    
    participation_to_list(market1.h5filename, participation_collector)
    position_to_list(market1.h5filename, position_collector)
    profit_to_list(market1.h5filename, profit_collector)
    spread_to_list(market1.h5filename, spread_collector)
    canceltrade_to_list(market1.h5filename, canceltrade_collector, by_mm_collector)
    tradesrets_to_list(market1.h5filename, returns_collector)
#    os.remove(market1.h5filename)
    
    print('Run %d:  %.2f minutes' % (j, (time.time() - start)/60))
    start = time.time()

lists_to_h5(participation_collector, position_collector, profit_collector, spread_collector, canceltrade_collector, by_mm_collector, returns_collector, h5_out)
