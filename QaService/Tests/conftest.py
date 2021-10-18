import time

import pytest
import logging
from ..Tools import reporter
from ..Requests import postman

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()


@pytest.fixture(scope='class')
def set_matching_logic(request):
    """
    This fixture can be used to change matching logic configuration in SQL
    :param request: matching logic ID, int
    :return: None
    """
    # if request.param:
    #     matching_logic = request.param[0]
    #
    # else:
    #     matching_logic = 1

    matching_logic = request.param[0]
    current_matching_logic = reporter.fetch_config_from_db("matching_logic")

    if current_matching_logic != matching_logic:
        reporter.set_config_in_db(1, matching_logic)


@pytest.fixture(scope='class')
def offer_placed(request):
    """
    This fixture can be used to place an offer with provided params
    :param request: offer params
    :return: placed offer ID, int
    """
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

@pytest.mark.parametrize('set_matching_logic', [[1]], indirect=True)
@pytest.fixture(scope='class')
def match_ready(request, set_matching_logic):
    """
    This fixture can be used to generate a match - it places an offer and a bid that is expected to match with the
    placed offer. The fixture expected for offer and bid params to be passed in a dict
    :param request: dict with offer and bid params
    :return: None (match ID is attached to Test Class body)
    """
    match_input = request.param[0]

    test_offer_owner = match_input['offer_owner']
    test_sum = match_input['offer_sum']
    test_duration = match_input['offer_duration']

    test_offer_interest = match_input['offer_interest']
    test_offer_owner_token = match_input['offer_owner_token']

    test_bid_owner = match_input['bid_owner']
    test_bid_interest = match_input['bid_interest']

    # Placing Offer
    response = postman.gateway_requests.place_offer(test_offer_owner, test_sum,
                                                    test_duration, test_offer_interest, 0)

    offer_id = response['offer_id']
    logging.info(f"Offer placement: response received {response}")

    assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
    assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

    time.sleep(5)

    # Placing Bid that is expected to match with the Offer

    for i in range(0, 5):
        response = postman.gateway_requests. \
            place_bid(test_bid_owner, test_bid_interest, offer_id, 0)
        logging.info(response)

    assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
    assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
    assert isinstance(response['bid_id'], int), "BID Placement error - invalid BID ID in response "

    # Finding the created match by Offer ID
    my_matches = postman.gateway_requests.get_matches_by_owner(test_offer_owner, test_offer_owner_token)

    result = [x for x in my_matches if x['offer_id'] == offer_id]

    if len(result) > 0:
        request.cls.created_match = [x for x in my_matches if x['offer_id'] == offer_id][0]

    else:
        logging.error(f"Match creation failed - offer ID {offer_id}")




