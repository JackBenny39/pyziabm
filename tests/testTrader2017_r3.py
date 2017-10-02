import random
import numpy as np
import unittest

from pyabmzi.trader2017_r3 import Provider, Provider5, Taker, MarketMaker, MarketMaker5, PennyJumper


class TestTrader(unittest.TestCase):
    '''
    Five classes:
    1. ZITrader is a base class with make_add_quote()
    2. Taker inherits from ZITrader with process_signal()
    3. Provider inherits from ZITrader with make_cancel_quote(), confirm_cancel_local(), confirm_trade_local(), 
       process_signal(), choose_price_from_exp() and bulk_cancel().
    4. MarketMaker inherits from Provider with confirm_trade_local(), cumulate_cashflow() and process_signal().
    5. PennyJumper inherits from ZITrader with make_cancel_quote(), confirm_trade_local() and process_signal().
       PennyJumper has an ask_quote dictionary and bid_quote dictionary which can be None.
    '''

    def setUp(self):
        self.p1 = Provider('p1', 1, 1, 0.05)
        self.p5 = Provider5('p5', 1, 5, 0.05)
        self.t1 = Taker('t1', 1)
        self.m1 = MarketMaker('m1', 1, 1, 0.05, 12, 60)
        self.m5 = MarketMaker5('m5', 1, 5, 0.05, 12, 60)
        self.j1 = PennyJumper('j1', 1, 5)
        self.q1 = {'order_id': 'p1_1', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'buy',
                   'price': 125}
        self.q2 = {'order_id': 'p1_2', 'timestamp': 2, 'type': 'add', 'quantity': 5, 'side': 'buy',
                   'price': 125}
        self.q3 = {'order_id': 'p1_3', 'timestamp': 3, 'type': 'add', 'quantity': 1, 'side': 'buy',
                   'price': 124}
        self.q4 = {'order_id': 'p1_4', 'timestamp': 4, 'type': 'add', 'quantity': 1, 'side': 'buy',
                   'price': 123}
        self.q5 = {'order_id': 'p1_5', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                   'price': 122}
        self.q6 = {'order_id': 'p1_6', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                   'price': 126}
        self.q7 = {'order_id': 'p1_7', 'timestamp': 7, 'type': 'add', 'quantity': 5, 'side': 'sell',
                   'price': 127}
        self.q8 = {'order_id': 'p1_8', 'timestamp': 8, 'type': 'add', 'quantity': 1, 'side': 'sell',
                   'price': 128}
        self.q9 = {'order_id': 'p1_9', 'timestamp': 9, 'type': 'add', 'quantity': 1, 'side': 'sell',
                   'price': 129}
        self.q10 = {'order_id': 'p1_10', 'timestamp': 10, 'type': 'add', 'quantity': 1, 'side': 'sell',
                   'price': 130}
        
# ZITrader tests
    
    def test_make_add_quote(self):
        time = 1
        quantity = 1
        side = 'sell'
        price = 125
        q = self.p1._make_add_quote(time, quantity, side, price)
        expected = {'order_id': 'p1_1', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'sell', 
                    'price': 125}
        self.assertDictEqual(q, expected)
        
# Taker tests

    def test_repr_Taker(self):
        #print('Provider: {0}, Taker: {1}'.format(self.p1, self.t1))
        self.assertEqual('Taker: Trader(t1, 1, Taker)', 'Taker: {0}'.format(self.t1))
        
    def test_process_signal_Taker(self):
        '''
        Generates a quote object (dict) and appends to quote_collector
        '''
        time = 1
        q_taker = 0.5
        low_ru_seed = 1
        hi_ru_seed = 10
        self.assertFalse(self.t1.quote_collector)
        random.seed(low_ru_seed)
        self.t1.process_signal(time, q_taker)
        self.assertEqual(len(self.t1.quote_collector), 1)
        self.assertEqual(self.t1.quote_collector[0]['side'], 'buy')
        self.assertEqual(self.t1.quote_collector[0]['price'], 2000000)
        random.seed(hi_ru_seed)
        self.t1.process_signal(time, q_taker)
        self.assertEqual(len(self.t1.quote_collector), 1)
        self.assertEqual(self.t1.quote_collector[0]['side'], 'sell')
        self.assertEqual(self.t1.quote_collector[0]['price'], 0)
        
