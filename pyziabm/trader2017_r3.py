import random
import numpy as np


class ZITrader(object):
    '''
    ZITrader generates quotes (dicts) based on mechanical probabilities.
    
    A general base class for specific trader types.
    Public attributes: quote_collector
    Public methods: none
    '''

    def __init__(self, name, maxq):
        '''
        Initialize ZITrader with some base class attributes and a method
        
        quote_collector is a public container for carrying quotes to the exchange
        '''
        self._trader_id = name # trader id
        self._max_quantity = maxq
        self.quote_collector = []
        self._quote_sequence = 0
        
    def __repr__(self):
        return 'Trader({0}, {1})'.format(self._trader_id, self._max_quantity)
        
    def _make_add_quote(self, time, quantity, side, price):
        '''Make one add quote (dict)'''
        self._quote_sequence += 1
        order_id = '%s_%d' % (self._trader_id, self._quote_sequence)
        return {'order_id': order_id, 'timestamp': time, 'type': 'add', 'quantity': quantity, 
                'side': side, 'price': price}
        

class PennyJumper(ZITrader):
    '''
    PennyJumper jumps in front of best quotes when possible
    
    Subclass of ZITrader
    Public attributes: trader_type, quote_collector (from ZITrader), cancel_collector
    Public methods: confirm_trade_local (from ZITrader)
    '''
    
    def __init__(self, name, maxq, mpi):
        '''
        Initialize PennyJumper
        
        cancel_collector is a public container for carrying cancel messages to the exchange
        PennyJumper tracks private _ask_quote and _bid_quote to determine whether it is alone
        at the inside or not.
        '''
        ZITrader.__init__(self, name, maxq)
        self.trader_type = 'PennyJumper'
        self._mpi = mpi
        self.cancel_collector = []
        self._ask_quote = None
        self._bid_quote = None
        
    def __repr__(self):
        return 'Trader({0}, {1}, {2}, {3})'.format(self._trader_id, self._max_quantity, self._mpi, self.trader_type)
    
    def _make_cancel_quote(self, q, time):
        return {'type': 'cancel', 'timestamp': time, 'order_id': q['order_id'], 'quantity': q['quantity'],
                'side': q['side'], 'price': q['price']}

    def confirm_trade_local(self, confirm):
        '''PJ has at most one bid and one ask outstanding - if it executes, set price None'''
        if confirm['side'] == 'buy':
            self._bid_quote = None
        else:
            self._ask_quote = None
            
    def process_signal(self, time, qsignal, q_taker):
        '''PJ determines if it is alone at the inside, cancels if not and replaces if there is an available price 
        point inside the current quotes.
        '''
        self.quote_collector.clear()
        self.cancel_collector.clear()
        if qsignal['best_ask'] - qsignal['best_bid'] > self._mpi:
            # q_taker > 0.5 implies greater probability of a buy order; PJ jumps the bid
            if random.uniform(0,1) < q_taker:
                if self._bid_quote: # check if not alone at the bid
                    if self._bid_quote['price'] < qsignal['best_bid'] or self._bid_quote['quantity'] < qsignal['bid_size']:
                        self.cancel_collector.append(self._make_cancel_quote(self._bid_quote, time))
                        self._bid_quote = None
                if not self._bid_quote:
                    price = qsignal['best_bid'] + self._mpi
                    side = 'buy'
                    q = self._make_add_quote(time, self._max_quantity, side, price)
                    self.quote_collector.append(q)
                    self._bid_quote = q
            else:
                if self._ask_quote: # check if not alone at the ask
                    if self._ask_quote['price'] > qsignal['best_ask'] or self._ask_quote['quantity'] < qsignal['ask_size']:
                        self.cancel_collector.append(self._make_cancel_quote(self._ask_quote, time))
                        self._ask_quote = None
                if not self._ask_quote:
                    price = qsignal['best_ask'] - self._mpi
                    side = 'sell'
                    q = self._make_add_quote(time, self._max_quantity, side, price)
                    self.quote_collector.append(q)
                    self._ask_quote = q
        else: # spread = mpi
            if self._bid_quote: # check if not alone at the bid
                if self._bid_quote['price'] < qsignal['best_bid'] or self._bid_quote['quantity'] < qsignal['bid_size']:
                    self.cancel_collector.append(self._make_cancel_quote(self._bid_quote, time))
                    self._bid_quote = None
            if self._ask_quote: # check if not alone at the ask
                if self._ask_quote['price'] > qsignal['best_ask'] or self._ask_quote['quantity'] < qsignal['ask_size']:
                    self.cancel_collector.append(self._make_cancel_quote(self._ask_quote, time))
                    self._ask_quote = None
            

