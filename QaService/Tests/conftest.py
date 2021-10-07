import pytest
#from Tools.reporter import Reporter
#from Requests.postman import Postman
import logging
from ..Tools import reporter
from ..Requests import postman

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()


@pytest.fixture(scope='class')
def set_matching_logic(request):

    matching_logic = request.param[0]
    current_matching_logic = reporter.fetch_config_from_db("matching_logic")

    if current_matching_logic != matching_logic:
        reporter.set_config_in_db(1, matching_logic)


@pytest.fixture(scope='class')
def offer_placed(request):
    test_offer_owner = request.param[0]
    test_sum = request.param[1]
    test_duration = request.param[2]
    test_offer_interest = request.param[3]

    response = postman.gateway_requests.place_offer(test_offer_owner, test_sum,
                                                    test_duration, test_offer_interest, 0)

    offer_id = response['offer_id']
    logging.info(f"Offer placement: response received {response}")

    assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
    assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

    return offer_id