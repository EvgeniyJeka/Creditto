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
test_sum = 20000
test_duration = 24

test_bid_interest_1 = 0.046
test_bid_interest_2 = 0.045
test_bid_interest_3 = 0.044
test_bid_interest_4 = 0.037
test_bid_interest_5 = 0.037


@pytest.mark.container
@pytest.mark.negative
@pytest.mark.incremental
class TestBidPlacement(object):
    """
    In those tests we verify that:
    1. Bid placement request with missing mandatory field will be rejected - verifying error message
    2. Bid placement request with NULL in mandatory field will be rejected - verifying error message
    3. Bid placement request with invalid data type will be rejected - verifying error message
    4. Bid placement request with no type in request body will be rejected - verifying error message
    5. Bid placement request is rejected, unless it's body is a valid JSON - verifying error message
    6. Bid placement request with incorrect type in request body will be rejected - verifying error message

    NOTE: Error message successful validation confirms that Gateway hasn't crashed and handled the invalid input
    # as expected.
    """
    offer_id = 0
    matching_bid_id = 0
    lender = None

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5]

    @pytest.mark.parametrize('set_matching_logic', [[1]], indirect=True)
    @pytest.mark.parametrize('get_authorized_lenders', [[5]], indirect=True)
    @pytest.mark.parametrize('offer_placed', [[test_sum, test_duration, test_offer_interest_low]],
                             indirect=True)
    def test_missing_bid_interest_field(self, set_matching_logic, offer_placed, get_authorized_lenders):
        
        TestBidPlacement.offer_id = offer_placed
        TestBidPlacement.lender = get_authorized_lenders

        # Trying to place a bid without the INTEREST field
        bid_body_no_interest = {
            TYPE: "bid",
            TARGET_OFFER_ID: self.offer_id,
            PARTIAL_ONLY: 0
        }

        logging.info(json.dumps(bid_body_no_interest, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_bid_custom_body(bid_body_no_interest,
                                                                  TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided bid'

        logging.info(f"----------------------- 'Invalid Bid without Interest can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_missing_target_offer_field(self):

        # Trying to place a bid without the TARGET OFFER field
        bid_body_no_target_offer = {
            TYPE: "bid",
            BID_INTEREST: self.bid_interest_list[0],
            PARTIAL_ONLY: 0
        }

        logging.info(json.dumps(bid_body_no_target_offer, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_bid_custom_body(bid_body_no_target_offer,
                                                                  TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == 'Required parameter is missing in provided bid'

        logging.info(f"----------------------- 'Invalid Bid without Target Offer ID can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_null_in_bid(self):

        # Trying to place a bid with NULLs
        bid_body_null_in_bid_interest = {
            TYPE: "bid",
            BID_INTEREST: None,
            TARGET_OFFER_ID: None,
            PARTIAL_ONLY: None
        }

        logging.info(json.dumps(bid_body_null_in_bid_interest, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_bid_custom_body(bid_body_null_in_bid_interest,
                                                                  TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == "Invalid object type for this API method"

        logging.info(f"-----------------------' Invalid Bid NULL in Interest field can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_invalid_data_types(self):

        # Trying to place a bid with invalid data types
        bid_invalid_data_types = {
            TYPE: 22,
            OWNER_ID: str(TestBidPlacement.lender[0].user_id),
            BID_INTEREST: str(self.bid_interest_list[0]),
            TARGET_OFFER_ID: str(self.offer_id),
            PARTIAL_ONLY: '0'
        }

        logging.info(json.dumps(bid_invalid_data_types, default=lambda o: vars(o), sort_keys=True, indent=4))

        response = postman.gateway_requests.place_bid_custom_body(bid_invalid_data_types,
                                                                  TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == "Invalid object type for this API method"

        logging.info(f"----------------------- 'Invalid data types in request - Bid can't be placed ' - step passed "
                     f"----------------------------------\n")

    def test_non_json_body(self):
        logging.info("bad_request_body_string")

        response = postman.gateway_requests.place_bid_custom_body("bad_request_body_string",
                                                                  TestBidPlacement.lender[0].jwt_token)
        logging.info(response)

        assert 'bid_id' not in response.keys()
        assert 'result' not in response.keys()
        assert 'error' in response.keys()
        assert response['error'] == "Invalid object type for this API method"

        logging.info(f"----------------------- 'Non-JSON body in request - Bid can't be placed ' - step passed"
                     f"----------------------------------\n")

    # def test_wrong_type_for_bid_request(self):
    #     bid_body_null_in_bid_interest = {
    #         TYPE: "offer",
    #         OWNER_ID: self.bid_owners[0],
    #         BID_INTEREST: self.bid_interest_list[0],
    #         TARGET_OFFER_ID: self.offer_id,
    #         PARTIAL_ONLY: 0
    #     }
    #
    #     logging.info(json.dumps(bid_body_null_in_bid_interest, default=lambda o: vars(o), sort_keys=True, indent=4))
    #
    #     response = postman.gateway_requests.place_bid_custom_body(bid_body_null_in_bid_interest)
    #     logging.info(response)
    #
    #     assert 'bid_id' not in response.keys()
    #     assert 'result' not in response.keys()
    #     assert 'error' in response.keys()
    #     assert response['error'] == 'Invalid object type for this API method'
    #
    #     logging.info(f"----------------------- 'Incorrect type for Bid - Bid can't be placed ' - step passed"
    #                  f"----------------------------------\n")
    #
    # def test_no_type_in_bid_reqest(self):
    #     bid_body_null_in_bid_interest = {
    #         OWNER_ID: self.bid_owners[0],
    #         BID_INTEREST: self.bid_interest_list[0],
    #         TARGET_OFFER_ID: self.offer_id,
    #         PARTIAL_ONLY: 0
    #     }
    #
    #     logging.info(json.dumps(bid_body_null_in_bid_interest, default=lambda o: vars(o), sort_keys=True, indent=4))
    #
    #     response = postman.gateway_requests.place_bid_custom_body(bid_body_null_in_bid_interest)
    #     logging.info(response)
    #
    #     assert 'bid_id' not in response.keys()
    #     assert 'result' not in response.keys()
    #     assert 'error' in response.keys()
    #     assert response['error'] == 'Invalid object type for this API method'
    #
    #     logging.info(f"----------------------- 'Incorrect type for Bid - Bid can't be placed ' - step passed"
    #                  f"----------------------------------\n")
