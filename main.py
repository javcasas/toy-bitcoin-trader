import requests
import json
import time
from datetime import datetime
import pickle
import os

class MovingAverage(object):
    def __init__(self, npoints):
        self.npoints = npoints
        self.points = []

    def add_point(self, value):
        self.points = [value] + self.points
        self.points = self.points[:self.npoints]

    def average(self):
        return sum(self.points) / len(self.points)


def main():
    logfile = open("data.txt", "a")
    wallet = {}
    _20min_ave = MovingAverage(20)
    _200min_ave = MovingAverage(200)
    if os.path.isfile("wallet.pickle"):
        wallet = pickle.load(file("wallet.pickle"))
    else:
        wallet['btc'] = 1.0
        wallet['usd'] = 0.0
    try:
        while True:
            try:
                r = requests.get('https://blockchain.info/ticker').text
                data = json.loads(r)
                val = float(data['USD']['last'])
                logfile.write("%s\n" % datetime.now().isoformat())
                logfile.write("%s\n\n" % r.encode("ascii", "ignore"))
            except Exception, e:
                print e
                time.sleep(0.5)
                continue
            _20min_ave.add_point(val)
            _200min_ave.add_point(val)
            print
            print
            print "%s" % datetime.now().isoformat()
            print "20: {}, 200:{}".format(_20min_ave.average(), _200min_ave.average())
            print "USD: {}, BTC:{}".format(wallet['usd'], wallet['btc'])
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

            time.sleep(60)
    finally:
        print "Final status:"
        print "USD: {}, BTC:{}".format(wallet['usd'], wallet['btc'])
        pickle.dump(wallet, file("wallet.pickle", "w"))
        logfile.close()

if __name__ == "__main__":
    main()
