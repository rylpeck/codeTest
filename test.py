import queue
import threading
import random
import time

class Order:
    def __init__(self, order_type, ticker, quantity, price):
        self.order_type = order_type  #sell/buy
        self.ticker = ticker #name of ticker
        self.quantity = quantity #quanity
        self.price = price  #price

class OrderBook:
    def __init__(self):
        self.buy_orders = queue.SimpleQueue()  #queue is simple, and has multi producer, multi consumer. works great for threading
        self.sell_orders = queue.SimpleQueue()  

    def add_order(self, order_type, ticker, quantity, price):
        order = Order(order_type, ticker, quantity, price)
        if order_type == "Buy":
            self.buy_orders.put(order) #ququ
        else:
            self.sell_orders.put(order)  
        print(f"Added {order_type} order: {quantity} shares of {ticker} at ${price}")

    def match_orders(self):
        temp_buy = []  
        temp_sell = [] 

        #attempt to not use a lock, just goes and changes it. I think a lock would make sense here still, due to how stocks can work
        while not self.buy_orders.empty() and not self.sell_orders.empty():
            buy_order = self.buy_orders.get()  
            sell_order = self.sell_orders.get() 

            if buy_order.price >= sell_order.price:
                matched_qty = min(buy_order.quantity, sell_order.quantity)
                print(f"Matched {matched_qty} shares of {buy_order.ticker} at ${sell_order.price}")

                buy_order.quantity -= matched_qty
                sell_order.quantity -= matched_qty

            if buy_order.quantity > 0:
                temp_buy.append(buy_order) 
            if sell_order.quantity > 0:
                temp_sell.append(sell_order) 

        #inserts them back in
        for order in temp_buy:
            self.buy_orders.put(order)
        for order in temp_sell:
            self.sell_orders.put(order)

#stops it
stop_event = threading.Event()


#stops after 5 seconds, else it just kinda runs forever
def random_order_simulation(order_book, duration=5):
    start_time = time.time()
    tickers = [f"T{str(i).zfill(3)}" for i in range(0, 1024)] #random tickers, 1024 of em, range is neat

    while not stop_event.is_set() and time.time() - start_time < duration:
        order_type = random.choice(["Buy", "Sell"])
        ticker = random.choice(tickers)
        quantity = random.randint(1, 100)
        price = round(random.uniform(10, 500), 2)

        order_book.add_order(order_type, ticker, quantity, price)
        print(f"Added {order_type} order: {quantity} shares of {ticker} at ${price}")

        order_book.match_orders()
        time.sleep(random.uniform(0.1, 0.5)) #sleep for a bit, can go crazy fast though


order_book = OrderBook()
threads = [threading.Thread(target=random_order_simulation, args=(order_book, 5)) for _ in range(3)]  # timer to only run for 5 seconds


for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
