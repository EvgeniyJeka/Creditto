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

test_offer_interest = 0.06
test_sum = 5000
test_duration = 13
test_bid_interest = 0.056


@pytest.mark.container
@pytest.mark.functional
class TestMatchData(object):
    """
       In those tests we verify that:
       1. Matches produced by the Matcher are saved to SQL DB
       2. Verifying match data saved to SQL against against matched offer and bid params
    """

    match_input = {'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest,
                   'bid_interest': test_bid_interest}

    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_verifying_match(self, match_ready):
        logging.info(self.created_match)

        monthly_payment = Calculator.calculate_monthly_payment(Decimal(test_sum), Decimal(test_bid_interest),
                                                               Decimal(test_duration), 4)

        assert self.created_match['offer_id'] == self.offer_id, "Match record in SQL differs from expected"
        assert self.created_match['bid_id'] == self.bid_id, "Match record in SQL differs from expected"
        assert self.created_match['offer_owner_id'] == self.offer_owner_id, "Match record in SQL differs from expected"

        assert self.created_match['bid_owner_id'] == self.bid_owner_id, "Match record in SQL differs from expected"
        assert Decimal(self.created_match['sum']) == Decimal(test_sum), "Match record in SQL differs from expected"
        assert self.created_match['final_interest'] == str(test_bid_interest), \
            "Match record in SQL differs from expected"

        assert Decimal(self.created_match['monthly_payment']) == monthly_payment, \
            "Match record in SQL differs from expected"

        logging.info(
            f"----------------------- Match validation in SQL - step passed ------------------------------\n")

