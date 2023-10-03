import pytest
import logging
import os

try:
    from Requests import postman
    from Tools import results_reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import results_reporter


logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
report_test_results = results_reporter.ResultsReporter()

test_offer_interest_low = 0.05
test_sum = 20000
test_duration = 24
test_bid_interest_10 = 0.041

BLANK_JWT = ""

test_id = 502
test_file_name = os.path.basename(__file__)


@pytest.mark.authorization
@pytest.mark.container
@pytest.mark.incremental
class TestTokenVerified(object):
    """
    In those tests we verify that:
    1. Requests that require authentication are denied if EMPTY STRING is provided instead of JWT in request headers
    """
    borrower = None
    lender = None

    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer_denied(self, set_matching_logic, get_authorized_borrowers):
        try:

            TestTokenVerified.borrower = get_authorized_borrowers[0]

            # Blank JWT is passed in the request
            response = postman.gateway_requests.place_offer(TestTokenVerified.borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest_low, 0, BLANK_JWT)
            logging.info(response)

            assert 'error' in response.keys()
            assert response['error'] == 'JWT is missing in request headers'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Offer Placement Attempt With Blank JWT Rejected - "
                     f"step passed ----------------------------------\n")

    @pytest.mark.parametrize('get_authorized_lenders', [[1]], indirect=True)
    def test_placing_bid_denied(self, get_authorized_lenders):
        try:
            # Placing an offer
            response = postman.gateway_requests.place_offer(TestTokenVerified.borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest_low, 0,
                                                            TestTokenVerified.borrower.jwt_token)
            logging.info(response)
            TestTokenVerified.offer_id = response['offer_id']

            TestTokenVerified.lender = get_authorized_lenders[0]

            # Blank JWT is passed in the request
            response = postman.gateway_requests. \
                place_bid(TestTokenVerified.lender.user_id, test_bid_interest_10, self.offer_id, 0, BLANK_JWT)
            logging.info(response)

            assert 'error' in response.keys()
            assert response['error'] == 'JWT is missing in request headers'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Bid Placement Attempt With Blank JWT Rejected - "
                     f"step passed ----------------------------------\n")

    def test_get_private_bids_denied(self):
        try:
            # Blank JWT is passed in the request
            response = postman.gateway_requests.get_bids_by_owner(BLANK_JWT)
            logging.info(response)

            assert 'error' in response.keys()
            assert response['error'] == 'JWT is missing in request headers'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Access To Private Data On Bids With Blank JWT Rejected - "
                     f"step passed ----------------------------------\n")

    def test_get_private_offers_denied(self):
        try:
            # Blank JWT is passed in the request
            response = postman.gateway_requests.get_offers_by_owner(BLANK_JWT)
            logging.info(response)

            assert 'error' in response.keys()
            assert response['error'] == 'JWT is missing in request headers'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Access To Private Data On Offers With Blank JWT Rejected - "
                     f"step passed ----------------------------------\n")

    def test_get_private_matches_denied(self):
        try:
            # Blank JWT is passed in the request
            response = postman.gateway_requests.get_matches_by_owner(BLANK_JWT)
            logging.info(response)

            assert 'error' in response.keys()
            assert response['error'] == 'JWT is missing in request headers'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Access To Private Data On Matches With Blank JWT Rejected - "
                     f"step passed ----------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)

