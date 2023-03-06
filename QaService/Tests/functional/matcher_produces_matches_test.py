import pytest
import logging
from decimal import Decimal
import os

try:
    from Requests import postman
    from Tools import KafkaIntegration, reporter, results_reporter

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import KafkaIntegration, reporter, results_reporter

from credittomodels.utils import Calculator as Calculator

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()
kafka_integration = KafkaIntegration.KafkaIntegration()
report_test_results = results_reporter.ResultsReporter()

test_offer_interest = 0.06

test_sum = 5000
test_duration = 13
test_bid_interest = 0.056

test_id = 103
test_file_name = os.path.basename(__file__)


@pytest.mark.container
@pytest.mark.functional
class TestMatchProduced(object):
    """
       In those tests we verify that:
       1. Matcher service produces valid serialized 'Match' messages to 'matches' Kafka topic when new match is created.
       2. Produced messages can be consumed and deserialized to a 'Match' instance
       3. Produced message content is verified against the expected match params (basing on placed offer and bid data)
    """

    match_input = {'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest,
                   'bid_interest': test_bid_interest}

    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_match_from_kafka(self, match_ready):
        try:

            TAIL_DIGITS = int(reporter.fetch_config_from_db('tail_digits'))

            monthly_payment = Calculator.calculate_monthly_payment(Decimal(test_sum), Decimal(test_bid_interest),
                                                                   Decimal(test_duration), TAIL_DIGITS)

            matches_from_kafka = kafka_integration.pull_produced_matches()

            # One Match pulled from 'matches' Kafka topic
            if len(matches_from_kafka) == 1:
                extracted_match = matches_from_kafka[0]
                print(f"Consumed and deserialized match: {extracted_match}")

                assert extracted_match.offer_id == self.offer_id
                assert extracted_match.bid_id == self.bid_id
                assert extracted_match.offer_owner_id == self.offer_owner_id

                assert extracted_match.bid_owner_id == self.bid_owner_id
                assert Decimal(extracted_match.sum) == Decimal(test_sum)
                assert extracted_match.final_interest == test_bid_interest

                assert Decimal.__round__(Decimal(extracted_match.monthly_payment), TAIL_DIGITS) == monthly_payment

            # Several matches pulled from 'matches' Kafka topic - finding the expected match by offer ID
            else:
                found_match_flag = False

                for extracted_match in matches_from_kafka:
                    if extracted_match.offer_id == self.offer_id:
                        found_match_flag = True

                        assert extracted_match.offer_id == self.offer_id
                        assert extracted_match.bid_id == self.bid_id
                        assert extracted_match.offer_owner_id == self.offer_owner_id

                        assert extracted_match.bid_owner_id == self.bid_owner_id
                        assert Decimal(extracted_match.sum) == Decimal(test_sum)
                        assert extracted_match.final_interest == test_bid_interest

                        assert Decimal.__round__(Decimal(extracted_match.monthly_payment), TAIL_DIGITS) == monthly_payment

                assert found_match_flag, "Placed bid is missing in 'bids' Kafka topic"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Pulled Match Message Validation - "
                     f"step passed ----------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)
