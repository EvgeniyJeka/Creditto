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

from credittomodels.utils import Calculator as Calculator


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
@pytest.mark.functional
class TestMatchData(object):

    match_input = {'offer_owner': test_offer_owner, 'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest, 'bid_owners_list': test_bid_owners_list,
                   'bid_interest': test_bid_interest, 'offer_owner_token': test_token}

    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_verifying_match(self, match_ready):
        logging.info(self.created_match)

        monthly_payment = Calculator.calculate_monthly_payment(Decimal(test_sum), Decimal(test_bid_interest),
                                                               Decimal(test_duration), 4)

        assert self.created_match['offer_id'] == self.offer_id, "Match record in SQL differs from expected"
        assert self.created_match['bid_id'] == self.bid_id, "Match record in SQL differs from expected"
        assert self.created_match['offer_owner_id'] == test_offer_owner, "Match record in SQL differs from expected"

        assert self.created_match['bid_owner_id'] == test_bid_owner_1, "Match record in SQL differs from expected"
        assert Decimal(self.created_match['sum']) == Decimal(test_sum), "Match record in SQL differs from expected"
        assert self.created_match['final_interest'] == str(test_bid_interest), \
            "Match record in SQL differs from expected"

        assert Decimal(self.created_match['monthly_payment']) == monthly_payment, \
            "Match record in SQL differs from expected"

        logging.info(
            f"----------------------- Match validation in SQL - step passed ------------------------------\n")

