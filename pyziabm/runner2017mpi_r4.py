import random
import numpy as np
import pandas as pd

from pyziabm.orderbook3 import Orderbook
from pyziabm.trader2017_r3 import Provider, Provider5, Taker, MarketMaker, MarketMaker5, PennyJumper, InformedTrader


class Runner(object):
    def __init__(self, prime1=20, num_mms=1, mm_maxq=1, mm_quotes=12, mm_quote_range=60, mm_delta=0.025, 
                 num_takers=50, taker_maxq=1, num_providers=38, provider_maxq=1, q_provide=0.5,
                 informed_maxq=1, informed_runlength=1, informed_mu=10,
                 alpha=0.0375, mu=0.001, delta=0.025, lambda0=100, wn=0.001, c_lambda=1.0, run_steps=100,
                 mpi=5, h5filename='test.h5', pj=False, alpha_pj=0):
        self.alpha_pj = alpha_pj
        print(self.alpha_pj)
        self.q_provide = q_provide
        self.lambda0 = lambda0
        self.run_steps = run_steps+1
        self.h5filename = h5filename
        self.t_delta_t, self.taker_array = self.make_taker_array(taker_maxq, num_takers, mu)
        self.t_delta_i, self.informed_trader = self.make_informed_trader(informed_maxq, informed_runlength, informed_mu)
        self.t_delta_p, self.provider_array = self.make_provider_array(provider_maxq, num_providers, delta, mpi, alpha)
        self.t_delta_m, self.marketmaker_array = self.make_marketmaker_array(mm_maxq, num_mms, mm_quotes, mm_quote_range, mm_delta, mpi)
        self.pennyjumper = self.make_pennyjumper(mpi)
        self.exchange = Orderbook()
        self.q_take, self.lambda_t = self.make_q_take(wn, c_lambda)
        self.trader_dict = self.make_traders(num_takers, num_providers, num_mms)
        self.seed_orderbook()
        self.make_setup(prime1)
        if pj:
            self.run_mcsPJ(prime1)
        else:
            self.run_mcs(prime1)
        self.exchange.trade_book_to_h5(h5filename)
        self.out_to_h5()
        
    def seed_orderbook(self):
        seed_provider = Provider('p999999', 1, 5, 0.05)
        self.trader_dict.update({'p999999': seed_provider})
        ba = random.choice(range(1000005, 1002001, 5))
        bb = random.choice(range(997995, 999996, 5))
        qask = {'order_id': 'p999999_a', 'timestamp': 0, 'type': 'add', 'quantity': 1, 'side': 'sell',
              'price': ba, 'exid': 99999999}
        qbid = {'order_id': 'p999999_b', 'timestamp': 0, 'type': 'add', 'quantity': 1, 'side': 'buy',
              'price': bb, 'exid': 99999999}
        seed_provider.local_book['p999999_a'] = qask
        self.exchange.add_order_to_book(qask)
        self.exchange.order_history.append(qask)
        seed_provider.local_book['p999999_b'] = qbid
        self.exchange.add_order_to_book(qbid)
        self.exchange.order_history.append(qbid)
    
    def make_taker_array(self, maxq, num_takers, mu):
        default_arr = np.array([1, 5, 10, 25, 50])
        actual_arr = default_arr[default_arr<=maxq]
        taker_size = np.random.choice(actual_arr, num_takers)
        t_delta_t = np.floor(np.random.exponential(1/mu, num_takers)+1)*taker_size
        takers_list = ['t%i' % i for i in range(num_takers)]
        takers = np.array([Taker(t,i) for t,i in zip(takers_list,taker_size)])
        return t_delta_t, takers
    
    def make_informed_trader(self, maxq, runlength, mu):
        default_arr = np.array([1, 5, 10, 25, 50])
        actual_arr = default_arr[default_arr<=maxq]
        informed_size = np.random.choice(actual_arr)
        t_delta_i = np.random.randint(1, 100000, size=mu)
        if runlength > 1:
            stack = t_delta_i
            for i in range(runlength):
                temp = t_delta_i+i+1
                stack = np.hstack((stack, temp))
            t_delta_i = np.unique(stack)
        sides = ['buy', 'sell']
        informed_side = np.random.choice(sides)
        informed_trader = InformedTrader('i0',informed_size,informed_side)
        print(informed_trader)
        return t_delta_i, informed_trader
    
    def make_provider_array(self, maxq, num_providers, delta, mpi, alpha):
        default_arr = np.array([1, 5, 10, 25, 50])
        actual_arr = default_arr[default_arr<=maxq]
        provider_size = np.random.choice(actual_arr, num_providers)
        t_delta_p = np.floor(np.random.exponential(1/alpha, num_providers)+1)*provider_size
        providers_list = ['p%i' % i for i in range(num_providers)]
        if mpi==1:
            providers = np.array([Provider(p,i,mpi,delta) for p,i in zip(providers_list,provider_size)])
        else:
            providers = np.array([Provider5(p,i,mpi,delta) for p,i in zip(providers_list,provider_size)])
        return t_delta_p, providers
    
    def make_marketmaker_array(self, maxq, num_mms, mm_quotes, mm_quote_range, mm_delta, mpi):
        default_arr = np.array([1, 5, 10, 25, 50])
        actual_arr = default_arr[default_arr<=maxq]
        provider_size = np.random.choice(actual_arr, num_mms)
        t_delta_m = maxq
        marketmakers_list = ['m%i' % i for i in range(num_mms)]
        if mpi==1:
            marketmakers = np.array([MarketMaker(p,i,mpi,mm_delta,mm_quotes,mm_quote_range) for p,i in zip(marketmakers_list,provider_size)])
        else:
            marketmakers = np.array([MarketMaker5(p,i,mpi,mm_delta,mm_quotes,mm_quote_range) for p,i in zip(marketmakers_list,provider_size)])
        return t_delta_m, marketmakers
        
    def make_pennyjumper(self, mpi):
        return PennyJumper('j0', 1, mpi)
    
    def make_traders(self, num_takers, num_providers, num_mms):
        takers_dict = dict(zip(['t%i' % i for i in range(num_takers)], list(self.taker_array)))
        providers_dict = dict(zip(['p%i' % i for i in range(num_providers)], list(self.provider_array)))
        takers_dict.update(providers_dict)
        marketmakers_dict = dict(zip(['m%i' % i for i in range(num_mms)], list(self.marketmaker_array)))
        takers_dict.update(marketmakers_dict)
        takers_dict.update({'i0': self.informed_trader})
        if self.alpha_pj > 0:
            takers_dict.update({'j0': self.pennyjumper})
        return takers_dict
    
    def make_providers(self, step):
        providers = self.provider_array[np.remainder(step, self.t_delta_p)==0]
        np.random.shuffle(providers)
        return providers
    
    def make_both(self, step):
        providers_mask = np.remainder(step, self.t_delta_p)==0
        takers_mask = np.remainder(step, self.t_delta_t)==0
        marketmakers_mask = np.remainder(step, self.t_delta_m)==0
        informed_mask = step in self.t_delta_i
        providers = np.vstack((self.provider_array, providers_mask)).T
        takers = np.vstack((self.taker_array, takers_mask)).T
        marketmakers = np.vstack((self.marketmaker_array, marketmakers_mask)).T
        informed = np.squeeze(np.vstack((self.informed_trader, informed_mask)).T)
        traders = np.vstack((providers, marketmakers, takers[takers_mask], informed[informed_mask]))
        np.random.shuffle(traders)
        return traders
    
    def make_q_take(self, s, c_lambda):
        noise = np.random.rand(2,self.run_steps)
        qt_take = np.empty_like(noise)
        qt_take[:,0] = 0.5
        for i in range(1,self.run_steps):
            qt_take[:,i] = qt_take[:,i-1] + (noise[:,i-1]>qt_take[:,i-1])*s - (noise[:,i-1]<qt_take[:,i-1])*s
        lambda_t = -self.lambda0*(1 + (np.abs(qt_take[1] - 0.5)/np.sqrt(np.mean(np.square(qt_take[0] - 0.5))))*c_lambda)
        return qt_take[1], lambda_t
    
    def qtake_to_h5(self):
        temp_df = pd.DataFrame({'qt_take': self.q_take, 'lambda_t': self.lambda_t})
        temp_df.to_hdf(self.h5filename, 'qtl', append=True, format='table', complevel=5, complib='blosc')
        
    def mm_profitability_to_h5(self):
        for m in self.marketmaker_array:
            temp_df = pd.DataFrame(m.cash_flow_collector)
            temp_df.to_hdf(self.h5filename, 'mmp', append=True, format='table', complevel=5, complib='blosc')
            
    def out_to_h5(self):
        self.qtake_to_h5()
        self.mm_profitability_to_h5()
        
    def make_setup(self, prime1):
        top_of_book = self.exchange.report_top_of_book(0)
        for current_time in range(1, prime1):
            for p in self.make_providers(current_time):
                p.process_signal(current_time, top_of_book, self.q_provide, -self.lambda0)
                self.exchange.process_order(p.quote_collector[-1])
                top_of_book = self.exchange.report_top_of_book(current_time)  
        
    def run_mcs(self, prime1):
        top_of_book = self.exchange.report_top_of_book(prime1)
        for current_time in range(prime1, self.run_steps):
            for row in self.make_both(current_time):
                if row[0].trader_type == 'Provider':
                    if row[1]:
                        row[0].process_signal(current_time, top_of_book, self.q_provide, self.lambda_t[current_time])
                        self.exchange.process_order(row[0].quote_collector[-1])
                        top_of_book = self.exchange.report_top_of_book(current_time)
                    row[0].bulk_cancel(current_time)
                    if row[0].cancel_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in row[0].cancel_collector:
                            self.exchange.process_order(c)
                            if self.exchange.confirm_modify_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                                row[0].confirm_cancel_local(self.exchange.confirm_modify_collector[0])
                        top_of_book = self.exchange.report_top_of_book(current_time)
                elif row[0].trader_type == 'MarketMaker':
                    if row[1]:
                        row[0].process_signal(current_time, top_of_book, self.q_provide)
                        for q in row[0].quote_collector:
                            self.exchange.process_order(q)
                        top_of_book = self.exchange.report_top_of_book(current_time)
                    row[0].bulk_cancel(current_time)
                    if row[0].cancel_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in row[0].cancel_collector:
                            self.exchange.process_order(c)
                            if self.exchange.confirm_modify_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                                row[0].confirm_cancel_local(self.exchange.confirm_modify_collector[0])
                        top_of_book = self.exchange.report_top_of_book(current_time)
                elif row[0].trader_type == 'InformedTrader':
                    row[0].process_signal(current_time)
                    self.exchange.process_order(row[0].quote_collector[-1])
                    if self.exchange.traded: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in self.exchange.confirm_trade_collector:
                            trader = self.trader_dict[c['trader']]
                            trader.confirm_trade_local(c)
                        top_of_book = self.exchange.report_top_of_book(current_time)
                else:
                    row[0].process_signal(current_time, self.q_take[current_time])
                    self.exchange.process_order(row[0].quote_collector[-1])
                    if self.exchange.traded: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in self.exchange.confirm_trade_collector:
                            trader = self.trader_dict[c['trader']]
                            trader.confirm_trade_local(c)
                        top_of_book = self.exchange.report_top_of_book(current_time)
            if not np.remainder(current_time, 2000):
                self.exchange.order_history_to_h5(self.h5filename)
                self.exchange.sip_to_h5(self.h5filename)
                
    def run_mcsPJ(self, prime1):
        top_of_book = self.exchange.report_top_of_book(prime1)
        for current_time in range(prime1, self.run_steps):
            for row in self.make_both(current_time):
                if row[0].trader_type == 'Provider':
                    if row[1]:
                        row[0].process_signal(current_time, top_of_book, self.q_provide, self.lambda_t[current_time])
                        self.exchange.process_order(row[0].quote_collector[-1])
                        top_of_book = self.exchange.report_top_of_book(current_time)
                    row[0].bulk_cancel(current_time)
                    if row[0].cancel_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in row[0].cancel_collector:
                            self.exchange.process_order(c)
                            if self.exchange.confirm_modify_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                                row[0].confirm_cancel_local(self.exchange.confirm_modify_collector[0])
                        top_of_book = self.exchange.report_top_of_book(current_time)
                elif row[0].trader_type == 'MarketMaker':
                    if row[1]:
                        row[0].process_signal(current_time, top_of_book, self.q_provide)
                        for q in row[0].quote_collector:
                            self.exchange.process_order(q)
                        top_of_book = self.exchange.report_top_of_book(current_time)
