from credittomodels import Bid
import pytest
import logging
import os


try:
    from Requests import postman
    from Tools import KafkaIntegration, results_reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import KafkaIntegration, results_reporter
    
    
logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
kafka_integration = KafkaIntegration.KafkaIntegration()
report_test_results = results_reporter.ResultsReporter()

test_offer_interest_low = 0.05
test_sum = 20000
test_duration = 24
test_bid_interest_10 = 0.041

test_id = 100
test_file_name = os.path.basename(__file__)


@pytest.mark.container
@pytest.mark.functional
@pytest.mark.kafka
@pytest.mark.incremental
class TestBidProduced(object):
    """
    In those tests we verify that:
    1. Gateway service produces valid serialized 'Bid' messages to 'bids' Kafka topic when new bid is placed.
    2. Produced messages can be consumed and deserialized to a 'Bid' instance
    3. Produced message content is verified against the original bid placement request
    """

    offer_id = 0
    bid_id = 0
    borrower_user_id = 0
    lender_user_id = 0
    
    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer(self, set_matching_logic, get_authorized_borrowers):
        try:
            borrower = get_authorized_borrowers[0]

            response = postman.gateway_requests.place_offer(borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest_low, 0, borrower.jwt_token)

            TestBidProduced.offer_id = response['offer_id']
            TestBidProduced.borrower_user_id = borrower.user_id
            logging.info(f"Offer placement: response received {response}")

            assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
            assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    @pytest.mark.parametrize('get_authorized_lenders', [[1]], indirect=True)
    def test_placing_bid(self, get_authorized_lenders):
        try:
            lender = get_authorized_lenders[0]

            response = postman.gateway_requests.\
                place_bid(lender.user_id, test_bid_interest_10, self.offer_id, 0, lender.jwt_token)
            logging.info(response)

            TestBidProduced.bid_id = response['bid_id']
            TestBidProduced.lender_user_id = lender.user_id

            assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
            assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
            assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")

    def test_bid_from_kafka(self):
        try:
            bids_from_kafka = kafka_integration.pull_produced_bids()

            # One Bid pulled from 'bids' Kafka topic
            if len(bids_from_kafka) == 1:
                extracted_bid = bids_from_kafka[0]
                logging.info(f"Consumed and deserialized bid: {extracted_bid}")

                assert extracted_bid.id == TestBidProduced.bid_id
                assert extracted_bid.owner_id == TestBidProduced.lender_user_id
                assert str(extracted_bid.bid_interest) == str(test_bid_interest_10)
                assert extracted_bid.target_offer_id == TestBidProduced.offer_id
                assert extracted_bid.status == Bid.BidStatuses.PLACED.value
                assert extracted_bid.date_added

            # Several bids pulled from 'bids' Kafka topic, need to find the placed bid by ID
            else:
                found_bid_flag = False

                for extracted_bid in bids_from_kafka:
                    if extracted_bid.id == TestBidProduced.bid_id:
                        found_bid_flag = True
                        assert extracted_bid.owner_id == TestBidProduced.lender_user_id
                        assert str(extracted_bid.bid_interest) == str(test_bid_interest_10)
                        assert extracted_bid.target_offer_id == TestBidProduced.offer_id
                        assert extracted_bid.status == Bid.BidStatuses.PLACED.value
                        assert extracted_bid.date_added

                assert found_bid_flag, "Placed bid is missing in 'bids' Kafka topic"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)

        logging.info(f"----------------------- Pulled Bid Message Validation - "
                     f"step passed ----------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)
