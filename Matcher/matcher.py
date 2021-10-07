#? On start - get all Offers and Bids from SQL DB / Kafka (from offset 0) ?

from credittomodels import statuses
from sql_recovery_reader import SqlRecoveryReader
from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from producer_from_matcher import ProducerFromMatcher
from best_of_five_oldest import BestOfFiveOldest
from best_of_ten_newest import BestOfTenNewest
import logging
from credittomodels import protobuf_handler


logging.basicConfig(level=logging.INFO)

producer = ProducerFromMatcher()


# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler

class Matcher(object):

    pool = {}

    def __init__(self):

        logging.info("MATCHER: Creating SQL RECOVERY READER instance")
        logging.info("MATCHER: Using the created instance to perform full recovery from SQL on start")
        self.read_sql_recovery = SqlRecoveryReader()
        self.pool = self.read_sql_recovery.recover_offers_bids_sql()
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
                logging.info(self.pool)

                logging.info(f"MATCHER: Checking match criteria for offer {offer} ")
                is_match = self.check_match(offer)

                # If Match object returned by 'is_match' it means that new bid addition has resulted in a match.
                # Newly created match must be sent to the 'matches' topic
                if isinstance(is_match, Match.Match):
                    self.matched_offer = offer

                    logging.info(is_match)

                    # Producing MATCH message to kafka (after it serialized to match proto message)
                    match_to_producer = proto_handler.serialize_match_to_proto(is_match)

                    match_record_headers = [("type", bytes('match', encoding='utf8'))]

                    logging.info(match_to_producer)
                    logging.info("MATCHER: Using Producer instance to send the match to Kafka topic 'matches' ")
                    producer.produce_message(match_to_producer, 'matches', match_record_headers)

        # Removing offer that was matched (if there was a match) and all bids on it from the pool
        if self.matched_offer:
            self.pool.pop(self.matched_offer)
            self.matched_offer = None

    def check_match(self, offer: Offer):
        """
        This method fetches the selected matching algorithm from SQL DB local_config and
        applies it to provided offer and all existing bids on that offer.
        If a match is created as a result of that application, 'Match' object is returned.
        Else the method returns 'False'.
        :param offer: Offer object
        :return: Match object on success
        """

        # Getting all available bids for given offer
        bids_for_offer = self.pool[offer]

        # Available matching methods
        available_matching_algorithms = [BestOfFiveOldest.find_best_bid, BestOfTenNewest.find_best_bid]

        # Fetching config from SQL
        matching_algorithm_config_sql = int(self.read_sql_recovery.fetch_config_from_db("matching_logic"))

        # Using the selected matching algorithm
        matching_algorithm = available_matching_algorithms[matching_algorithm_config_sql - 1]

        return matching_algorithm(bids_for_offer, offer)

    def get_all_existing_offers_ids(self):
        """
        This method returns all available Offer ID's from Matcher object pool
        :return: list of ints
        """
        return [x.id for x in self.pool.keys()]


if __name__ == "__main__":
    matcher = Matcher()

