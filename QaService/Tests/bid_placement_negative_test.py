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

test_bid_interest_1 = 0.046
test_bid_interest_2 = 0.045
test_bid_interest_3 = 0.044
test_bid_interest_4 = 0.037
test_bid_interest_5 = 0.037


@pytest.mark.incremental
class TestBidPlacement(object):

    offer_id = 0
    matching_bid_id = 0

    bid_owners = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5]

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5]

    @pytest.mark.parametrize('set_matching_logic', [[1]], indirect=True)
    @pytest.mark.parametrize('offer_placed', [[test_bid_owner_1, test_sum, test_duration, test_offer_interest_low]],
                             indirect=True)
    def test_no_bid_on_non_existing_offer(self, set_matching_logic, offer_placed):
        TestBidPlacement.offer_id = offer_placed

        response = postman.gateway_requests. \
            place_bid(self.bid_owners[0], self.bid_interest_list[0], self.offer_id + 1, 0)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f"Offer {self.offer_id + 1} does not exist"

        logging.info(f"----------------------- Invalid offer ID in BID - step passed "
                     f"----------------------------------\n")

    def test_no_bid_interest_above_suggested(self):

        response = postman.gateway_requests. \
            place_bid(self.bid_owners[0], test_offer_interest_low * 2, self.offer_id, 0)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f'Interest rate above offer interest rate {test_offer_interest_low}'

        logging.info(f"----------------------- BID Interest Greater Then Offer Interest - step passed "
                     f"----------------------------------\n")

    def test_matched_bid_cant_be_matched(self):

        # Placing 5 bids so the offer will become matched
        for i in range(0, 5):
            response = postman.gateway_requests. \
                place_bid(self.bid_owners[i], self.bid_interest_list[i], self.offer_id, 0)
            logging.info(response)

        response = postman.gateway_requests. \
            place_bid(self.bid_owners[i], self.bid_interest_list[i], self.offer_id, 0)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f"Bids can't be placed on offers in status {Offer.OfferStatuses.MATCHED.value}"

        logging.info(f"----------------------- BID Can't Be Placed On Matched Offer' - step passed "
                     f"----------------------------------\n")