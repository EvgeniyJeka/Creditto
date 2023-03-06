from credittomodels import Offer
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

test_id = 101
test_file_name = os.path.basename(__file__)


@pytest.mark.container
@pytest.mark.functional
@pytest.mark.kafka
@pytest.mark.incremental
class TestOffersProduced(object):
    """
    In those tests we verify that:
    1. Gateway service produces valid serialized 'Offer' messages to 'offers' Kafka topic when new offer is placed.
    2. Produced messages can be consumed and deserialized to an 'Offer' instance
    3. Produced message content is verified against the original offer placement request
    """

    offer_id = 0
    borrower_user_id = 0

    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer(self, set_matching_logic, get_authorized_borrowers):
        try:
            borrower = get_authorized_borrowers[0]

            response = postman.gateway_requests.place_offer(borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest_low, 0, borrower.jwt_token)

            TestOffersProduced.offer_id = response['offer_id']
            TestOffersProduced.borrower_user_id = borrower.user_id
            logging.info(f"Offer placement: response received {response}")

            assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
            assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_offer_from_kafka(self):
        try:
            offers_from_kafka = kafka_integration.pull_produced_offers()

            # One Offer pulled from 'offers' Kafka topic
            if len(offers_from_kafka) == 1:
                extracted_offer = offers_from_kafka[0]
                logging.info(f"Consumed and deserialized bid: {extracted_offer}")

                assert extracted_offer.id == TestOffersProduced.offer_id
                assert extracted_offer.owner_id == TestOffersProduced.borrower_user_id
                assert str(extracted_offer.offered_interest) == str(test_offer_interest_low)
                assert extracted_offer.sum == test_sum
                assert extracted_offer.status == Offer.OfferStatuses.OPEN.value
                assert extracted_offer.duration == test_duration
                assert extracted_offer.matching_bid == 0
                assert extracted_offer.date_added

                # Several offers pulled from 'offers' Kafka topic, need to find the placed offer by ID
            else:
                found_offer_flag = False

                for extracted_offer in offers_from_kafka:
                    if extracted_offer.id == TestOffersProduced.offer_id:
                        found_offer_flag = True

                        assert extracted_offer.owner_id == TestOffersProduced.borrower_user_id
                        assert str(extracted_offer.offered_interest) == str(test_offer_interest_low)
                        assert extracted_offer.sum == test_sum
                        assert extracted_offer.status == Offer.OfferStatuses.OPEN.value
                        assert extracted_offer.duration == test_duration
                        assert extracted_offer.matching_bid == 0
                        assert extracted_offer.date_added

                assert found_offer_flag, "Placed offer is missing in 'offers' Kafka topic"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Pulled Offer Message Validation - "
                     f"step passed ----------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)
