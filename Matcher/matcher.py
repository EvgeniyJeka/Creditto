
#? On start - get all Offers and Bids from SQL DB / Kafka (from offset 0) ?
from decimal import Decimal

from Matcher.sql_recovery_reader import SqlRecoveryReader
from config import Config, MatchingAlgorithm
from models.Offer import Offer
from models.Bid import Bid
import logging


class Matcher(object):

    pool = {}

    def __init__(self):

        # Creating SQL RECOVERY READER instance
        # Using the created instance to perform full recovery from SQL on start
        read_sql_recovery = SqlRecoveryReader()
        self.pool = read_sql_recovery.recover_offers_bids_sql()



    def add_offer(self, offer: Offer):

        if offer.id not in self.get_all_existing_offers_ids():
            self.pool[offer] = []

        print(self.pool)
        return True

    def add_bid(self, bid: Bid):
        # Each time new Bid is added check MATCH CONDITION for given offer.
        # If fulfilled - change Offer status, produce a Match to 'matches' topic, change all related bids status

        # Verifying target offer exists in the system
        if bid.target_offer_id not in self.get_all_existing_offers_ids():
            logging.error(f"Bid with ID {bid.id} can't be accepted - target offer {bid.target_offer_id} doesn't exists")

        # Bid can be added only to existing and OPEN/PARTIALLY_MATCHED offer (not to MATCHED, EXPIRED, CANCELLED offer)
        for offer in self.pool.keys():
            if offer.id == bid.target_offer_id:
                logging.info(f"Adding bid {bid.id} - in progress. Targeted offer {offer.id} found.")

                if offer.status not in (1, 3):
                    logging.error(f" Adding bid {bid.id} - failed. Targeted offer {offer.id} is no longer available")

                self.pool[offer].append(bid)
                logging.info(f"Bid {bid.id} was successfully attached to offer {offer.id}.")
                print(self.pool)
                logging.info(f"Checking match criteria for offer {offer} ")

                is_match =  self.check_match(offer, Config.SELECTED_MATCHING_ALGORITHM.value)
                # if isinstance(is_match, match):
                #    produce_match(is_match)



    # This method checks if match cretirea for provided offer is matched
    def check_match(self, offer: Offer, match_algorithm: int):

        # Default match algorithm - Bid with the lowest interest is selected among 5 available bids.
        if match_algorithm == MatchingAlgorithm.BEST_OF_FIVE_LOWEST_INTEREST.value:
            bids_for_offer = self.pool[offer]

            if len(bids_for_offer) < Config.MIN_BIDS_EXPECTED.value:
                logging.info(f"Not enough bids for offer {offer.id}, no match")
                return False

            print([x.bid_interest for x in bids_for_offer])

            bids_for_offer.sort(key=lambda x: Decimal(x.bid_interest))

            print(f"MATCHED BID {bids_for_offer[0].id} WITH OFFER {offer.id}")




    def get_all_existing_offers_ids(self):
        return [x.id for x in self.pool.keys()]


if __name__=="__main__":
    matcher = Matcher()

    second_offer = None

    for offer in matcher.pool.keys():
        if offer.id == 2:
            second_offer = offer

    print(second_offer)
    print(matcher.pool[second_offer])
    print(matcher.check_match(second_offer, 1))