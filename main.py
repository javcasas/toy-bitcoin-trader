import requests
import json
import time
from datetime import datetime

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
    _20min_ave = MovingAverage(20)
    _200min_ave = MovingAverage(200)
    btc = 1.0
    usd = 0.0
    try:
        while True:
            r = requests.get('https://blockchain.info/ticker').text
            data = json.loads(r)
            val = float(data['USD']['last'])
            _20min_ave.add_point(val)
            _200min_ave.add_point(val)
            print
            print
            print "%s" % datetime.now().isoformat()
            print "20: {}, 200:{}".format(_20min_ave.average(), _200min_ave.average())
            print "USD: {}, BTC:{}".format(usd, btc)
            if _20min_ave.average() > _200min_ave.average():
                # Up trend, buy BTC
                if usd > 0:
                    print "Buying BTC"
                    btc = usd / val
                    usd = 0.0
            elif _20min_ave.average() < _200min_ave.average():
                # down trend, sell BTC
                if btc > 0:
                    print "Selling BTC"
                    usd = btc * val
                    btc = 0.0

            time.sleep(60)
    finally:
        print "Initial status:"
        print "USD: {}, BTC:{}".format(0.0, 1.0)
        print "Final status:"
        print "USD: {}, BTC:{}".format(usd, btc)

if __name__ == "__main__":
    main()
