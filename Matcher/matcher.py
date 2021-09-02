#? On start - get all Offers and Bids from SQL DB / Kafka (from offset 0) ?
from datetime import datetime
from decimal import Decimal
import simplejson

from credittomodels import statuses
from sql_recovery_reader import SqlRecoveryReader
from local_config import Config, MatchingAlgorithm
from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from producer_from_matcher import ProducerFromMatcher
from best_of_five_oldest import BestOfFiveOldest
import logging

producer = ProducerFromMatcher()


class Matcher(object):

    pool = {}

    def __init__(self):

        logging.info("MATCHER: Creating SQL RECOVERY READER instance")
        logging.info("MATCHER: Using the created instance to perform full recovery from SQL on start")
        read_sql_recovery = SqlRecoveryReader()
        self.pool = read_sql_recovery.recover_offers_bids_sql()
        self.matched_offer = None

    def add_offer(self, offer: Offer):
        logging.info("MATCHER: Adding a new OFFER to the matching pool")

        # T.B.D. - add handling for incoming offer with status CANCELLED (default status is OPEN)
        if offer.id not in self.get_all_existing_offers_ids():
            self.pool[offer] = []

        print(self.pool)
        return True

    def add_bid(self, bid: Bid):
        logging.info("MATCHER: Adding a new BID to the matching pool")

        # Each time new Bid is added check MATCH CONDITION for given offer.
        # If fulfilled - change Offer status, produce a Match to 'matches' topic, change all related bids status

        # Verifying target offer exists in the system
        if bid.target_offer_id not in self.get_all_existing_offers_ids():
            logging.error(f"MATCHER: Bid with ID {bid.id} can't be accepted - "
                          f"target offer {bid.target_offer_id} doesn't exists")

        # Bid can be added only to existing and OPEN/PARTIALLY_MATCHED offer (not to MATCHED, EXPIRED, CANCELLED offer)
        for offer in self.pool.keys():
            if offer.id == bid.target_offer_id:
                logging.info(f"MATCHER: Adding bid {bid.id} - in progress. Targeted offer {offer.id} found.")

                if offer.status not in (statuses.OfferStatuses.OPEN.value, statuses.OfferStatuses.PARTIALLY_MATCHED.value):
                    logging.error(f"MATCHER: Adding bid {bid.id} - failed. Targeted offer {offer.id} is no longer available")

                self.pool[offer].append(bid)
                logging.info(f"MATCHER: Bid {bid.id} was successfully attached to offer {offer.id}.")
                print(self.pool)

                logging.info(f"MATCHER: Checking match criteria for offer {offer} ")
                is_match = self.check_match(offer, Config.SELECTED_MATCHING_ALGORITHM.value)

                # If Match object returned by 'is_match' it means that new bid addition has resulted in a match.
                # Newly created match must be sent to the 'matches' topic
                if isinstance(is_match, Match.Match):
                    self.matched_offer = offer
                    match_to_producer = simplejson.dumps(is_match.__dict__, use_decimal=True)

                    logging.info(match_to_producer)
                    logging.info("MATCHER: Using Producer instance to send the match to Kafka topic 'matches' ")
                    print(producer.produce_message(match_to_producer, 'matches'))

        # Removing offer that was matched (if there was a match) and all bids on it from the pool
        if self.matched_offer:
            self.pool.pop(self.matched_offer)
            self.matched_offer = None

    # Consider making a separate method for each matching algorithm
    def check_match(self, offer: Offer, match_algorithm: int):
        """
        # This method checks if match cretirea for provided offer is matched
        :param offer: Offer object
        :param match_algorithm: selected match algorithm ID, int
        :return: Match object on success
        """
        # Default match algorithm - Bid with the lowest interest is selected among 5 available bids.
        if match_algorithm == MatchingAlgorithm.BEST_OF_FIVE_LOWEST_INTEREST_OLDEST.value:
            bids_for_offer = self.pool[offer]

            # if len(bids_for_offer) < Config.MIN_BIDS_EXPECTED.value:
            #     logging.info(f"MATCHER: Not enough bids for offer {offer.id}, no match")
            #     return False

            return BestOfFiveOldest.find_best_bid(bids_for_offer, offer)

    def get_all_existing_offers_ids(self):
        """
        This method returns all available Offer ID's from Matcher object pool
        :return: list of ints
        """
        return [x.id for x in self.pool.keys()]


if __name__ == "__main__":
    matcher = Matcher()

    # second_offer = None
    #
    # for offer in matcher.pool.keys():
    #     if offer.id == 2:
    #         second_offer = offer
    #
    # print(second_offer)
    # print(matcher.pool[second_offer])
    # print(matcher.check_match(second_offer, 1))