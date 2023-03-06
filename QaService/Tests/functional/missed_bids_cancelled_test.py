import pytest
import logging
from credittomodels import Bid
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

test_offer_owner = 1312
test_offer_interest = 0.06

test_sum = 5000
test_duration = 13

test_bid_owner_1 = 911
test_bid_owner_2 = 582
test_bid_owner_3 = 781
test_bid_owner_4 = 343
test_bid_owner_5 = 216

test_bid_owners_list = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5]
test_bid_interest = 0.056

test_token = '1Aa@<>12'

test_id = 104
test_file_name = os.path.basename(__file__)


@pytest.mark.container
@pytest.mark.functional
class TestBidsCancelled(object):
    """
       In those tests we verify that:
       1. When Offer is matched with one of the bids the status of that bid is changed to MATCHED
       2. The status of all other bids on that offer is changed to CANCELLED 
     
    """

    match_input = {'offer_owner': test_offer_owner, 'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest, 'bid_owners_list': test_bid_owners_list,
                   'bid_interest': test_bid_interest, 'offer_owner_token': test_token}

    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_missed_bids_cancelled(self, match_ready):
        try:

            bids_on_offer = reporter.get_bids_by_offer(self.offer_id)
            matched_bid_id = self.bid_id

            for bid in bids_on_offer:
                if bid['id'] == matched_bid_id:
                    assert bid['status'] == Bid.BidStatuses.MATCHED.value, "Matched Bid status wasn't updated in SQL"
                else:
                    assert bid['status'] == Bid.BidStatuses.CANCELLED.value, "Missed Bid status wasn't updated in SQL"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Bids status is updated in SQL after a match - step passed "
                     f"------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)



