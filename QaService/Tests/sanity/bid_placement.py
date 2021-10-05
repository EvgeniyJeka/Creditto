import time
from credittomodels import Offer
from credittomodels import Bid
import pytest
from decimal import Decimal
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

test_token = '1Aa@<>12'


@pytest.mark.incremental
class TestBidSanity(object):
    """
    In those tests we verify that:
    1. Bid can be successfully placed on existing OPEN offer
    2. API method 'get_my_bids' (get bids by owner) provides valid data on placed Bid
    3. Placed Bid has status PLACED (until matched, cancelled or expired)
    """

    offer_id = 0
    bid_id = 0

    bid_owners = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5,
                  test_bid_owner_6, test_bid_owner_7, test_bid_owner_8, test_bid_owner_9, test_bid_owner_10]

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5, test_bid_interest_6, test_bid_interest_7,
                         test_bid_interest_8, test_bid_interest_9, test_bid_interest_10]

    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    def test_placing_offer(self, set_matching_logic):
        response = postman.gateway_requests.place_offer(test_offer_owner_1, test_sum,
                                                        test_duration, test_offer_interest_low, 0)

        TestBidSanity.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        self.offer_id = response['offer_id']

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_placing_bid(self):

        response = postman.gateway_requests.\
            place_bid(self.bid_owners[0], self.bid_interest_list[0], self.offer_id, 0)
        logging.info(response)

        TestBidSanity.bid_id = response['bid_id']

        assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
        assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
        assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")


    def test_bids_by_owner(self):

        response = postman.gateway_requests.get_bids_by_owner(self.bid_owners[0], test_token)
        logging.info(response)

        assert isinstance(response, list), "Invalid data type in API response"
        assert len(response) > 0, "Placed offer wasn't returned in API response "
        assert isinstance(response[0], dict), "Invalid data type in API response"

        for bid in response:
            if bid['id'] == TestBidSanity.bid_id:
                print(bid)
                assert bid['owner_id'] == test_bid_owner_1
                assert bid['bid_interest'] == str(self.bid_interest_list[0])
                assert bid['target_offer_id'] == TestBidSanity.offer_id
                assert bid['status'] == Bid.BidStatuses.PLACED.value

        logging.info(f"----------------------- Get All Bids By Owner API method - data verified ---------"
                     f"-------------------------\n")