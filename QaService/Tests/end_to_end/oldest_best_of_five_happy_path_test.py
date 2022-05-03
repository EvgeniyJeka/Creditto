import time
from credittomodels import Offer
import pytest
import logging
from decimal import Decimal


try:
    from Requests import postman
    from Tools import reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import reporter


logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()


test_offer_owner_1 = 1024
test_offer_interest_low = 0.05
test_sum = 30000
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
@pytest.mark.container
@pytest.mark.end2end
class TestBestOfFive:
    """
        In those tests we verify that:
        1. Full end-to-end flow : placed Offer is matched with the best Bid out of five placed bids
        2. Matching logic is configurable
        3. Selected matching logic - the Bid with the best interest is selected out of 5 bids,
        when the 5th bid is placed. If 2 or more bids have the same interest the oldest bid is selected.
        4. Offer status is updated accordingly in SQL DB
        5. Offer 'final interest' (best bid interest) is updated accordingly in SQL DB
    """

    offer_id = 0
    matching_bid_id = 0
    lenders = None
    borrower = None

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5]

    @pytest.mark.parametrize('set_matching_logic', [[1]], indirect=True)
    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer(self, set_matching_logic, get_authorized_borrowers):

        TestBestOfFive.borrower = get_authorized_borrowers[0]
        response = postman.gateway_requests.place_offer(TestBestOfFive.borrower.user_id, test_sum,
                                                        test_duration, test_offer_interest_low, 0,
                                                        TestBestOfFive.borrower.jwt_token)

        TestBestOfFive.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        self.offer_id = response['offer_id']

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_offer_in_sql(self):
        time.sleep(4)
        offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
        logging.info(offer_sql)
        assert offer_sql['id'] == self.offer_id, "Offer Placement error - placed offer wasn't saved to DB"

        logging.info(f"----------------------- Offer ID validation in SQL - step passed ------------------------------\n")

    @pytest.mark.parametrize('get_authorized_lenders', [[5]], indirect=True)
    def test_placing_first_bids(self, get_authorized_lenders):

        TestBestOfFive.lenders = get_authorized_lenders

        for i in range(0, 3):
            response = postman.gateway_requests.\
                place_bid(TestBestOfFive.lenders[i].user_id, self.bid_interest_list[i],
                          self.offer_id, 0, TestBestOfFive.lenders[i].jwt_token)
            logging.info(response)

            assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
            assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
            assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")

    def test_verify_no_match_yet(self):
        logging.info(f"Offer SQL : {reporter.get_offer_by_id(self.offer_id)}")

        offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
        logging.info(offer_sql)
        assert offer_sql['status'] == Offer.OfferStatuses.OPEN.value, "Offer was matched before 3 bids were placed"
        assert offer_sql['final_interest'] == '-1'

        logging.info(f"----------------------- No Match On Third Bid verification - step passed ----------"
                     f"------------------------\n")

    def test_placing_final_bids(self):
        for i in range(3, 5):
            response = postman.gateway_requests. \
                place_bid(TestBestOfFive.lenders[i].user_id, self.bid_interest_list[i],
                          self.offer_id, 0, TestBestOfFive.lenders[i].jwt_token)
            logging.info(response)

            # The bid that is expected to create a match with the offer
            if i == 3:
                TestBestOfFive.matching_bid_id = response['bid_id']

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
        assert offer_sql['final_interest'] == str(test_bid_interest_4), \
            "Final interest in SQL wasn't updated after match"

        logging.info(f"----------------------- Verifying Offer Data Updated in SQL - step passed --------------"
                     f"--------------------\n")

    def test_match_data_verified(self):
        match_sql = reporter.get_match_by_offer_id(self.offer_id)[0]
        logging.info(match_sql)

        assert match_sql['bid_id'] == TestBestOfFive.matching_bid_id
        assert match_sql['bid_owner_id'] == TestBestOfFive.lenders[3].user_id
        assert match_sql['final_interest'] == str(test_bid_interest_4)

        logging.info(f"----------------------- Verifying Match Data in SQL - step passed --------------------"
                     f"--------------\n")

    def test_get_offers_by_status(self):
        response = postman.gateway_requests.get_offers_by_status(Offer.OfferStatuses.MATCHED.value)
        logging.info(response)

        assert isinstance(response, list), "Invalid data type in API response"
        assert len(response) > 0, "Placed offer wasn't returned in API response "
        assert isinstance(response[0], dict), "Invalid data type in API response"

        for offer in response:
            if offer['id'] == TestBestOfFive.offer_id:
                assert offer['owner_id'] == TestBestOfFive.borrower.user_id
                assert Decimal(offer['sum']) == Decimal(test_sum)
                assert offer['duration'] == test_duration
                assert offer['offered_interest'] == str(test_offer_interest_low)
                assert offer['status'] == Offer.OfferStatuses.MATCHED.value

        logging.info(f"----------------------- Get All MATCHED Offers  API method - data verified "
                     f"------------------------------\n")
