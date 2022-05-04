import time
from credittomodels import Offer
import pytest
import logging

try:
    from Requests  import postman
    from Tools import reporter

except ModuleNotFoundError:
    from ....Requests import postman
    from ....Tools import reporter


logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()


test_offer_interest_low = 0.05
test_sum = 20000
test_duration = 24

test_bid_interest_1 = 0.046
test_bid_interest_2 = 0.045
test_bid_interest_3 = 0.044
test_bid_interest_4 = 0.037
test_bid_interest_5 = 0.037


@pytest.mark.container
@pytest.mark.negative
@pytest.mark.incremental
class TestBidPlacement(object):
    """
        In those tests we verify that:
        1. Bid can't be placed on non-existing offer
        2. Bid interest can't be greater then target Offer interest
        3. Lender can place only ONE Bid on each Offer
        4. Bids can't be placed on an Offer that is already matched

        NOTE: Error message successful validation confirms that Gateway hasn't crashed and handled the invalid input
        # as expected.
        """

    offer_id = 0
    matching_bid_id = 0
    lender = None
    borrower = None

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5]

    @pytest.mark.parametrize('set_matching_logic', [[1]], indirect=True)
    @pytest.mark.parametrize('get_authorized_lenders', [[5]], indirect=True)
    def test_no_bid_on_non_existing_offer(self, set_matching_logic, get_authorized_lenders):
        TestBidPlacement.lender = get_authorized_lenders

        response = postman.gateway_requests. \
            place_bid(TestBidPlacement.lender[0].user_id, self.bid_interest_list[0],
                      self.offer_id + 1, 0, TestBidPlacement.lender[0].jwt_token)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f"Offer {self.offer_id + 1} does not exist"

        logging.info(f"----------------------- Invalid offer ID in BID - step passed "
                     f"----------------------------------\n")

    @pytest.mark.parametrize('offer_placed', [[test_sum, test_duration, test_offer_interest_low]],
                             indirect=True)
    def test_no_bid_interest_above_suggested(self, offer_placed):

        TestBidPlacement.offer_id = offer_placed

        response = postman.gateway_requests. \
            place_bid(TestBidPlacement.lender[0].user_id, test_offer_interest_low * 2,
                      TestBidPlacement.offer_id, 0, TestBidPlacement.lender[0].jwt_token)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f'Interest rate above offer interest rate {test_offer_interest_low}'

        logging.info(f"----------------------- BID Interest Greater Then Offer Interest - step passed "
                     f"----------------------------------\n")

    def test_lender_can_place_one_bid_on_offer(self):
        response = postman.gateway_requests. \
            place_bid(TestBidPlacement.lender[0].user_id, self.bid_interest_list[0],
                      TestBidPlacement.offer_id, 0,  TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
        assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
        assert isinstance(response['bid_id'], int), "BID Placement error - invalid BID ID in response "

        response = postman.gateway_requests. \
            place_bid(TestBidPlacement.lender[0].user_id, self.bid_interest_list[0],
                      TestBidPlacement.offer_id, 0, TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f'Lender is allowed to place only one Bid on each Offer'

        logging.info(f"----------------------- Lender Can Place One Bid On Each Offer - step passed "
                     f"----------------------------------\n")

    def test_matched_offer_cant_be_matched(self):

        # Placing 5 bids so the offer will become matched
        for i in range(1, 5):
            response = postman.gateway_requests. \
                place_bid(TestBidPlacement.lender[i].user_id, self.bid_interest_list[i],
                          self.offer_id, 0, TestBidPlacement.lender[i].jwt_token)
            logging.info(response)

        time.sleep(5)

        response = postman.gateway_requests. \
            place_bid(TestBidPlacement.lender[i].user_id, self.bid_interest_list[i],
                      self.offer_id, 0, TestBidPlacement.lender[i].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == f"Bids can't be placed on offers in status {Offer.OfferStatuses.MATCHED.value}"

        logging.info(f"----------------------- BID Can't Be Placed On Matched Offer' - step passed "
                     f"----------------------------------\n")