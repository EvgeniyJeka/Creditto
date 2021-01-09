
#? On start - get all Offers and Bids from SQL DB / Kafka (from offset 0) ?
from Matcher.sql_recovery_reader import SqlRecoveryReader
from models.Offer import Offer
from models.Bid import Bid


class Matcher(object):

    pool = {}

    def __init__(self):

        # Creating SQL RECOVERY READER instance
        # Using the created instance to perform full recovery from SQL on start
        read_sql_recovery = SqlRecoveryReader()
        self.pool = read_sql_recovery.recover_offers_bids_sql()

        

    def add_offer(self, offer: Offer):

        # Move this gathering action to another method. Gather offers with provided status
        existing_offers_ids = [x.id for x in self.pool.keys()]

        if offer.id not in existing_offers_ids:
            self.pool[offer] = []

        print(self.pool)

    def add_bid(self, bid: Bid):
        # Each time new Bid is added check MATCH CONDITION for given offer.
        # If fulfilled - change Offer status, produce a Match to 'matches' topic, change all related bids status
        pass

