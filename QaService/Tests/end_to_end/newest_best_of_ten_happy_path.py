import time
from credittomodels import Offer
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
test_bid_owner_6 = 278
test_bid_owner_7 = 390
test_bid_owner_8 = 920
test_bid_owner_9 = 911
test_bid_owner_10 = 883


test_bid_interest_1 = 0.046
test_bid_interest_2 = 0.045
test_bid_interest_3 = 0.044
test_bid_interest_4 = 0.037
test_bid_interest_5 = 0.037
test_bid_interest_6 = 0.042
test_bid_interest_7 = 0.048
test_bid_interest_8 = 0.039
test_bid_interest_9 = 0.038
test_bid_interest_10 = 0.041


@pytest.mark.incremental
class TestBestOfTen(object):

    offer_id = 0
    matching_bid_id = 0

    bid_owners = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5,
                  test_bid_owner_6, test_bid_owner_7, test_bid_owner_8, test_bid_owner_9, test_bid_owner_10]

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5, test_bid_interest_6, test_bid_interest_7,
                         test_bid_interest_8, test_bid_interest_9, test_bid_interest_10]

    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    def test_placing_offer(self, set_matching_logic):
        response = postman.gateway_requests.place_offer(test_offer_owner_1, test_sum,
                                                        test_duration, test_offer_interest_low, 0)

        TestBestOfTen.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        self.offer_id = response['offer_id']

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_offer_in_sql(self):
        offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
        logging.info(offer_sql)
        assert offer_sql['id'] == self.offer_id, "Offer Placement error - placed offer wasn't saved to DB"

        logging.info(f"----------------------- Offer ID validation in SQL - step passed ------------------------------\n")

    def test_placing_first_bids(self):

        for i in range(0, 5):
            response = postman.gateway_requests.\
                place_bid(self.bid_owners[i], self.bid_interest_list[i], self.offer_id, 0)
            logging.info(response)

            # The bid that is expected to create a match with the offer
            if i == 4:
                TestBestOfTen.matching_bid_id = response['bid_id']

            assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
            assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
            assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")

    def test_verify_no_match_yet(self):
        offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
        logging.info(offer_sql)
        assert offer_sql['status'] == Offer.OfferStatuses.OPEN.value, "Offer was matched before 3 bids were placed"
        assert offer_sql['final_interest'] == '-1.0'

        logging.info(f"----------------------- No Match On Fifth Bid verification - step passed ----------"
                     f"------------------------\n")

    def test_placing_final_bids(self):
        for i in range(5, 10):
            response = postman.gateway_requests. \
                place_bid(self.bid_owners[i], self.bid_interest_list[i], self.offer_id, 0)
            logging.info(response)

            assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
            assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
            assert isinstance(response['bid_id'], int), "BID Placement error - invalid BID ID in response "

        logging.info(f"----------------------- Final Bid Placement - step passed ----------------------------------\n")

    def test_updated_offer_after_match(self):
        time.sleep(5)
        offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
        logging.info(offer_sql)

        assert offer_sql['status'] == Offer.OfferStatuses.MATCHED.value,\
            "Offer status in SQL wasn't updated after match"
        assert offer_sql['final_interest'] == str(test_bid_interest_5), \
            "Final interest in SQL wasn't updated after match"

        logging.info(f"----------------------- Verifying Offer Data Updated in SQL - step passed --------------"
                     f"--------------------\n")

    def test_match_data_verified(self):
        match_sql = reporter.get_match_by_offer_id(self.offer_id)[0]
        logging.info(match_sql)

        assert match_sql['bid_id'] == TestBestOfTen.matching_bid_id
        assert match_sql['bid_owner_id'] == test_bid_owner_5
        assert match_sql['final_interest'] == str(test_bid_interest_5)

        logging.info(f"----------------------- Verifying Match Data in SQL - step passed --------------------"
                     f"--------------\n")