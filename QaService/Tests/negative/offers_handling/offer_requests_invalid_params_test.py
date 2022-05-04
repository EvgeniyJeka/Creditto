import json
import pytest
import logging


try:
    from Requests import postman
    from Tools import reporter
    from Requests.Body_Constructors.requests_constants import *

except ModuleNotFoundError:
    from ....Requests import postman
    from ....Tools import reporter
    from ....Requests.Body_Constructors.requests_constants import *

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()

test_offer_owner_1 = 1024
test_offer_interest_low = 0.05
test_offer_interest_hight = 0.09
test_sum = 50000
test_duration = 24


@pytest.mark.container
@pytest.mark.negative
@pytest.mark.incremental
class TestOfferPlacement(object):
    """
        In those tests we verify that:
        1. Offer placement request with missing mandatory field will be rejected - verifying error message
        2. Offer placement request with NULL in mandatory field will be rejected - verifying error message
        3. Offer placement request with invalid data type will be rejected - verifying error message
        4. Offer placement request with no type in request body will be rejected - verifying error message
        5. Offer placement request is rejected, unless it's body is a valid JSON - verifying error message
        6. Offer placement request with incorrect type in request body will be rejected - verifying error message

    NOTE: Error message successful validation confirms that Gateway hasn't crashed and handled the invalid input
    # as expected.
    """

    # def test_missing_owner_id_field(self):
    # 
    #     offer_body_no_owner = {
    #         TYPE: "offer",
    #         SUM: test_sum,
    #         DURATION: test_duration,
    #         OFFERED_INTEREST: test_offer_interest_hight,
    #         ALLOW_PARTIAL_FILL: 0
    #     }
    # 
    #     logging.info(json.dumps(offer_body_no_owner, default=lambda o: vars(o), sort_keys=True, indent=4))
    # 
    #     response = postman.gateway_requests.place_offer_custom_body(offer_body_no_owner)
    #     logging.info(response)
    # 
    #     assert 'offer_id' not in response.keys()
    #     assert 'result' not in response.keys()
    #     assert 'error' in response.keys()
    #     assert response['error'] == 'Required parameter is missing in provided offer'
    # 
    #     logging.info(f"----------------------- 'Invalid Offer without Owner ID can't be placed ' - step passed "
    #                  f"----------------------------------\n")

    def test_missing_sum_field(self):

        offer_body_no_sum = {
            TYPE: "offer",
            DURATION: test_duration,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_no_sum, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_no_sum)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided offer'

        logging.info(f"----------------------- 'Invalid Offer without Sum can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_duration_field(self):

        offer_body_no_duration = {
            TYPE: "offer",
            SUM: test_sum,
            OWNER_ID: test_offer_owner_1,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_no_duration, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_no_duration)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided offer'

        logging.info(f"----------------------- 'Invalid Offer without Duration can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_offered_interest_field(self):

        offer_body_no_interest = {
            TYPE: "offer",
            SUM: test_sum,
            OWNER_ID: test_offer_owner_1,
            DURATION: test_duration,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_no_interest, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_no_interest)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided offer'

        logging.info(f"----------------------- 'Invalid Offer without Offer Interest can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_null_values(self):

        offer_body_null_values = {
            TYPE: "offer",
            SUM: None,
            OWNER_ID: None,
            DURATION: None,
            OFFERED_INTEREST: None,
            ALLOW_PARTIAL_FILL: None
        }

        logging.info(json.dumps(offer_body_null_values, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_null_values)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer with NULL can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_invalid_data_types(self):
        offer_body_invalid_types = {
            TYPE: 33,
            SUM: str(test_sum),
            OWNER_ID: str(test_offer_owner_1),
            DURATION: str(test_duration),
            OFFERED_INTEREST: [test_offer_interest_hight, test_offer_interest_low],
            ALLOW_PARTIAL_FILL: '0'
        }

        logging.info(json.dumps(offer_body_invalid_types, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_invalid_types)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Offer with invalid data types can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_type(self):

        offer_body_type_missing = {
            SUM: test_sum,
            OWNER_ID: test_offer_owner_1,
            DURATION: test_duration,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_type_missing, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_type_missing)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer without Type can't be placed ' - step passed "
                     f"----------------------------------\n")

    def non_json_body(self):
        logging.info("bad_request_body_string")

        response = postman.gateway_requests.place_offer_custom_body("bad_request_body_string")
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer Non-JSON body in request can't be placed' ' - step passed "
                     f"----------------------------------\n")

    def test_incorrect_type(self):

        offer_body_type_missing = {
            TYPE: "bid",
            SUM: test_sum,
            OWNER_ID: test_offer_owner_1,
            DURATION: test_duration,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_type_missing, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_type_missing)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer without Incorrect Type can't be placed ' - step passed "
                     f"----------------------------------\n")

