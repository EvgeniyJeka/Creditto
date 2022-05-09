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
    borrower = None

    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_missing_sum_field(self, get_authorized_borrowers):
        TestOfferPlacement.borrower = get_authorized_borrowers[0]

        # Trying to place an offer without the SUM field
        offer_body_no_sum = {
            TYPE: "offer",
            DURATION: test_duration,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_no_sum, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_no_sum,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided offer'

        logging.info(f"----------------------- 'Invalid Offer without Sum can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_duration_field(self):

        # Trying to place an offer without the DURATION field
        offer_body_no_duration = {
            TYPE: "offer",
            SUM: test_sum,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_no_duration, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_no_duration,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided offer'

        logging.info(f"----------------------- 'Invalid Offer without Duration can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_offered_interest_field(self):

        # Trying to place an offer without the INTEREST field
        offer_body_no_interest = {
            TYPE: "offer",
            SUM: test_sum,
            DURATION: test_duration,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_no_interest, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_no_interest,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided offer'

        logging.info(f"----------------------- 'Invalid Offer without Offer Interest can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_null_values(self):

        # Trying to place an offer with NULLS
        offer_body_null_values = {
            TYPE: "offer",
            SUM: None,
            DURATION: None,
            OFFERED_INTEREST: None,
            ALLOW_PARTIAL_FILL: None
        }

        logging.info(json.dumps(offer_body_null_values, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_null_values,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer with NULL can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_invalid_data_types(self):

        # Trying to place an offer with invalid data types
        offer_body_invalid_types = {
            TYPE: 33,
            SUM: str(test_sum),
            DURATION: str(test_duration),
            OFFERED_INTEREST: [test_offer_interest_hight, test_offer_interest_low],
            ALLOW_PARTIAL_FILL: '0'
        }

        logging.info(json.dumps(offer_body_invalid_types, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_invalid_types,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Offer with invalid data types can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_type(self):

        # Trying to place an offer without TYPE
        offer_body_type_missing = {
            SUM: test_sum,
            DURATION: test_duration,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_type_missing, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_type_missing,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer without Type can't be placed ' - step passed "
                     f"----------------------------------\n")

    def non_json_body(self):

        # Trying to place an offer with a string as body (instead of JSON)
        response = postman.gateway_requests.place_offer_custom_body("bad_request_body_string",
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer Non-JSON body in request can't be placed' ' - step passed "
                     f"----------------------------------\n")

    def test_incorrect_type(self):

        # Trying to place an offer with an incorrect TYPE
        offer_body_type_missing = {
            TYPE: "bid",
            SUM: test_sum,
            DURATION: test_duration,
            OFFERED_INTEREST: test_offer_interest_hight,
            ALLOW_PARTIAL_FILL: 0
        }

        logging.info(json.dumps(offer_body_type_missing, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_offer_custom_body(offer_body_type_missing,
                                                                    TestOfferPlacement.borrower.jwt_token)
        logging.info(response)

        assert 'offer_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Invalid object type for this API method'

        logging.info(f"----------------------- 'Invalid Offer without Incorrect Type can't be placed ' - step passed "
                     f"----------------------------------\n")

