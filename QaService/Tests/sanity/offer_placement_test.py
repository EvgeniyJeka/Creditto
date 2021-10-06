from credittomodels import Offer
import pytest
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)

try:
    from Requests import postman
    from Tools import reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import reporter

postman = postman.Postman()
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


@pytest.mark.sanity
@pytest.mark.incremental
class TestOfferSanity(object):
    """
       In those tests we verify that:
       1. Offer can be successfully placed
       2. API method 'get_all_offers' (get all existing offers) provide valid data on placed Offer
       3. API method 'get_offers_by_status' (get all bids with provided status) provide valid data on placed Offer
       4. Placed Offer has status OPEN (until matched, cancelled or expired)
       """

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

        TestOfferSanity.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        self.offer_id = response['offer_id']

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_get_all_offers(self):
        response = postman.gateway_requests.get_all_offers()
        logging.info(response)

        assert isinstance(response, list), "Invalid data type in API response"
        assert len(response) > 0, "Placed offer wasn't returned in API response "
        assert isinstance(response[0], dict), "Invalid data type in API response"

        for offer in response:
            if offer['id'] == TestOfferSanity.offer_id:
                assert offer['owner_id'] == test_offer_owner_1
                assert Decimal(offer['sum']) == Decimal(test_sum)
                assert offer['duration'] == test_duration
                assert offer['offered_interest'] == str(test_offer_interest_low)
                assert offer['status'] == Offer.OfferStatuses.OPEN.value

        logging.info(f"----------------------- Get All Offers API method - data verified "
                     f"------------------------------\n")

    def test_get_offers_by_status(self):
        response = postman.gateway_requests.get_offers_by_status(Offer.OfferStatuses.OPEN.value)
        logging.info(response)

        assert isinstance(response, list), "Invalid data type in API response"
        assert len(response) > 0, "Placed offer wasn't returned in API response "
        assert isinstance(response[0], dict), "Invalid data type in API response"

        for offer in response:
            if offer['id'] == TestOfferSanity.offer_id:
                assert offer['owner_id'] == test_offer_owner_1
                assert Decimal(offer['sum']) == Decimal(test_sum)
                assert offer['duration'] == test_duration
                assert offer['offered_interest'] == str(test_offer_interest_low)
                assert offer['status'] == Offer.OfferStatuses.OPEN.value

        logging.info(f"----------------------- Get All OPEN Offers  API method - data verified "
                     f"------------------------------\n")

