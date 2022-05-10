import pytest
import logging

try:
    from Requests import postman
    from Tools import KafkaIntegration

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import KafkaIntegration

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
kafka_integration = KafkaIntegration.KafkaIntegration()


test_offer_interest = 0.05
test_sum = 20000
test_duration = 24


@pytest.mark.authorization
@pytest.mark.container
@pytest.mark.incremental
class TestPermissions(object):
    """
    In those tests we verify that:
    1. Lender can place Bids
    2. Lender can't place Offers
    """

    offer_id = 0
    lender = None

    @pytest.mark.parametrize('offer_placed', [[test_sum, test_duration, test_offer_interest]], indirect=True)
    @pytest.mark.parametrize('get_authorized_lenders', [[1]], indirect=True)
    def test_placing_bids(self, offer_placed, get_authorized_lenders):
        TestPermissions.offer_id = offer_placed
        TestPermissions.lender = get_authorized_lenders[0]

        # Placing a bid
        response = postman.gateway_requests. \
            place_bid(TestPermissions.lender.user_id, test_offer_interest / 2, self.offer_id, 0,
                      TestPermissions.lender.jwt_token)
        logging.info(response)

        assert 'bid_id' in response.keys()
        assert isinstance(response['bid_id'], int)

        logging.info(f"----------------------- Bid Placement Lender Permissions Verified - "
                     f"step passed ----------------------------------\n")

    def test_lender_offers_blocked(self):

        response = postman.gateway_requests.place_offer(TestPermissions.lender.user_id, test_sum,
                                                        test_duration, test_offer_interest, 0,
                                                        TestPermissions.lender.jwt_token)
        logging.info(response)

        assert 'error' in response.keys()
        assert response['error'] == 'Forbidden action'

        logging.info(f"----------------------- Offer Placement Lender Permissions Verified - "
                     f"step passed ----------------------------------\n")



