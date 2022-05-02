import time

import pytest
import logging

from credittomodels import User

try:
    from Requests import postman
    from Tools import reporter
    from Tools import DockerIntegration

except ModuleNotFoundError:
    from ..Requests import postman
    from ..Tools import reporter
    from ..Tools import DockerIntegration

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()
docker_tool = DockerIntegration.DockerIntegration

container_downtime = 10
container_deactivation_delay = 5


@pytest.fixture(scope='class')
def set_matching_logic(request):
    """
    This fixture can be used to change matching logic configuration in SQL
    :param request: matching logic ID, int
    :return: None
    """
    if hasattr(request, 'param'):
        matching_logic = request.param[0]

    else:
        matching_logic = 1

    current_matching_logic = reporter.fetch_config_from_db("matching_logic")

    if current_matching_logic != matching_logic:
        reporter.set_config_in_db(1, matching_logic)


@pytest.fixture(scope='class')
def get_authorized_borrowers(request):

    result = []
    borrowers_amount = request.param[0]

    borrowers_raw = reporter.get_users_by_role(1)

    for borrower in borrowers_raw[0:borrowers_amount]:
        user_borrower = User.User(*borrower)
        user_borrower.password = test_users_passwords()[user_borrower.user_name]

        result.append(sign_in_user(user_borrower))

    return result


@pytest.fixture(scope='class')
def get_authorized_lenders(request):

    result = []
    lenders_amount = request.param[0]

    lenders_raw = reporter.get_users_by_role(2)

    for lender in lenders_raw[0:lenders_amount]:
        user_lender = User.User(*lender)
        user_lender.password = test_users_passwords()[user_lender.user_name]

        result.append(sign_in_user(user_lender))

    return result


def get_authorized_borrowers_internal(borrowers_amount):

    result = []
    borrowers_raw = reporter.get_users_by_role(1)

    for borrower in borrowers_raw[0:borrowers_amount]:
        user_borrower = User.User(*borrower)
        user_borrower.password = test_users_passwords()[user_borrower.user_name]

        result.append(sign_in_user(user_borrower))

    return result


def get_authorized_lenders_internal(lenders_amount):

    result = []
    lenders_raw = reporter.get_users_by_role(2)

    for lender in lenders_raw[0:lenders_amount]:
        user_lender = User.User(*lender)
        user_lender.password = test_users_passwords()[user_lender.user_name]

        result.append(sign_in_user(user_lender))

    return result


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


@pytest.fixture(scope='class')
def restart_container(request):
    """
    This fixture can be used to restart a running Docker container

    """

    container_to_restart = request.param[0]

    container = docker_tool.stop_container(container_to_restart)
    time.sleep(container_downtime)
    docker_tool.start_container(container)


def container_restart(container_to_restart):
    """
    This method can be used to restart a running Docker container
    :param container_to_restart: container name , str
    :return: True on success, False on failure
    """
    try:
        container = docker_tool.stop_container(container_to_restart)
        time.sleep(6)
        docker_tool.start_container(container)
        return True

    except Exception as e:
        logging.error(f"Failed to restart container: {container_to_restart} - {e}")
        return False


def container_stop(container_to_stop):
    """
    This method can be used to restart a running Docker container
    :param container_to_stop: container name , str
    :return: docker container instance, stopped container. False - on failure
    """
    try:
        container = docker_tool.stop_container(container_to_stop)
        time.sleep(container_deactivation_delay)
        return container

    except Exception as e:
        logging.error(f"Failed to stop container: {container_to_stop} - {e}")
        return False


def container_start(container_to_start):
    """
    This method can be used to start stopped Docker container
    :param container_to_start: docker container instance
    :return: True on success, False on failure
    """
    try:
        container = docker_tool.start_container(container_to_start)
        time.sleep(container_deactivation_delay)
        docker_tool.start_container(container)
        return True

    except Exception as e:
        logging.error(f"Failed to start container: {container_to_start} - {e}")
        return False


@pytest.fixture(scope='class')
def match_ready(request, set_matching_logic):
    """
    This fixture can be used to generate a match - it places an offer and a bid that is expected to match with the
    placed offer. The fixture expected for offer and bid params to be passed in a dict
    :param request: dict with offer and bid params
    :return: None (match ID is attached to Test Class body)
    """
    borrower = get_authorized_borrowers_internal(1)[0]
    lenders = get_authorized_lenders_internal(5)

    match_input = request.param[0]

    test_sum = match_input['offer_sum']
    test_duration = match_input['offer_duration']

    test_offer_interest = match_input['offer_interest']
    test_bid_interest = match_input['bid_interest']

    # Placing Offer
    response = postman.gateway_requests.place_offer(borrower.user_id, test_sum,
                                                    test_duration, test_offer_interest, 0, borrower.jwt_token)

    offer_id = response['offer_id']
    logging.info(f"Offer placement: response received {response}")

    assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
    assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

    time.sleep(5)

    # Placing Bid that is expected to match with the Offer
    bid_id = 0

    for i in range(0, 5):
        response = postman.gateway_requests. \
            place_bid(lenders[i].user_id, test_bid_interest, offer_id, 0, lenders[i].jwt_token)
        logging.info(response)

        assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
        assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
        assert isinstance(response['bid_id'], int), "BID Placement error - invalid BID ID in response "
        if i == 0:
            bid_id = response['bid_id']

    # Finding the created match by Offer ID
    time.sleep(5)
    my_matches = postman.gateway_requests.get_matches_by_owner(borrower.jwt_token)
    logging.warning(f"Matches received: {my_matches}")

    logging.warning(f"Looking for offer ID {offer_id}")
    result = [x for x in my_matches if x['offer_id'] == offer_id]

    logging.info(f"Found the created match: {result}")

    if len(result) > 0:
        request.cls.created_match = [x for x in my_matches if x['offer_id'] == offer_id][0]
        request.cls.offer_id = offer_id
        request.cls.bid_id = bid_id
        #request.cls.bid_owner_id = get_authorized_lenders[0]

    else:
        logging.error(f"Match creation failed - offer ID {offer_id}")


def test_users_passwords():
    return {'Greg Bradly': "Pigs", 'Joe Anderson': "Truth",
            'Andrew Levi': "Pass", 'Mary Poppins': "Journey",
            'David Ben Gurion': "Rabbit", 'Joseph Biggs': "Bank",
            'Mara Karadja': "Fist", 'Lena Goldan': "Nice", 'Katya Rast': "Elite",
            'Paul Atreides': "Spice", 'Leto Atreides': "Kiev", 'Baba Yaga': "Hero", 'Mike Smith': "Mars"}


def sign_in_user(user: User):
    password = test_users_passwords()[user.user_name]
    response = postman.gateway_requests.sign_in_user(user.user_name, password)
    user.jwt_token = response['Token']
    return user


# Support for @pytest.mark.incremental
def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item

def pytest_runtest_setup(item):
    previousfailed = getattr(item.parent, "_previousfailed", None)
    if previousfailed is not None:
        pytest.xfail(f"previous test step failed {previousfailed.name}, test flow is terminated")




# if __name__ == '__main__':
#     ussr = User.User(202, 'Joe Anderson', 'cc3a062a97bf2935e0e12e1aee3bed944a81e1f4e4ca21eaa03b07be38628686', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiSm9lIEFuZGVyc29uIiwicGFzc3dvcmQiOiJUcnV0aCJ9.I4wjJ4COVHjXaJuqCWUOA87kvRtm6vWIYRngxpoVAbo', 'key4790', '1651420544.7691257', 2)
#     rt = sign_in_user(ussr)
#     print(rt.user_name)