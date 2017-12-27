from pyziabm.orderbook3 import Orderbook
import unittest


class TestOrderbook(unittest.TestCase):
    '''
    Attribute objects in the Orderbook class include:
        order_history: list
        _bid_book: dictionary
        _bid_book_prices: sorted list
        _ask_book: dictionary
        _ask_book_prices: sorted list
        confirm_modify_collector: list
        confirm_trade_collector: list
        sip_collector: list
        trade_book: list
    Each method impacts one or more of these attributes.
    '''
    
    def setUp(self):
        '''
        setUp creates the Orderbook instance and a set of orders
        '''
        self.ex1 = Orderbook(5)
        self.q0_buy = {'order_id': 't1_0', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'buy',
                       'price': 50}
        self.q1_buy = {'order_id': 't1_1', 'timestamp': 2, 'type': 'add', 'quantity': 1, 'side': 'buy',
                       'price': 50}
        self.q2_buy = {'order_id': 't1_2', 'timestamp': 3, 'type': 'add', 'quantity': 1, 'side': 'buy',
                       'price': 50}
        self.q3_buy = {'order_id': 't10_1', 'timestamp': 4, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 49}
        self.q4_buy = {'order_id': 't11_1', 'timestamp': 5, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 47}
        self.q5_buy = {'order_id': 't12_1', 'timestamp': 6, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 47}
        self.q6_buy = {'order_id': 't13_1', 'timestamp': 7, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 47}
        self.q0_sell = {'order_id': 't1_5', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'sell',
                        'price': 52}
        self.q1_sell = {'order_id': 't1_3', 'timestamp': 2, 'type': 'add', 'quantity': 1, 'side': 'sell',
                        'price': 52}
        self.q2_sell = {'order_id': 't1_4', 'timestamp': 3, 'type': 'add', 'quantity': 1, 'side': 'sell',
                        'price': 52}
        self.q3_sell = {'order_id': 't10_2', 'timestamp': 4, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 53}
        self.q4_sell = {'order_id': 't11_2', 'timestamp': 5, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 55}
        self.q5_sell = {'order_id': 't12_2', 'timestamp': 6, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 53}
        self.q6_sell = {'order_id': 't13_2', 'timestamp': 7, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 55}
            
    def test_add_order_to_history(self):
        '''
        add_order_to_history() impacts the order_history list
        '''
        h1 = {'order_id': 't1_5', 'timestamp': 4, 'type': 'add', 'quantity': 5, 'side': 'sell', 'price': 55}
        self.assertFalse(self.ex1.order_history)
        h1['exid'] = 1
        self.ex1._add_order_to_history(h1)
        self.assertDictEqual(h1, self.ex1.order_history[0])
    
    def test_add_order_to_book(self):
        '''
        add_order_to_book() impacts _bid_book and _bid_book_prices or _ask_book and _ask_book_prices
        Add two buy orders, then two sell orders
        '''
        # 2 buy orders
        self.assertFalse(self.ex1._bid_book_prices)
        self.assertFalse(self.ex1._bid_book)
        self.ex1.add_order_to_book(self.q1_buy)
        self.assertTrue(50 in self.ex1._bid_book_prices)
        self.assertTrue(50 in self.ex1._bid_book.keys())
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 1)
        self.assertEqual(self.ex1._bid_book[50]['size'], 1)
        self.assertEqual(self.ex1._bid_book[50]['order_ids'][0], self.q1_buy['order_id'])
        self.assertDictEqual(self.ex1._bid_book[50]['orders'][self.q1_buy['order_id']], self.q1_buy)
        self.ex1.add_order_to_book(self.q2_buy)
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 2)
        self.assertEqual(self.ex1._bid_book[50]['size'], 2)
        self.assertEqual(self.ex1._bid_book[50]['order_ids'][1], self.q2_buy['order_id'])
        self.assertDictEqual(self.ex1._bid_book[50]['orders'][self.q2_buy['order_id']], self.q2_buy)
        # 2 sell orders
        self.assertFalse(self.ex1._ask_book_prices)
        self.assertFalse(self.ex1._ask_book)
        self.ex1.add_order_to_book(self.q1_sell)
        self.assertTrue(52 in self.ex1._ask_book_prices)
        self.assertTrue(52 in self.ex1._ask_book.keys())
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 1)
        self.assertEqual(self.ex1._ask_book[52]['size'], 1)
        self.assertEqual(self.ex1._ask_book[52]['order_ids'][0], self.q1_sell['order_id'])
        self.assertDictEqual(self.ex1._ask_book[52]['orders'][self.q1_sell['order_id']], self.q1_sell)
        self.ex1.add_order_to_book(self.q2_sell)
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 2)
        self.assertEqual(self.ex1._ask_book[52]['size'], 2)
        self.assertEqual(self.ex1._ask_book[52]['order_ids'][1], self.q2_sell['order_id'])
        self.assertDictEqual(self.ex1._ask_book[52]['orders'][self.q2_sell['order_id']], self.q2_sell)
        
    def test_remove_order(self):
        '''
        _remove_order() impacts _bid_book and _bid_book_prices or _ask_book and _ask_book_prices
        Add two  orders, remove the second order twice
        '''
        # buy orders
        self.ex1.add_order_to_book(self.q1_buy)
        self.ex1.add_order_to_book(self.q2_buy)
        self.assertTrue(50 in self.ex1._bid_book_prices)
        self.assertTrue(50 in self.ex1._bid_book.keys())
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 2)
        self.assertEqual(self.ex1._bid_book[50]['size'], 2)
        self.assertEqual(len(self.ex1._bid_book[50]['order_ids']), 2)
        # remove first order
        self.ex1._remove_order('buy', 50, 't1_1')
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 1)
        self.assertEqual(self.ex1._bid_book[50]['size'], 1)
        self.assertEqual(len(self.ex1._bid_book[50]['order_ids']), 1)
        self.assertFalse('t1_1' in self.ex1._bid_book[50]['orders'].keys())
        self.assertTrue(50 in self.ex1._bid_book_prices)
        # remove second order
        self.ex1._remove_order('buy', 50, 't1_2')
        self.assertFalse(self.ex1._bid_book_prices)
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 0)
        self.assertEqual(self.ex1._bid_book[50]['size'], 0)
        self.assertEqual(len(self.ex1._bid_book[50]['order_ids']), 0)
        self.assertFalse('t1_2' in self.ex1._bid_book[50]['orders'].keys())
        self.assertFalse(50 in self.ex1._bid_book_prices)
        # remove second order again
        self.ex1._remove_order('buy', 50, 't1_2')
        self.assertFalse(self.ex1._bid_book_prices)
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 0)
        self.assertEqual(self.ex1._bid_book[50]['size'], 0)
        self.assertEqual(len(self.ex1._bid_book[50]['order_ids']), 0)
        self.assertFalse('t1_2' in self.ex1._bid_book[50]['orders'].keys())
        # sell orders
        self.ex1.add_order_to_book(self.q1_sell)
        self.ex1.add_order_to_book(self.q2_sell)
        self.assertTrue(52 in self.ex1._ask_book_prices)
        self.assertTrue(52 in self.ex1._ask_book.keys())
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 2)
        self.assertEqual(self.ex1._ask_book[52]['size'], 2)
        self.assertEqual(len(self.ex1._ask_book[52]['order_ids']), 2)
        # remove first order
        self.ex1._remove_order('sell', 52, 't1_3')
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 1)
        self.assertEqual(self.ex1._ask_book[52]['size'], 1)
        self.assertEqual(len(self.ex1._ask_book[52]['order_ids']), 1)
        self.assertFalse('t1_1' in self.ex1._ask_book[52]['orders'].keys())
        self.assertTrue(52 in self.ex1._ask_book_prices)
        # remove second order
        self.ex1._remove_order('sell', 52, 't1_4')
        self.assertFalse(self.ex1._ask_book_prices)
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 0)
        self.assertEqual(self.ex1._ask_book[52]['size'], 0)
        self.assertEqual(len(self.ex1._ask_book[52]['order_ids']), 0)
        self.assertFalse('t1_2' in self.ex1._ask_book[52]['orders'].keys())
        self.assertFalse(52 in self.ex1._ask_book_prices)
        # remove second order again
        self.ex1._remove_order('sell', 52, 't1_4')
        self.assertFalse(self.ex1._ask_book_prices)
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 0)
        self.assertEqual(self.ex1._ask_book[52]['size'], 0)
        self.assertEqual(len(self.ex1._ask_book[52]['order_ids']), 0)
        self.assertFalse('t1_2' in self.ex1._ask_book[52]['orders'].keys())
        
    def test_modify_order(self):
        '''
        _modify_order() primarily impacts _bid_book or _ask_book 
        _modify_order() could impact _bid_book_prices or _ask_book_prices if the order results 
        in removing the full quantity with a call to _remove_order() 
        Add 1 order, remove partial, then remainder
        '''
        # Buy order
        q1 = {'order_id': 't1_1', 'timestamp': 5, 'type': 'add', 'quantity': 2, 'side': 'buy',
              'price': 50}
        self.ex1.add_order_to_book(q1)
        self.assertEqual(self.ex1._bid_book[50]['size'], 2)
        # remove 1
        self.ex1._modify_order('buy', 1, 't1_1', 50)
        self.assertEqual(self.ex1._bid_book[50]['size'], 1)
        self.assertEqual(self.ex1._bid_book[50]['orders']['t1_1']['quantity'], 1)
        self.assertTrue(self.ex1._bid_book_prices)
        # remove remainder
        self.ex1._modify_order('buy', 1, 't1_1', 50)
        self.assertFalse(self.ex1._bid_book_prices)
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 0)
        self.assertEqual(self.ex1._bid_book[50]['size'], 0)
        self.assertFalse('t1_1' in self.ex1._bid_book[50]['orders'].keys())
        # Sell order
        q2 = {'order_id': 't1_1', 'timestamp': 5, 'type': 'add', 'quantity': 2, 'side': 'sell',
              'price': 50}
        self.ex1.add_order_to_book(q2)
        self.assertEqual(self.ex1._ask_book[50]['size'], 2)
        # remove 1
        self.ex1._modify_order('sell', 1, 't1_1', 50)
        self.assertEqual(self.ex1._ask_book[50]['size'], 1)
        self.assertEqual(self.ex1._ask_book[50]['orders']['t1_1']['quantity'], 1)
        self.assertTrue(self.ex1._ask_book_prices)
        # remove remainder
        self.ex1._modify_order('sell', 1, 't1_1', 50)
        self.assertFalse(self.ex1._ask_book_prices)
        self.assertEqual(self.ex1._ask_book[50]['num_orders'], 0)
        self.assertEqual(self.ex1._ask_book[50]['size'], 0)
        self.assertFalse('t1_1' in self.ex1._ask_book[50]['orders'].keys())
        
    def test_add_trade_to_book(self):
        '''
        add_trade_to_book() impacts trade_book
        Check trade book empty, add a trade, check non-empty, verify dict equality
        '''
        t1 = dict(resting_order_id='t1_1', resting_timestamp=2, incoming_order_id='t2_1',
                  timestamp=5, price=50, quantity=1, side='buy')
        self.assertFalse(self.ex1.trade_book)
        self.ex1._add_trade_to_book('t1_1', 2, 't2_1', 5, 50, 1, 'buy')
        self.assertTrue(self.ex1.trade_book)
        self.assertDictEqual(t1, self.ex1.trade_book[0])
        
    def test_confirm_trade(self):
        '''
        confirm_trade() impacts confirm_trade_collector
        Check confirm trade collector empty, add a trade, check non-empty, verify dict equality
        '''
        t2 = dict(timestamp=5, trader='t3', order_id='t3_1', quantity=1, 
                  side='sell', price=50)
        self.assertFalse(self.ex1.confirm_trade_collector)
        self.ex1._confirm_trade(5, 'sell', 1, 't3_1', 50)
        self.assertTrue(self.ex1.confirm_trade_collector)
        self.assertDictEqual(t2, self.ex1.confirm_trade_collector[0])
        
    def test_confirm_modify(self):
        '''
        confirm_modify() impacts confirm_modify_collector
        Check confirm modify collector empty, add a trade, check non-empty, verify dict equality
        '''      
        m1 = dict(timestamp=7, trader='t5', order_id='t5_10', quantity=5, side='buy')
        self.assertFalse(self.ex1.confirm_modify_collector)
        self.ex1._confirm_modify(7, 'buy', 5, 't5_10')
        self.assertTrue(self.ex1.confirm_modify_collector)
        self.assertDictEqual(m1, self.ex1.confirm_modify_collector[0])

    def test_process_order(self):
        '''
        process_order() impacts confirm_modify_collector, traded indicator, order_history, 
        _bid_book and _bid_book_prices or _ask_book and _ask_book_prices.
        process_order() is a traffic manager. An order is either an add order or not. If it is an add order,
        it is either priced to go directly to the book or is sent to match_trade (which is tested below). If it
        is not an add order, it is either modified or cancelled. To test, we will add some buy and sell orders, 
        then test for trades, cancels and modifies. process_order() also resets some object collectors.
        '''
        self.q2_buy['quantity'] = 2
        self.q2_sell['quantity'] = 2
        
        self.assertEqual(len(self.ex1._ask_book_prices), 0)
        self.assertEqual(len(self.ex1._bid_book_prices), 0)
        self.assertFalse(self.ex1.confirm_modify_collector)
        self.assertFalse(self.ex1.order_history)
        self.assertFalse(self.ex1.traded)
        # seed order book
        self.ex1.add_order_to_book(self.q1_buy)
        self.ex1.add_order_to_book(self.q1_sell)
        # process new orders
        self.ex1.process_order(self.q2_buy)
        self.ex1.process_order(self.q2_sell)
        self.assertEqual(len(self.ex1._ask_book_prices), 1)
        self.assertEqual(len(self.ex1._bid_book_prices), 1)
        self.assertEqual(len(self.ex1.order_history), 2)
        # marketable sell takes out 1 share
        q3_sell = {'order_id': 't3_1', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'sell',
                   'price': 0}
        self.ex1.process_order(q3_sell)
        self.assertEqual(len(self.ex1.order_history), 3)
        self.assertEqual(self.ex1._bid_book[50]['num_orders'], 1)
        self.assertEqual(self.ex1._bid_book[50]['size'], 2)
        self.assertTrue(self.ex1.traded)
        # marketable buy takes out 1 share
        q3_buy = {'order_id': 't3_2', 'timestamp': 5, 'type': 'add', 'quantity': 1, 'side': 'buy',
                  'price': 10000}
        self.ex1.process_order(q3_buy)
        self.assertEqual(len(self.ex1.order_history), 4)
        self.assertEqual(self.ex1._ask_book[52]['num_orders'], 1)
        self.assertEqual(self.ex1._ask_book[52]['size'], 2)
        self.assertTrue(self.ex1.traded)
        # add/cancel buy order
        q4_buy = {'order_id': 't4_1', 'timestamp': 10, 'type': 'add', 'quantity': 1, 'side': 'buy',
                  'price': 48}
        self.ex1.process_order(q4_buy)
        self.assertEqual(len(self.ex1.order_history), 5)
        self.assertEqual(len(self.ex1._bid_book_prices), 2)
        self.assertEqual(self.ex1._bid_book[48]['num_orders'], 1)
        self.assertEqual(self.ex1._bid_book[48]['size'], 1)
        self.assertFalse(self.ex1.traded)
        q4_cancel1 = {'order_id': 't4_1', 'timestamp': 10, 'type': 'cancel', 'quantity': 1, 'side': 'buy',
                     'price': 48}
        self.ex1.process_order(q4_cancel1)
        self.assertEqual(len(self.ex1.order_history), 6)
        self.assertEqual(len(self.ex1._bid_book_prices), 1)
        self.assertFalse(self.ex1.traded)
        # add/cancel sell order
        q4_sell = {'order_id': 't4_2', 'timestamp': 10, 'type': 'add', 'quantity': 1, 'side': 'sell',
                  'price': 54}
        self.ex1.process_order(q4_sell)
        self.assertEqual(len(self.ex1.order_history), 7)
        self.assertEqual(len(self.ex1._ask_book_prices), 2)
        self.assertEqual(self.ex1._ask_book[54]['num_orders'], 1)
        self.assertEqual(self.ex1._ask_book[54]['size'], 1)
        self.assertFalse(self.ex1.traded)
        q4_cancel2 = {'order_id': 't4_2', 'timestamp': 10, 'type': 'cancel', 'quantity': 1, 'side': 'sell',
                     'price': 54}
        self.ex1.process_order(q4_cancel2)
        self.assertEqual(len(self.ex1.order_history), 8)
        self.assertEqual(len(self.ex1._ask_book_prices), 1)
        self.assertFalse(self.ex1.traded)
        # add/modify buy order
        q5_buy = {'order_id': 't5_1', 'timestamp': 10, 'type': 'add', 'quantity': 5, 'side': 'buy',
                  'price': 48}
        self.ex1.process_order(q5_buy)
        self.assertEqual(len(self.ex1.order_history), 9)
        self.assertEqual(len(self.ex1._bid_book_prices), 2)
        self.assertEqual(self.ex1._bid_book[48]['num_orders'], 1)
        self.assertEqual(self.ex1._bid_book[48]['size'], 5)
        q5_modify1 = {'order_id': 't5_1', 'timestamp': 10, 'type': 'modify', 'quantity': 2, 'side': 'buy',
                     'price': 48}
        self.ex1.process_order(q5_modify1)
        self.assertEqual(len(self.ex1.order_history), 10)
        self.assertEqual(len(self.ex1._bid_book_prices), 2)
        self.assertEqual(self.ex1._bid_book[48]['size'], 3)
        self.assertEqual(self.ex1._bid_book[48]['orders']['t5_1']['quantity'], 3)
        self.assertEqual(len(self.ex1.confirm_modify_collector), 1)
        self.assertFalse(self.ex1.traded)
        # add/modify sell order
        q5_sell = {'order_id': 't5_1', 'timestamp': 10, 'type': 'add', 'quantity': 5, 'side': 'sell',
                  'price': 54}
        self.ex1.process_order(q5_sell)
        self.assertEqual(len(self.ex1.order_history), 11)
        self.assertEqual(len(self.ex1._ask_book_prices), 2)
        self.assertEqual(self.ex1._ask_book[54]['num_orders'], 1)
        self.assertEqual(self.ex1._ask_book[54]['size'], 5)
        q5_modify2 = {'order_id': 't5_1', 'timestamp': 10, 'type': 'modify', 'quantity': 2, 'side': 'sell',
                     'price': 54}
        self.ex1.process_order(q5_modify2)
        self.assertEqual(len(self.ex1.order_history), 12)
        self.assertEqual(len(self.ex1._ask_book_prices), 2)
        self.assertEqual(self.ex1._ask_book[54]['size'], 3)
        self.assertEqual(self.ex1._ask_book[54]['orders']['t5_1']['quantity'], 3)
        self.assertEqual(len(self.ex1.confirm_modify_collector), 1)
        self.assertFalse(self.ex1.traded)

    def test_match_trade_sell(self):
        '''
        An incoming order can:
        1. take out part of an order,
        2. take out an entire price level,
        3. if priced, take out a price level and make a new inside market.
        '''
        # seed order book
        self.ex1.add_order_to_book(self.q1_buy)
        self.ex1.add_order_to_book(self.q1_sell)
        # process new orders
        self.ex1.process_order(self.q2_buy)
        self.ex1.process_order(self.q2_sell)
        self.ex1.process_order(self.q3_buy)
        self.ex1.process_order(self.q3_sell)
        self.ex1.process_order(self.q4_buy)
        self.ex1.process_order(self.q4_sell)
        # The book: bids: 2@50, 3@49, 3@47 ; asks: 2@52, 3@53, 3@55
        self.assertEqual(self.ex1._bid_book[47]['size'], 3)
        self.assertEqual(self.ex1._bid_book[49]['size'], 3)
        self.assertEqual(self.ex1._bid_book[50]['size'], 2)
        self.assertEqual(self.ex1._ask_book[52]['size'], 2)
        self.assertEqual(self.ex1._ask_book[53]['size'], 3)
        self.assertEqual(self.ex1._ask_book[55]['size'], 3)
        #self.assertFalse(self.ex1.sip_collector)
        # market sell order takes out part of first best bid
        q1 = {'order_id': 't100_1', 'timestamp': 10, 'type': 'add', 'quantity': 1, 'side': 'sell',
              'price': 0}
        self.ex1.process_order(q1)
        self.assertEqual(self.ex1._bid_book[50]['size'], 1)
        self.assertTrue(50 in self.ex1._bid_book_prices)
        self.assertEqual(self.ex1._bid_book[49]['size'], 3)
        self.assertEqual(self.ex1._bid_book[47]['size'], 3)
        self.assertEqual(self.ex1._bid_book[50]['orders'][self.ex1._bid_book[50]['order_ids'][0]]['quantity'], 1)
        #self.assertEqual(len(self.ex1.sip_collector), 1)
        # market sell order takes out remainder first best bid and all of the next level
        self.assertEqual(len(self.ex1._bid_book_prices), 3)
        q2 = {'order_id': 't100_2', 'timestamp': 11, 'type': 'add', 'quantity': 4, 'side': 'sell',
              'price': 0}
        self.ex1.process_order(q2)
        self.assertEqual(len(self.ex1._bid_book_prices), 1)
        self.assertFalse(50 in self.ex1._bid_book_prices)
        self.assertFalse(49 in self.ex1._bid_book_prices)
        self.assertTrue(47 in self.ex1._bid_book_prices)
        #self.assertEqual(len(self.ex1.sip_collector), 3)
        # make new market
        q3 = {'order_id': 't101_1', 'timestamp': 12, 'type': 'add', 'quantity': 2, 'side': 'buy',
              'price': 48}
        q4 = {'order_id': 't102_1', 'timestamp': 13, 'type': 'add', 'quantity': 3, 'side': 'sell',
              'price': 48}
        self.ex1.process_order(q3)
        self.assertEqual(len(self.ex1._bid_book_prices), 2)
        self.assertTrue(48 in self.ex1._bid_book_prices)
        self.assertTrue(47 in self.ex1._bid_book_prices)
        self.assertEqual(self.ex1._bid_book_prices[-1], 48)
        self.assertEqual(self.ex1._bid_book_prices[-2], 47)
        # sip_collector does not reset until new trade at new time
        #self.assertEqual(len(self.ex1.sip_collector), 3)
        self.ex1.process_order(q4)
        self.assertEqual(len(self.ex1._bid_book_prices), 1)
        self.assertFalse(48 in self.ex1._bid_book_prices)
        self.assertTrue(47 in self.ex1._bid_book_prices)
        self.assertEqual(len(self.ex1._ask_book_prices), 4)
        self.assertTrue(48 in self.ex1._ask_book_prices)
        self.assertEqual(self.ex1._ask_book_prices[0], 48)
        self.assertEqual(self.ex1._bid_book_prices[-1], 47)
        #self.assertEqual(len(self.ex1.sip_collector), 1)
        
    def test_match_trade_buy(self):
        '''
        An incoming order can:
        1. take out part of an order,
        2. take out an entire price level,
        3. if priced, take out a price level and make a new inside market.
        '''
        # seed order book
        self.ex1.add_order_to_book(self.q1_buy)
        self.ex1.add_order_to_book(self.q1_sell)
        # process new orders
        self.ex1.process_order(self.q2_buy)
        self.ex1.process_order(self.q2_sell)
        self.ex1.process_order(self.q3_buy)
        self.ex1.process_order(self.q3_sell)
        self.ex1.process_order(self.q4_buy)
        self.ex1.process_order(self.q4_sell)
        # The book: bids: 2@50, 3@49, 3@47 ; asks: 2@52, 3@53, 3@55
        self.assertEqual(self.ex1._bid_book[47]['size'], 3)
        self.assertEqual(self.ex1._bid_book[49]['size'], 3)
        self.assertEqual(self.ex1._bid_book[50]['size'], 2)
        self.assertEqual(self.ex1._ask_book[52]['size'], 2)
        self.assertEqual(self.ex1._ask_book[53]['size'], 3)
        self.assertEqual(self.ex1._ask_book[55]['size'], 3)
        # market buy order takes out part of first best ask
        q1 = {'order_id': 't100_1', 'timestamp': 10, 'type': 'add', 'quantity': 1, 'side': 'buy',
              'price': 100000}
        self.ex1.process_order(q1)
        self.assertEqual(self.ex1._ask_book[52]['size'], 1)
        self.assertTrue(52 in self.ex1._ask_book_prices)
        self.assertEqual(self.ex1._ask_book[53]['size'], 3)
        self.assertEqual(self.ex1._ask_book[55]['size'], 3)
        self.assertEqual(self.ex1._ask_book[52]['orders'][self.ex1._ask_book[52]['order_ids'][0]]['quantity'], 1)
        # market buy order takes out remainder first best ask and all of the next level
        self.assertEqual(len(self.ex1._ask_book_prices), 3)
        q2 = {'order_id': 't100_2', 'timestamp': 11, 'type': 'add', 'quantity': 4, 'side': 'buy',
              'price': 100000}
        self.ex1.process_order(q2)
        self.assertEqual(len(self.ex1._ask_book_prices), 1)
        self.assertFalse(52 in self.ex1._ask_book_prices)
        self.assertFalse(53 in self.ex1._ask_book_prices)
        self.assertTrue(55 in self.ex1._ask_book_prices)
        # make new market
        q3 = {'order_id': 't101_1', 'timestamp': 12, 'type': 'add', 'quantity': 2, 'side': 'sell',
              'price': 54}
        q4 = {'order_id': 't102_1', 'timestamp': 13, 'type': 'add', 'quantity': 3, 'side': 'buy',
              'price': 54}
        self.ex1.process_order(q3)
        self.assertEqual(len(self.ex1._ask_book_prices), 2)
        self.assertTrue(55 in self.ex1._ask_book_prices)
        self.assertTrue(54 in self.ex1._ask_book_prices)
        self.assertEqual(self.ex1._ask_book_prices[0], 54)
        self.assertEqual(self.ex1._ask_book_prices[1], 55)
        self.ex1.process_order(q4)
        self.assertEqual(len(self.ex1._ask_book_prices), 1)
        self.assertFalse(54 in self.ex1._ask_book_prices)
        self.assertTrue(55 in self.ex1._ask_book_prices)
        self.assertEqual(len(self.ex1._bid_book_prices), 4)
        self.assertTrue(54 in self.ex1._bid_book_prices)
        self.assertEqual(self.ex1._ask_book_prices[0], 55)
        self.assertEqual(self.ex1._bid_book_prices[-1], 54)
        
    def test_report_top_of_book(self):
        '''
        Testing for computing of lagged averages
        '''
        self.q0_buy = {'order_id': 't1_0', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'buy',
                       'price': 50}
        self.q1_buy = {'order_id': 't1_1', 'timestamp': 2, 'type': 'add', 'quantity': 1, 'side': 'buy',
                       'price': 50}
        self.q2_buy = {'order_id': 't1_2', 'timestamp': 3, 'type': 'add', 'quantity': 1, 'side': 'buy',
                       'price': 50}
        self.q3_buy = {'order_id': 't10_1', 'timestamp': 4, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 49}
        self.q4_buy = {'order_id': 't11_1', 'timestamp': 5, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 47}
        self.q5_buy = {'order_id': 't12_1', 'timestamp': 6, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 47}
        self.q6_buy = {'order_id': 't13_1', 'timestamp': 7, 'type': 'add', 'quantity': 3, 'side': 'buy',
                       'price': 51}
        self.q0_sell = {'order_id': 't1_5', 'timestamp': 1, 'type': 'add', 'quantity': 1, 'side': 'sell',
                        'price': 52}
        self.q1_sell = {'order_id': 't1_3', 'timestamp': 2, 'type': 'add', 'quantity': 1, 'side': 'sell',
                        'price': 52}
        self.q2_sell = {'order_id': 't1_4', 'timestamp': 3, 'type': 'add', 'quantity': 1, 'side': 'sell',
                        'price': 52}
        self.q3_sell = {'order_id': 't10_2', 'timestamp': 4, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 53}
        self.q4_sell = {'order_id': 't11_2', 'timestamp': 5, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 55}
        self.q5_sell = {'order_id': 't12_2', 'timestamp': 6, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 53}
        self.q6_sell = {'order_id': 't13_2', 'timestamp': 7, 'type': 'add', 'quantity': 3, 'side': 'sell',
                        'price': 55}
        
        for j, orders in enumerate(zip([self.q0_buy, self.q1_buy, self.q2_buy, self.q3_buy, self.q4_buy, self.q5_buy],
                                       [self.q0_sell, self.q1_sell, self.q2_sell, self.q3_sell, self.q4_sell, self.q5_sell])):
            buy, sell = orders
            self.ex1.add_order_to_book(buy)
            self.ex1.add_order_to_book(sell)
            self.ex1.report_top_of_book(j+1)
        tob_check_pre = {'timestamp': 6, 'best_bid': 50, 'best_ask': 52, 'bid_size': 3, 'ask_size': 3, 'lag_spread': 2.0,
                        'lag_bid_depth': 2.4, 'lag_ask_depth': 2.4}
        self.assertDictEqual(self.ex1._sip_collector[-1], tob_check_pre)
        #print(self.ex1._sip_collector[-1])
        
    def test_market_collapse(self):
        '''
        At setup(), there is 8 total bid size and 8 total ask size
        A trade for 8 or more should collapse the market
        '''
        print('Market Collapse Tests to stdout:\n')
        # seed order book
        self.ex1.add_order_to_book(self.q1_buy)
        self.ex1.add_order_to_book(self.q1_sell)
        # process new orders
        self.ex1.process_order(self.q2_buy)
        self.ex1.process_order(self.q2_sell)
        self.ex1.process_order(self.q3_buy)
        self.ex1.process_order(self.q3_sell)
        self.ex1.process_order(self.q4_buy)
        self.ex1.process_order(self.q4_sell)
        # The book: bids: 2@50, 3@49, 3@47 ; asks: 2@52, 3@53, 3@55
        # market buy order takes out part of the asks: no collapse
        q1 = {'order_id': 't100_1', 'timestamp': 10, 'type': 'add', 'quantity': 4, 'side': 'buy',
              'price': 100000}
        self.ex1.process_order(q1)
        # next market buy order takes out the asks: market collapse
        q2 = {'order_id': 't100_2', 'timestamp': 10, 'type': 'add', 'quantity': 5, 'side': 'buy',
              'price': 100000}
        self.ex1.process_order(q2)
        # market sell order takes out part of the bids: no collapse
        q3 = {'order_id': 't100_3', 'timestamp': 10, 'type': 'add', 'quantity': 4, 'side': 'sell',
              'price': 0}
        self.ex1.process_order(q3)
        # next market sell order takes out the asks: market collapse
        q4 = {'order_id': 't100_4', 'timestamp': 10, 'type': 'add', 'quantity': 5, 'side': 'sell',
              'price': 0}
        self.ex1.process_order(q4)
        
