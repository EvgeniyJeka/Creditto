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
    1. Borrower can place Offers
    2. Borrower can't place Bids
    """

    offer_id = 0
    borrower = None

    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer(self, set_matching_logic, get_authorized_borrowers):
        TestPermissions.borrower = get_authorized_borrowers[0]

        response = postman.gateway_requests.place_offer(TestPermissions.borrower.user_id, test_sum,
                                                        test_duration, test_offer_interest, 0,
                                                        TestPermissions.borrower.jwt_token)

        TestPermissions.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        logging.info(f"----------------------- Offer Placement Borrower Permissions Verified - "
                     f"step passed ----------------------------------\n")

    def test_borrower_bids_blocked(self):
        response = postman.gateway_requests. \
            place_bid(TestPermissions.borrower.user_id, test_offer_interest, self.offer_id, 0,
                      TestPermissions.borrower.jwt_token)
        logging.info(response)

        assert 'error' in response.keys()
        assert response['error'] == 'Forbidden action'

        logging.info(f"----------------------- Bid Placement Borrower Permissions Verified - "
                     f"step passed ----------------------------------\n")