# Provider tests  

    def test_repr_Provider(self):
        #print('Provider: {0}, Taker: {1}'.format(self.p1, self.t1))
        self.assertEqual('Provider: Trader(p1, 1, Provider)', 'Provider: {0}'.format(self.p1))
        self.assertEqual('Provider: Trader(p5, 1, Provider)', 'Provider: {0}'.format(self.p5))
              
    def test_make_cancel_quote_Provider(self):
        q = self.p1._make_cancel_quote(self.q1, 2)
        expected = {'order_id': 'p1_1', 'timestamp': 2, 'type': 'cancel', 'quantity': 1, 'side': 'buy', 
                    'price': 125}
        self.assertDictEqual(q, expected)
        
    def test_confirm_cancel_local_Provider(self):
        self.p1.local_book[self.q1['order_id']] = self.q1
        self.p1.local_book[self.q2['order_id']] = self.q2
        self.assertEqual(len(self.p1.local_book), 2)
        q = self.p1._make_cancel_quote(self.q1, 2)
        self.p1.confirm_cancel_local(q)
        self.assertEqual(len(self.p1.local_book), 1)
        expected = {self.q2['order_id']: self.q2}
        self.assertDictEqual(self.p1.local_book, expected)

    def test_confirm_trade_local_Provider(self):
        '''
        Test Provider for full and partial trade
        '''
        # Provider
        self.p1.local_book[self.q1['order_id']] = self.q1
        self.p1.local_book[self.q2['order_id']] = self.q2
        # trade full quantity of q1
        trade1 = {'timestamp': 2, 'trader': 'p1', 'order_id': 'p1_1', 'quantity': 1, 'side': 'buy', 'price': 2000000}
        self.assertEqual(len(self.p1.local_book), 2)
        self.p1.confirm_trade_local(trade1)
        self.assertEqual(len(self.p1.local_book), 1)
        expected = {self.q2['order_id']: self.q2}
        self.assertDictEqual(self.p1.local_book, expected)
        # trade partial quantity of q2
        trade2 = {'timestamp': 3, 'trader': 'p1', 'order_id': 'p1_2', 'quantity': 2, 'side': 'buy', 'price': 2000000}
        self.p1.confirm_trade_local(trade2)
        self.assertEqual(len(self.p1.local_book), 1)
        expected = {'order_id': 'p1_2', 'timestamp': 2, 'type': 'add', 'quantity': 3, 'side': 'buy', 
                    'price': 125}
        self.assertDictEqual(self.p1.local_book.get(trade2['order_id']), expected) 
        
    def test_choose_price_from_exp(self):
        # mpi == 1
        sell_price = self.p1._choose_price_from_exp('bid', 75000, -100)
        self.assertLess(sell_price, 75000)
        buy_price = self.p1._choose_price_from_exp('ask', 25000, -100)
        self.assertGreater(buy_price, 25000)
        self.assertEqual(np.remainder(buy_price,self.p1._mpi),0)
        self.assertEqual(np.remainder(sell_price,self.p1._mpi),0)
        # mpi == 5        
        sell_price = self.p5._choose_price_from_exp('bid', 75000, -100)
        self.assertLess(sell_price, 75000)
        buy_price = self.p5._choose_price_from_exp('ask', 25000, -100)
        self.assertGreater(buy_price, 25000)
        self.assertEqual(np.remainder(buy_price,self.p5._mpi),0)
        self.assertEqual(np.remainder(sell_price,self.p5._mpi),0)
            
    def test_process_signal_Provider(self):
        time = 1
        q_provider = 0.5
        low_ru_seed = 1
        hi_ru_seed = 10
        tob_price = {'best_bid': 25000, 'best_ask': 75000}
        self.assertFalse(self.p1.quote_collector)
        self.assertFalse(self.p1.local_book)
        np.random.seed(low_ru_seed)
        self.p1.process_signal(time, tob_price, q_provider, -100)
        self.assertEqual(len(self.p1.quote_collector), 1)
        self.assertEqual(self.p1.quote_collector[0]['side'], 'buy')
        self.assertEqual(len(self.p1.local_book), 1)
        np.random.seed(hi_ru_seed)
        self.p1.process_signal(time, tob_price, q_provider, -100)
        self.assertEqual(len(self.p1.quote_collector), 1)
        self.assertEqual(self.p1.quote_collector[0]['side'], 'sell')
        self.assertEqual(len(self.p1.local_book), 2)
    
    def test_bulk_cancel_Provider(self):
        '''
        Put 10 orders in the book, use random seed to determine which orders are cancelled,
        test for cancelled orders in the queue
        '''
        self.assertFalse(self.p1.local_book)
        self.assertFalse(self.p1.cancel_collector)
        self.p1.local_book[self.q1['order_id']] = self.q1
        self.p1.local_book[self.q2['order_id']] = self.q2
        self.p1.local_book[self.q3['order_id']] = self.q3
        self.p1.local_book[self.q4['order_id']] = self.q4
        self.p1.local_book[self.q5['order_id']] = self.q5
        self.p1.local_book[self.q6['order_id']] = self.q6
        self.p1.local_book[self.q7['order_id']] = self.q7
        self.p1.local_book[self.q8['order_id']] = self.q8
        self.p1.local_book[self.q9['order_id']] = self.q9
        self.p1.local_book[self.q10['order_id']] = self.q10
        self.assertEqual(len(self.p1.local_book), 10)
        self.assertFalse(self.p1.cancel_collector)
        # np.random seed = 8 generates 1 position less than 0.025 from np.random.ranf: 5
        np.random.seed(8)
        self.p1._delta = 0.025
        self.p1.bulk_cancel(11)
        self.assertEqual(len(self.p1.cancel_collector), 1)
        # np.random seed = 7 generates 2 positions less than 0.1 from np.random.ranf: 0, 7
        np.random.seed(7)
        self.p1._delta = 0.1
        self.p1.bulk_cancel(12)
        self.assertEqual(len(self.p1.cancel_collector), 2)
        # np.random seed = 6 generates 0 position less than 0.025 from np.random.ranf
        np.random.seed(6)
        self.p1._delta = 0.025
        self.p1.bulk_cancel(12)
        self.assertFalse(self.p1.cancel_collector)
        
    # MarketMaker tests
           
    def test_repr_MM(self):
        self.assertEqual('MarketMaker: Trader(m1, 1, MarketMaker, 12)', 'MarketMaker: {0}'.format(self.m1))
        self.assertEqual('MarketMaker: Trader(m5, 1, MarketMaker, 12)', 'MarketMaker: {0}'.format(self.m5))
        
    def test_confirm_trade_local_MM(self):
        '''
        Test Market Maker for full and partial trade
        '''
        # MarketMaker buys
        self.m1.local_book[self.q1['order_id']] = self.q1
        self.m1.local_book[self.q2['order_id']] = self.q2
        # trade full quantity of q1
        trade1 = {'timestamp': 2, 'trader': 'p1', 'order_id': 'p1_1', 'quantity': 1, 'side': 'buy', 'price': 2000000}
        self.assertEqual(len(self.m1.local_book), 2)
        self.m1.confirm_trade_local(trade1)
        self.assertEqual(len(self.m1.local_book), 1)
        self.assertEqual(self.m1._position, 1)
        expected = {self.q2['order_id']: self.q2}
        self.assertDictEqual(self.m1.local_book, expected)
        # trade partial quantity of q2
        trade2 = {'timestamp': 3, 'trader': 'p1', 'order_id': 'p1_2', 'quantity': 2, 'side': 'buy', 'price': 2000000}
        self.m1.confirm_trade_local(trade2)
        self.assertEqual(len(self.m1.local_book), 1)
        self.assertEqual(self.m1._position, 3)
        expected = {'order_id': 'p1_2', 'timestamp': 2, 'type': 'add', 'quantity': 3, 'side': 'buy', 
                    'price': 125}
        self.assertDictEqual(self.m1.local_book.get(trade2['order_id']), expected) 
        
        # MarketMaker sells
        self.setUp()
        self.m1.local_book[self.q6['order_id']] = self.q6
        self.m1.local_book[self.q7['order_id']] = self.q7
        # trade full quantity of q6
        trade1 = {'timestamp': 6, 'trader': 'p1', 'order_id': 'p1_6', 'quantity': 1, 'side': 'sell', 'price': 0}
        self.assertEqual(len(self.m1.local_book), 2)
        self.m1.confirm_trade_local(trade1)
        self.assertEqual(len(self.m1.local_book), 1)
        self.assertEqual(self.m1._position, -1)
        expected = {self.q7['order_id']: self.q7}
        self.assertDictEqual(self.m1.local_book, expected)
        # trade partial quantity of q7
        trade2 = {'timestamp': 7, 'trader': 'p1', 'order_id': 'p1_7', 'quantity': 2, 'side': 'sell', 'price': 0}
        self.m1.confirm_trade_local(trade2)
        self.assertEqual(len(self.m1.local_book), 1)
        self.assertEqual(self.m1._position, -3)
        expected = {'order_id': 'p1_7', 'timestamp': 7, 'type': 'add', 'quantity': 3, 'side': 'sell', 
                    'price': 127}
        self.assertDictEqual(self.m1.local_book.get(trade2['order_id']), expected) 
        
    def test_cumulate_cashflow_MM(self):
        self.assertFalse(self.m1.cash_flow_collector)
        expected = {'mmid': 'm1', 'timestamp': 10, 'cash_flow': 0, 'position': 0}
        self.m1._cumulate_cashflow(10)
        self.assertDictEqual(self.m1.cash_flow_collector[0], expected)
        
    def test_process_signal_MM5_12(self):
        time = 1
        q_provider = 0.5
        low_ru_seed = 1
        hi_ru_seed = 10
        # size > 1: market maker matches best price
        tob1 = {'best_bid': 25000, 'best_ask': 75000, 'bid_size': 10, 'ask_size': 10}
        self.assertFalse(self.m5.quote_collector)
        self.assertFalse(self.m5.local_book)
        random.seed(low_ru_seed)
        self.m5.process_signal(time, tob1, q_provider)
        self.assertEqual(len(self.m5.quote_collector), 12)
        self.assertEqual(self.m5.quote_collector[0]['side'], 'buy')
        for i in range(len(self.m5.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m5.quote_collector[i]['price'], 25000)
                self.assertGreaterEqual(self.m5.quote_collector[i]['price'], 24935)
                self.assertTrue(self.m5.quote_collector[i]['price'] in range(24935, 25001, 5))
        self.assertEqual(len(self.m5.local_book), 12)
        random.seed(hi_ru_seed)
        self.m5.process_signal(time, tob1, q_provider)
        self.assertEqual(len(self.m5.quote_collector), 12)
        self.assertEqual(self.m5.quote_collector[0]['side'], 'sell')
        for i in range(len(self.m5.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m5.quote_collector[i]['price'], 75065)
                self.assertGreaterEqual(self.m5.quote_collector[i]['price'], 75000)
                self.assertTrue(self.m5.quote_collector[i]['price'] in range(75000, 75066, 5))
        self.assertEqual(len(self.m5.local_book), 24)
        # size == 1: market maker adds liquidity one point behind
        self.setUp()
        tob2 = {'best_bid': 25000, 'best_ask': 75000, 'bid_size': 1, 'ask_size': 1}
        self.assertFalse(self.m5.quote_collector)
        self.assertFalse(self.m5.local_book)
        np.random.seed(low_ru_seed)
        self.m5.process_signal(time, tob2, q_provider)
        self.assertEqual(len(self.m5.quote_collector), 12)
        self.assertEqual(self.m5.quote_collector[0]['side'], 'buy')
        for i in range(len(self.m5.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m5.quote_collector[i]['price'], 24995)
                self.assertGreaterEqual(self.m5.quote_collector[i]['price'], 24930)
                self.assertTrue(self.m5.quote_collector[i]['price'] in range(24930, 24995))
        self.assertEqual(len(self.m5.local_book), 12)
        np.random.seed(hi_ru_seed)
        self.m5.process_signal(time, tob2, q_provider)
        self.assertEqual(len(self.m5.quote_collector), 12)
        self.assertEqual(self.m5.quote_collector[0]['side'], 'sell')
        for i in range(len(self.m5.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m5.quote_collector[i]['price'], 75065)
                self.assertGreaterEqual(self.m5.quote_collector[i]['price'], 75005)
                self.assertTrue(self.m5.quote_collector[i]['price'] in range(75005, 75065, 5))
        self.assertEqual(len(self.m5.local_book), 24)
        
    def test_process_signal_MM1_12(self):
        time = 1
        q_provider = 0.5
        low_ru_seed = 1
        hi_ru_seed = 10
        # size > 1: market maker matches best price
        tob1 = {'best_bid': 25000, 'best_ask': 75000, 'bid_size': 10, 'ask_size': 10}
        self.assertFalse(self.m1.quote_collector)
        self.assertFalse(self.m1.local_book)
        random.seed(low_ru_seed)
        self.m1.process_signal(time, tob1, q_provider)
        self.assertEqual(len(self.m1.quote_collector), 12)
        self.assertEqual(self.m1.quote_collector[0]['side'], 'buy')
        for i in range(len(self.m1.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m1.quote_collector[i]['price'], 25000)
                self.assertGreaterEqual(self.m1.quote_collector[i]['price'], 24941)
                self.assertTrue(self.m1.quote_collector[i]['price'] in range(24941, 25001))
        self.assertEqual(len(self.m1.local_book), 12)
        random.seed(hi_ru_seed)
        self.m1.process_signal(time, tob1, q_provider)
        self.assertEqual(len(self.m1.quote_collector), 12)
        self.assertEqual(self.m1.quote_collector[0]['side'], 'sell')
        for i in range(len(self.m1.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m1.quote_collector[i]['price'], 75060)
                self.assertGreaterEqual(self.m1.quote_collector[i]['price'], 75000)
                self.assertTrue(self.m1.quote_collector[i]['price'] in range(75000, 75061))
        self.assertEqual(len(self.m1.local_book), 24)
        # size == 1: market maker adds liquidity one point behind
        self.setUp()
        tob2 = {'best_bid': 25000, 'best_ask': 75000, 'bid_size': 1, 'ask_size': 1}
        self.assertFalse(self.m1.quote_collector)
        self.assertFalse(self.m1.local_book)
        np.random.seed(low_ru_seed)
        self.m1.process_signal(time, tob2, q_provider)
        self.assertEqual(len(self.m1.quote_collector), 12)
        self.assertEqual(self.m1.quote_collector[0]['side'], 'buy')
        for i in range(len(self.m1.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m1.quote_collector[i]['price'], 24999)
                self.assertGreaterEqual(self.m1.quote_collector[i]['price'], 24940)
                self.assertTrue(self.m1.quote_collector[i]['price'] in range(24940, 25000))
        self.assertEqual(len(self.m1.local_book), 12)
        np.random.seed(hi_ru_seed)
        self.m1.process_signal(time, tob2, q_provider)
        self.assertEqual(len(self.m1.quote_collector), 12)
        self.assertEqual(self.m1.quote_collector[0]['side'], 'sell')
        for i in range(len(self.m1.quote_collector)):
            with self.subTest(i=i):
                self.assertLessEqual(self.m1.quote_collector[i]['price'], 75060)
                self.assertGreaterEqual(self.m1.quote_collector[i]['price'], 75001)
                self.assertTrue(self.m1.quote_collector[i]['price'] in range(75001, 75061))
        self.assertEqual(len(self.m1.local_book), 24)
        
    # PennyJumper tests
    def test_repr_PJ(self):
        self.assertEqual('PennyJumper: Trader(j1, 1, 5, PennyJumper)', 'PennyJumper: {0}'.format(self.j1))
        
    def test_confirm_trade_local_PJ(self):
        # PennyJumper book
        self.j1._bid_quote = {'order_id': 'j1_1', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'buy',
                             'price': 125}
        self.j1._ask_quote = {'order_id': 'j1_6', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                              'price': 126}
        # trade at the bid
        trade1 = {'timestamp': 2, 'trader': 'j1', 'order_id': 'j1_1', 'quantity': 1, 'side': 'buy', 'price': 0}
        self.assertTrue(self.j1._bid_quote)
        self.j1.confirm_trade_local(trade1)
        self.assertFalse(self.j1._bid_quote)
        # trade at the ask
        trade2 = {'timestamp': 12, 'trader': 'j1', 'order_id': 'j1_6', 'quantity': 1, 'side': 'sell', 'price': 2000000}
        self.assertTrue(self.j1._ask_quote)
        self.j1.confirm_trade_local(trade2)
        self.assertFalse(self.j1._ask_quote)
        
    def test_process_signal_PJ(self):
        # spread > mpi
        tob = {'bid_size': 5, 'best_bid': 999990, 'best_ask': 1000005, 'ask_size': 5}
        # PJ book empty
        self.j1._bid_quote = None
        self.j1._ask_quote = None
        # random.seed = 1 generates random.uniform(0,1) = 0.13 then .85
        # jump the bid by 1, then jump the ask by 1
        random.seed(1)
        self.j1.process_signal(5, tob, 0.5)
        self.assertDictEqual(self.j1._bid_quote, {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                                                 'price': 999995})
        tob = {'bid_size': 1, 'best_bid': 999995, 'best_ask': 1000005, 'ask_size': 5}
        self.j1.process_signal(6, tob, 0.5)
        self.assertDictEqual(self.j1._ask_quote, {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                                                 'price': 1000000})
        # PJ alone at tob
        tob = {'bid_size': 1, 'best_bid': 999995, 'best_ask': 1000000, 'ask_size': 1}
        # nothing happens
        self.j1.process_signal(7, tob, 0.5)
        self.assertDictEqual(self.j1._bid_quote, {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                                                 'price': 999995})
        self.assertDictEqual(self.j1._ask_quote, {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                                                 'price': 1000000})
        # PJ bid and ask behind the book
        tob = {'bid_size': 1, 'best_bid': 999990, 'best_ask': 1000005, 'ask_size': 1}
        self.j1._bid_quote = {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                             'price': 999985}
        self.j1._ask_quote = {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                             'price': 1000010}
        # random.seed = 1 generates random.uniform(0,1) = 0.13 then .85
        # jump the bid by 1, then jump the ask by 1; cancel old quotes
        random.seed(1)
        self.j1.process_signal(10, tob, 0.5)
        self.assertDictEqual(self.j1._bid_quote, {'order_id': 'j1_3', 'timestamp': 10, 'type': 'add', 'quantity': 1, 'side': 'buy',
                                                 'price': 999995})
        self.assertDictEqual(self.j1.cancel_collector[0], {'order_id': 'j1_1', 'timestamp': 10, 'type': 'cancel', 'quantity': 1, 'side': 'buy',
                                                            'price': 999985})
        self.assertDictEqual(self.j1.quote_collector[0], self.j1._bid_quote)
        self.j1.process_signal(11, tob, 0.5)
        self.assertDictEqual(self.j1._ask_quote, {'order_id': 'j1_4', 'timestamp': 11, 'type': 'add', 'quantity': 1, 'side': 'sell',
                                                 'price': 1000000})
        self.assertDictEqual(self.j1.cancel_collector[0], {'order_id': 'j1_2', 'timestamp': 11, 'type': 'cancel', 'quantity': 1, 'side': 'sell',
                                                           'price': 1000010})
        self.assertDictEqual(self.j1.quote_collector[0],self.j1._ask_quote)
        # PJ not alone at the inside
        tob = {'bid_size': 5, 'best_bid': 999990, 'best_ask': 1000010, 'ask_size': 5}
        self.j1._bid_quote = {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                             'price': 999990}
        self.j1._ask_quote = {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                             'price': 1000010}
        # random.seed = 1 generates random.uniform(0,1) = 0.13 then .85
        # jump the bid by 1, then jump the ask by 1; cancel old quotes
        random.seed(1)
        self.j1.process_signal(12, tob, 0.5)
        self.assertDictEqual(self.j1._bid_quote, {'order_id': 'j1_5', 'timestamp': 12, 'type': 'add', 'quantity': 1, 'side': 'buy',
                                                 'price': 999995})
        self.assertDictEqual(self.j1.cancel_collector[0], {'order_id': 'j1_1', 'timestamp': 12, 'type': 'cancel', 'quantity': 1, 'side': 'buy',
                                                           'price': 999990})
        self.assertDictEqual(self.j1.quote_collector[0], self.j1._bid_quote)
        self.j1.process_signal(13, tob, 0.5)
        self.assertDictEqual(self.j1._ask_quote, {'order_id': 'j1_6', 'timestamp': 13, 'type': 'add', 'quantity': 1, 'side': 'sell',
                                                 'price': 1000005})
        self.assertDictEqual(self.j1.cancel_collector[0], {'order_id': 'j1_2', 'timestamp': 13, 'type': 'cancel', 'quantity': 1, 'side': 'sell',
                                                           'price': 1000010})
        self.assertDictEqual(self.j1.quote_collector[0],self.j1._ask_quote)
        # spread at mpi, PJ alone at nbbo
        tob = {'bid_size': 1, 'best_bid': 999995, 'best_ask': 1000000, 'ask_size': 1}
        self.j1._bid_quote = {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                             'price': 999995}
        self.j1._ask_quote = {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                             'price': 1000000}
        random.seed(1)
        self.j1.process_signal(14, tob, 0.5)
        self.assertDictEqual(self.j1._bid_quote, {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                                                 'price': 999995})
        self.assertFalse(self.j1.cancel_collector)
        self.assertFalse(self.j1.quote_collector)
        self.j1.process_signal(15, tob, 0.5)
        self.assertDictEqual(self.j1._ask_quote, {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                                                 'price': 1000000})
        self.assertFalse(self.j1.cancel_collector)
        self.assertFalse(self.j1.quote_collector)
        # PJ bid and ask behind the book
        self.j1._bid_quote = {'order_id': 'j1_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                             'price': 999990}
        self.j1._ask_quote = {'order_id': 'j1_2', 'timestamp': 6, 'type': 'add', 'quantity': 1, 'side': 'sell',
                             'price': 1000010}
        # random.seed = 1 generates random.uniform(0,1) = 0.13 then .85
        # cancel bid and ask
        random.seed(1)
        self.assertTrue(self.j1._bid_quote)
        self.assertTrue(self.j1._ask_quote)
        self.j1.process_signal(16, tob, 0.5)
        self.assertFalse(self.j1._bid_quote)
        self.assertFalse(self.j1._ask_quote)
        self.assertDictEqual(self.j1.cancel_collector[0], {'order_id': 'j1_1', 'timestamp': 16, 'type': 'cancel', 'quantity': 1, 'side': 'buy',
                                                           'price': 999990})
        self.assertDictEqual(self.j1.cancel_collector[1], {'order_id': 'j1_2', 'timestamp': 16, 'type': 'cancel', 'quantity': 1, 'side': 'sell',
                                                           'price': 1000010})
        self.assertFalse(self.j1.quote_collector)
        
    
