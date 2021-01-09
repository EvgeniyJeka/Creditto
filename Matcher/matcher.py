


#? On start - get all Offers and Bids from SQL DB / Kafka (from offset 0) ?
from models import Offer, Bid


class Matcher(object):

    pool = {}


    def add_offer(self, offer: Offer):

        # Move this gathering action to another method. Gather offers with provided status
        existing_offers_ids = [x.id for x in self.pool.keys()]

        if offer.id not in existing_offers_ids:
            self.pool[offer] = []

        print(self.pool)

    def add_bid(self, bid: Bid):
        pass