class Taker(ZITrader):
    '''
    Taker generates quotes (dicts) based on take probability.
        
    Subclass of ZITrader
    Public attributes: trader_type, quote_collector (from ZITrader)
    Public methods: process_signal 
    '''

    def __init__(self, name, maxq):
        ZITrader.__init__(self, name, maxq)
        self.trader_type = 'Taker'
        
    def __repr__(self):
        return 'Trader({0}, {1}, {2})'.format(self._trader_id, self._max_quantity, self.trader_type)
        
    def process_signal(self, time, q_taker):
        '''Taker buys or sells with 50% probability.'''
        self.quote_collector.clear()
        if random.uniform(0,1) < q_taker: # q_taker > 0.5 implies greater probability of a buy order
            price = 2000000 # agent buys at max price (or better)
            side = 'buy'
        else:
            price = 0 # agent sells at min price (or better)
            side = 'sell'
        q = self._make_add_quote(time, self._max_quantity, side, price)
        self.quote_collector.append(q)
        
        
class Provider(ZITrader):
    '''
    Provider generates quotes (dicts) based on make probability.
    
    Subclass of ZITrader
    Public attributes: trader_type, quote_collector (from ZITrader), cancel_collector, local_book
    Public methods: confirm_cancel_local, confirm_trade_local, process_signal, bulk_cancel
    '''

    def __init__(self, name, maxq, mpi, delta):
        '''Provider has own mpi and delta; a local_book to track outstanding orders and a 
        cancel_collector to convey cancel messages to the exchange.
        '''
        ZITrader.__init__(self, name, maxq)
        self.trader_type = 'Provider'
        self._mpi = mpi
        self._delta = delta
        self.local_book = {}
        self.cancel_collector = []
                
    def __repr__(self):
        return 'Trader({0}, {1}, {2})'.format(self._trader_id, self._max_quantity, self.trader_type)
    
    def _make_cancel_quote(self, q, time):
        return {'type': 'cancel', 'timestamp': time, 'order_id': q['order_id'], 'quantity': q['quantity'],
                'side': q['side'], 'price': q['price']}
        
    def confirm_cancel_local(self, cancel_dict):
        del self.local_book[cancel_dict['order_id']]

    def confirm_trade_local(self, confirm):
        to_modify = self.local_book.get(confirm['order_id'], "WTF???")
        if confirm['quantity'] == to_modify['quantity']:
            self.confirm_cancel_local(to_modify)
        else:
            self.local_book[confirm['order_id']]['quantity'] -= confirm['quantity']
            
    def bulk_cancel(self, time):
        '''bulk_cancel cancels _delta percent of outstanding orders'''
        self.cancel_collector.clear()
        lob = len(self.local_book)
        if lob > 0:
            order_keys = list(self.local_book.keys())
            orders_to_delete = np.random.ranf(lob)
            for idx in range(lob):
                if orders_to_delete[idx] < self._delta:
                    self.cancel_collector.append(self._make_cancel_quote(self.local_book.get(order_keys[idx]), time))

    def process_signal(self, time, qsignal, q_provider, lambda_t):
        '''Provider buys or sells with probability related to q_provide'''
        self.quote_collector.clear()
        if np.random.uniform(0,1) < q_provider:
            price = self._choose_price_from_exp('bid', qsignal['best_ask'], lambda_t)
            side = 'buy'
        else:
            price = self._choose_price_from_exp('ask', qsignal['best_bid'], lambda_t)
            side = 'sell'
        q = self._make_add_quote(time, self._max_quantity, side, price)
        self.local_book[q['order_id']] = q
        self.quote_collector.append(q)            
      
    def _choose_price_from_exp(self, side, inside_price, lambda_t):
        '''Prices chosen from an exponential distribution'''
        # make pricing explicit for now. Logic scales for other mpi.
        plug = np.int(lambda_t*np.log(np.random.rand()))
        if side == 'bid':
            #price = np.int(5*np.floor((inside_price-1-plug)/5))
            price = inside_price-1-plug
        else:
            #price = np.int(5*np.ceil((inside_price+1+plug)/5))
            price = inside_price+1+plug
        return price
    

class Provider5(Provider):
    '''
    Provider5 generates quotes (dicts) based on make probability.
    
    Subclass of Provider
    '''

    def __init__(self, name, maxq, mpi, delta):
        '''Provider has own mpi and delta; a local_book to track outstanding orders and a 
        cancel_collector to convey cancel messages to the exchange.
        '''
        Provider.__init__(self, name, maxq, mpi, delta)

    def _choose_price_from_exp(self, side, inside_price, lambda_t):
        '''Prices chosen from an exponential distribution'''
        # make pricing explicit for now. Logic scales for other mpi.
        plug = np.int(lambda_t*np.log(np.random.rand()))
        if side == 'bid':
            price = np.int(5*np.floor((inside_price-1-plug)/5))
        else:
            price = np.int(5*np.ceil((inside_price+1+plug)/5))
        return price
    
    