#                    row[0].bulk_cancel(self.delta*2, current_time, self.q_take[current_time])
                    row[0].bulk_cancel(current_time)
                    if row[0].cancel_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in row[0].cancel_collector:
                            self.exchange.process_order(c)
                            if self.exchange.confirm_modify_collector: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                                row[0].confirm_cancel_local(self.exchange.confirm_modify_collector[0])
                        top_of_book = self.exchange.report_top_of_book(current_time)
                elif row[0].trader_type == 'InformedTrader':
                    row[0].process_signal(current_time)
                    self.exchange.process_order(row[0].quote_collector[-1])
                    if self.exchange.traded: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in self.exchange.confirm_trade_collector:
                            trader = self.trader_dict[c['trader']]
                            trader.confirm_trade_local(c)
                        top_of_book = self.exchange.report_top_of_book(current_time)
                else:
                    row[0].process_signal(current_time, self.q_take[current_time])
                    self.exchange.process_order(row[0].quote_collector[-1])
                    if self.exchange.traded: # <---- Check permission versus forgiveness here and elsewhere - move to methods?
                        for c in self.exchange.confirm_trade_collector:
                            trader = self.trader_dict[c['trader']]
                            trader.confirm_trade_local(c)
                        top_of_book = self.exchange.report_top_of_book(current_time)
                if random.uniform(0,1) < self.alpha_pj:
                    self.pennyjumper.process_signal(current_time, top_of_book, self.q_take[current_time])
                    if self.pennyjumper.cancel_collector:
                        for c in self.pennyjumper.cancel_collector:
                            self.exchange.process_order(c)
                    if self.pennyjumper.quote_collector:
                        for q in self.pennyjumper.quote_collector:
                            self.exchange.process_order(q)
                    top_of_book = self.exchange.report_top_of_book(current_time)
            if not np.remainder(current_time, 2000):
                self.exchange.order_history_to_h5(self.h5filename)
                self.exchange.sip_to_h5(self.h5filename)
    
