import datetime as dt
import time
import random
import logging

from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')
    
STOCK_A = 'PHILIPS_A'
STOCK_B = 'PHILIPS_B'

stock_order_bookA = exchange.get_last_price_book(STOCK_A)
stock_order_bookB = exchange.get_last_price_book(STOCK_B)

def getDelta(v):
    positions = exchange.get_positions()
    
    total = v 
    
    for i in positions:
        total += positions[i]
    
    return total

def trade_(instrument_id, volume, side, position_limit=250, delta = 40):
    positions = exchange.get_positions()
    position_instrument = positions[instrument_id]
    
    for i in positions:
        print(positions[i])
    
    
    if side == 'bid':
        if(position_instrument + volume > position_limit):
            print("postion block")
        if(getDelta(volume) > delta):
            print("delat breach")
        return position_instrument + volume <= position_limit  #and (getDelta(volume) <= delta)
    elif side == 'ask':
        if(position_instrument + volume < -position_limit):
            print("postion block")
        if(getDelta(volume) < -delta):
            print("delat breach")
        
        return position_instrument - volume  >= -position_limit #and (getDelta(volume) >= -delta)
    else:
        raise Exception(f'''Invalid side provided: {side}, expecting 'bid' or 'ask'.''')

def get_spread(instrument_id):
    if(instrument_id == STOCK_A):
        return stock_order_bookA.asks[0].price - stock_order_bookA.bids[0].price
    
    if(instrument_id == STOCK_B):
        return stock_order_bookB.asks[0].price - stock_order_bookB.bids[0].price

#exchange.insert_order(STOCK_A, price=best_ask_priceA, volume=10, side='bid', order_type='limit')
#exchange.insert_order(STOCK_B, price=best_ask_priceB, volume=20, side='ask', order_type='ioc')

#positions = exchange.get_positions()
#for p in positions:
#    print(p, positions[p])
i = 0


def arbitrage_trade(buy_stock,sell_stock, buy_price,sell_price ,volume):
    
    action = 'bid'
    if(trade_(buy_stock,volume,action)):
        print("the volume is ", volume)
        exchange.insert_order(
        instrument_id=buy_stock,
        price=buy_price,
        volume=volume,
        side=action,
        order_type='ioc')
        print(f'''Inserting {action} for {buy_stock}: {volume:.0f} lot(s) at price {buy_price:.2f}.''')
        
        history = exchange.poll_new_trades(buy_stock)
        last_trade_volume = history[-1].volume
        print(last_trade_volume)
        if (last_trade_volume < volume):
            volume = last_trade_volume
        
        action = 'ask'
        print("the volume is ", volume)
        exchange.insert_order(
        instrument_id=sell_stock,
        price=sell_price,
        volume=volume,
        side=action,    
        order_type='ioc')
        print(f'''Inserting {action} for {sell_stock}: {volume:.0f} lot(s) at price {sell_price:.2f}.''')

                
def arbitrage_volume(buy_book,sell_book,buy_stock,sell_stock):
    
    summ = 0
    ask_index = 0
    bid_index = 0

