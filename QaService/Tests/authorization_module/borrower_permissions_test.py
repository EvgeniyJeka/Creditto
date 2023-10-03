import pytest
import logging
import os

try:
    from Requests import postman
    from Tools import KafkaIntegration, results_reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import KafkaIntegration, results_reporter

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
kafka_integration = KafkaIntegration.KafkaIntegration()
report_test_results = results_reporter.ResultsReporter()


test_offer_interest = 0.05
test_sum = 20000
test_duration = 24

test_id = 500
test_file_name = os.path.basename(__file__)


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
        try:

            TestPermissions.borrower = get_authorized_borrowers[0]

            response = postman.gateway_requests.place_offer(TestPermissions.borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest, 0,
                                                            TestPermissions.borrower.jwt_token)

            TestPermissions.offer_id = response['offer_id']
            logging.info(f"Offer placement: response received {response}")

            assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
            assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Offer Placement Borrower Permissions Verified - "
                     f"step passed ----------------------------------\n")

    def test_borrower_bids_blocked(self):
        try:
            response = postman.gateway_requests. \
                place_bid(TestPermissions.borrower.user_id, test_offer_interest, self.offer_id, 0,
                          TestPermissions.borrower.jwt_token)
            logging.info(response)

            assert 'error' in response.keys()
            assert response['error'] == 'Forbidden action'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Bid Placement Borrower Permissions Verified - "
                     f"step passed ----------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)


