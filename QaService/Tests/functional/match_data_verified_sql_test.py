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


@pytest.mark.container
@pytest.mark.incremental
class TestMatchData(object):

    match_input = {'offer_owner': test_offer_owner, 'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest, 'bid_owners_list': test_bid_owners_list,
                   'bid_interest': test_bid_interest, 'offer_owner_token': test_token}


    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_verifying_match(self, set_matching_logic, match_ready):
        print(self.created_match)
