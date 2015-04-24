import requests
import json
import time
from datetime import datetime
import pickle
import os


class MovingAverage(object):
    """
    Implements a Moving Average, of the specified points
    """
    def __init__(self, npoints):
        self.npoints = npoints
        self.points = []

    def add_point(self, value):
        self.points = [value] + self.points
        self.points = self.points[:self.npoints]

    def average(self):
        return sum(self.points) / len(self.points)


def get_btc_price():
    """
    Connects to blockchain.info, and returns the last BTC/USD quote
    """
    while True:
        try:
            r = requests.get('https://blockchain.info/ticker').text
            data = json.loads(r)
            val = float(data['USD']['last'])
            return val
        except Exception, e:
            print e
            time.sleep(0.5)


def wallet_status(wallet):
    """
    Returns a readable string for the specified wallet
    """
    return "Wallet: USD:{} BTC:{}".format(wallet['usd'], wallet['btc'])


def main(wallet_fn="wallet.pickle"):
    """
    Main function. Reads wallet and simulates trading
    """
    tick_time = 3  # 1 check every minute

    _20min_ave = MovingAverage(20)
    _200min_ave = MovingAverage(200)

    # Load/recreate wallet
    if os.path.isfile(wallet_fn):
        wallet = pickle.load(file(wallet_fn))
    else:
        # Start with 1BTC
        wallet = {}
        wallet['btc'] = 1.0
        wallet['usd'] = 0.0

    try:
        # Do forever, until Ctrl-C
        while True:
            val = get_btc_price()
            _20min_ave.add_point(val)
            _200min_ave.add_point(val)

            # Some logging
            print
            print "Timestamp:", datetime.now().isoformat()
            print "Averages:", "20:", _20min_ave.average(), "200:", _200min_ave.average()
            print wallet_status(wallet)

            # Simulate operation
            if _20min_ave.average() > _200min_ave.average():
                # Up trend, buy BTC
                if wallet['usd'] > 0:
                    print "Buying BTC"
                    wallet['btc'] = wallet['usd'] / val
                    wallet['usd'] = 0.0
            elif _20min_ave.average() < _200min_ave.average():
                # down trend, sell BTC
                if wallet['btc'] > 0:
                    print "Selling BTC"
                    wallet['usd'] = wallet['btc'] * val
                    wallet['btc'] = 0.0

            time.sleep(tick_time)
    finally:
        print "Final status:"
        print wallet_status(wallet)
        pickle.dump(wallet, file("wallet.pickle", "w"))

if __name__ == "__main__":
    main()