class MarketMaker(Provider):
    '''
    MarketMaker generates a series of quotes near the inside (dicts) based on make probability.
    
    Subclass of Provider
    Public attributes: trader_type, quote_collector (from ZITrader), cancel_collector (from Provider),
    cash_flow_collector
    Public methods: confirm_cancel_local (from Provider), confirm_trade_local, process_signal 
    '''

    def __init__(self, name, maxq, mpi, delta, num_quotes, quote_range):
        '''_num_quotes and _quote_range determine the depth of MM quoting;
        _position and _cashflow are stored MM metrics
        '''
        Provider.__init__(self, name, maxq, mpi, delta)
        self.trader_type = 'MarketMaker'
        self._num_quotes = num_quotes
        self._quote_range = quote_range
        self._position = 0
        self._cash_flow = 0
        self.cash_flow_collector = []
                      
    def __repr__(self):
        return 'Trader({0}, {1}, {2}, {3})'.format(self._trader_id, self._max_quantity, self.trader_type, self._num_quotes)
            
    def confirm_trade_local(self, confirm):
        '''Modify _cash_flow and _position; update the local_book'''
        if confirm['side'] == 'buy':
            self._cash_flow -= confirm['price']*confirm['quantity']
            self._position += confirm['quantity']
        else:
            self._cash_flow += confirm['price']*confirm['quantity']
            self._position -= confirm['quantity']
        to_modify = self.local_book.get(confirm['order_id'], "WTF???")
        if confirm['quantity'] == to_modify['quantity']:
            self.confirm_cancel_local(to_modify)
        else:
            self.local_book[confirm['order_id']]['quantity'] -= confirm['quantity']
        self._cumulate_cashflow(confirm['timestamp'])
         
    def _cumulate_cashflow(self, timestamp):
        self.cash_flow_collector.append({'mmid': self._trader_id, 'timestamp': timestamp, 'cash_flow': self._cash_flow,
                                         'position': self._position})
            
    def process_signal(self, time, qsignal, q_provider):
        '''
        MM chooses prices from a grid determined by the best prevailing prices.
        MM never joins the best price if it has size=1.
        ''' 
        # make pricing explicit for now. Logic scales for other mpi and quote ranges.
        self.quote_collector.clear()
        if random.uniform(0,1) < q_provider:
            max_bid_price = qsignal['best_bid'] if qsignal['bid_size'] > 1 else qsignal['best_bid']-self._mpi
            prices = np.random.choice(range(max_bid_price-self._quote_range+1, max_bid_price+1, self._mpi), size=self._num_quotes)
            side = 'buy'
        else:
            min_ask_price = qsignal['best_ask'] if qsignal['ask_size'] > 1 else qsignal['best_ask']+self._mpi
            prices = np.random.choice(range(min_ask_price, min_ask_price+self._quote_range, self._mpi), size=self._num_quotes)
            side = 'sell'
        for price in prices:
            q = self._make_add_quote(time, self._max_quantity, side, price)
            self.local_book[q['order_id']] = q
            self.quote_collector.append(q)
            
            
class MarketMaker5(MarketMaker):
    '''
    MarketMaker5 generates a series of quotes near the inside (dicts) based on make probability.
    
    Subclass of MarketMaker
    Public methods: process_signal 
    '''
    
    def __init__(self, name, maxq, mpi, delta, num_quotes, quote_range):
        '''
        _num_quotes and _quote_range determine the depth of MM quoting;
        _position and _cashflow are stored MM metrics
        '''
        MarketMaker.__init__(self, name, maxq, mpi, delta, num_quotes, quote_range)
        self._p5ask = [1/20, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/30]
        self._p5bid = [1/30, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/20]
               
    def process_signal(self, time, qsignal, q_provider):
        '''
        MM chooses prices from a grid determined by the best prevailing prices.
        MM never joins the best price if it has size=1.
        ''' 
        # make pricing explicit for now. Logic scales for other mpi and quote ranges.
        self.quote_collector.clear()
        if random.uniform(0,1) < q_provider:
            max_bid_price = qsignal['best_bid'] if qsignal['bid_size'] > 1 else qsignal['best_bid']-self._mpi
            prices = np.random.choice(range(max_bid_price-self._quote_range, max_bid_price+1, self._mpi), size=self._num_quotes, p=self._p5bid)
            side = 'buy'
        else:
            min_ask_price = qsignal['best_ask'] if qsignal['ask_size'] > 1 else qsignal['best_ask']+self._mpi
            prices = np.random.choice(range(min_ask_price, min_ask_price+self._quote_range+1, self._mpi), size=self._num_quotes, p=self._p5ask)
            side = 'sell'
        for price in prices:
            q = self._make_add_quote(time, self._max_quantity, side, price)
            self.local_book[q['order_id']] = q
            self.quote_collector.append(q)