##assuming liquid
    price_ask = buy_book.asks[ask_index].price
    price_bid = sell_book.bids[bid_index].price
    
    positions = exchange.get_positions()
    buy_position = positions[buy_stock]
    sell_position = positions[sell_stock]
    
    positions_limit = 250
    delta_limit = 10

    while (price_ask < price_bid and ask_index < len(buy_book.asks) and bid_index < len(sell_book.bids)):  ##and trade_(STOCK_A,summ,'bid')
        
        print("sum is", summ)
        
        
        ask_volume = buy_book.asks[ask_index].volume
        bid_volume = sell_book.bids[bid_index].volume
        price_ask = buy_book.asks[ask_index].price
        price_bid = sell_book.bids[bid_index].price
        
        
        if(ask_volume <= bid_volume):
            
            print("ASK VOLUME:", ask_volume)
            print("buy pos", buy_position)
            
            if(ask_volume >= positions_limit - buy_position):
                ask_volume = 30
                
                # print("return  ",delta_limit)
                # return (delta_limit, price_ask, price_bid)
            
            summ += ask_volume
            bid_volume -= ask_volume
            buy_position += ask_volume
            ask_index += 1
            if (bid_volume == 0):
                bid_index += 1
            
        else:    
            print("bid VOLUME:",bid_volume)
            print("sell pos", sell_position)
            if(bid_volume >= positions_limit - sell_position):
                bid_volume = 30
                
                # print("return  ",delta_limit)
                # return (delta_limit, price_ask, price_bid)
            summ+= bid_volume
            ask_volume -= bid_volume
            sell_position += bid_volume
            
            bid_index += 1
            if (ask_volume == 0):
                ask_index += 1
                
    if (summ > positions_limit):
        return (delta_limit, price_ask, price_bid)
    
    return (summ, price_ask, price_bid)


while True:
    best_bid_priceA = 0
    best_bid_priceB = 0
    best_ask_priceA = 0
    best_ask_priceB = 0
    
    ask_volumeB = 0
    ask_volumeA = 0
    bid_volumeB = 0
    bid_volumeA = 0
    
    while True:
        try:
            stock_order_bookA = exchange.get_last_price_book(STOCK_A)
            stock_order_bookB = exchange.get_last_price_book(STOCK_B)
            best_bid_priceA = stock_order_bookA.bids[0].price
            best_bid_priceB = stock_order_bookB.bids[0].price
            best_ask_priceA = stock_order_bookA.asks[0].price
            best_ask_priceB = stock_order_bookB.asks[0].price
            
            for i in [best_ask_priceB,best_bid_priceA,best_ask_priceA,best_bid_priceB]:
                print(i)
            
            ask_volumeB = stock_order_bookB.asks[0].volume
            ask_volumeA = stock_order_bookA.asks[0].volume
            bid_volumeB = stock_order_bookB.bids[0].volume
            bid_volumeA = stock_order_bookA.bids[0].volume
            break
        except:
            print("books empty")
    
    #volume = 10
    #change volume to take variable amounts based on current position

    ##Arbitrage
    if (best_ask_priceB < best_bid_priceA):
        print("best ask B")
        
        (volume,best_ask_priceA,best_bid_priceB) = arbitrage_volume(stock_order_bookB,stock_order_bookA,STOCK_B,STOCK_A)
        if (volume != 0):
            print("volume is ", volume)
            
            arbitrage_trade(STOCK_B,STOCK_A,best_ask_priceA,best_bid_priceB,volume)
        
        
        # if(ask_volumeB < bid_volumeA):
            
        #     #calculate a volume
        #     #extract hedging voluming
            
        #     arbitrage_trade(STOCK_B,best_ask_priceB,volume,'bid')
        #     arbitrage_trade(STOCK_A,best_bid_priceA,volume,'ask')
                
        # else:
        #     arbitrage_trade(STOCK_A,best_bid_priceA,volume,'ask')
        #     arbitrage_trade(STOCK_B,best_ask_priceB,volume,'bid')
            
    if(best_ask_priceA < best_bid_priceB):
        print("best ask A")
        (volume,best_ask_priceA,best_bid_priceB) = arbitrage_volume(stock_order_bookA,stock_order_bookB,STOCK_A,STOCK_B)
        if volume != 0:
            arbitrage_trade(STOCK_A,STOCK_B,best_ask_priceA,best_bid_priceB,volume)
            
        # if(ask_volumeA < bid_volumeB):
        #     arbitrage_trade(STOCK_A,best_ask_priceA,volume,'bid')
        #     arbitrage_trade(STOCK_B,best_bid_priceB,volume,'ask')
            
        # else:
        #     arbitrage_trade(STOCK_B,best_ask_priceB,volume,'ask')
        #     arbitrage_trade(STOCK_A,best_bid_priceA,volume,'bid')

    time.sleep(0.04)