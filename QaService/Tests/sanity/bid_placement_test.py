from credittomodels import Bid
import pytest
import logging
import os

try:
    from Requests import postman
    from Tools import reporter, results_reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import reporter, results_reporter

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()
report_test_results = results_reporter.ResultsReporter()

test_offer_interest_low = 0.05
test_sum = 20000
test_duration = 24


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

test_id = 300
test_file_name = os.path.basename(__file__)


@pytest.mark.container
@pytest.mark.sanity
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
    borrower = None
    lenders = None

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5, test_bid_interest_6, test_bid_interest_7,
                         test_bid_interest_8, test_bid_interest_9, test_bid_interest_10]

    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer(self, set_matching_logic, get_authorized_borrowers):
        try:

            TestBidSanity.borrower = get_authorized_borrowers[0]

            response = postman.gateway_requests.place_offer(TestBidSanity.borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest_low, 0,
                                                            TestBidSanity.borrower.jwt_token)

            TestBidSanity.offer_id = response['offer_id']
            logging.info(f"Offer placement: response received {response}")

            assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
            assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

            self.offer_id = response['offer_id']

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    @pytest.mark.parametrize('get_authorized_lenders', [[1]], indirect=True)
    def test_placing_bid(self, get_authorized_lenders):
        try:

            TestBidSanity.lenders = get_authorized_lenders

            response = postman.gateway_requests.\
                place_bid(TestBidSanity.lenders[0].user_id, self.bid_interest_list[0],
                          self.offer_id, 0, TestBidSanity.lenders[0].jwt_token)
            logging.info(response)

            TestBidSanity.bid_id = response['bid_id']

            assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
            assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
            assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")

    def test_bids_by_owner(self):
        try:
            response = postman.gateway_requests.get_bids_by_owner(TestBidSanity.lenders[0].jwt_token)
            logging.info(response)

            assert isinstance(response, list), "Invalid data type in API response"
            assert len(response) > 0, "Placed offer wasn't returned in API response "
            assert isinstance(response[0], dict), "Invalid data type in API response"

            for bid in response:
                if bid['id'] == TestBidSanity.bid_id:
                    logging.info(bid)
                    assert bid['owner_id'] == TestBidSanity.lenders[0].user_id
                    assert bid['bid_interest'] == str(self.bid_interest_list[0])
                    assert bid['target_offer_id'] == TestBidSanity.offer_id
                    assert bid['status'] == Bid.BidStatuses.PLACED.value

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Get All Bids By Owner API method - data verified ---------"
                     f"-------------------------\n")

        report_test_results.report_success(test_id, test_file_name)