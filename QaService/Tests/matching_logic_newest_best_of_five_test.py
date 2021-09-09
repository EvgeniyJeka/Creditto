import pytest
from Requests.postman import Postman
from Tools import reporter
import logging

logging.basicConfig(level=logging.INFO)

postman = Postman()
reporter = reporter.Reporter()


test_offer_owner_1 = 1024
test_offer_interest_low = 0.05
test_sum = 20000
test_duration = 24

test_bid_owner_1 = 393
test_bid_owner_2 = 582
test_bid_owner_3 = 781
test_bid_owner_4 = 343
test_bid_owner_5 = 216

test_bid_interest_1 = 0.046
test_bid_interest_2 = 0.045
test_bid_interest_3 = 0.044
test_bid_interest_4 = 0.037
test_bid_interest_5 = 0.037

class TestBestOfFive(object):

    offer_id = 0
    matching_bid_id = 0

    bid_owners = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5]

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5]

    def test_placing_offer(self):
        response = postman.gateway_requests.place_offer(test_offer_owner_1, test_sum,
                                                        test_duration, test_offer_interest_low, 0)

        TestBestOfFive.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        self.offer_id = response['offer_id']

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------")

    def test_offer_in_sql(self):
        offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
        logging.info(offer_sql)
        assert offer_sql['id'] == self.offer_id, "Offer Placement error - placed offer wasn't saved to DB"

        logging.info(f"----------------------- Offer ID validation in SQL - step passed ------------------------------")

    def test_placing_first_bids(self):

        for i in range(0, 3):
            response = postman.gateway_requests.\
                place_bid(self.bid_owners[i], self.bid_interest_list[i], self.offer_id, 0)
            logging.info(response)

            assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
            assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
            assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------")

    def test_verify_no_match_yet(self):
        pass

    def test_placing_final_bids(self):
        pass


    def test_verifying_match(self):
        pass
