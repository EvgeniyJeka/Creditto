import pytest
import logging
from decimal import Decimal

try:
    from Requests import postman
    from Tools import KafkaIntegration

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import KafkaIntegration

from credittomodels.utils import Calculator as Calculator

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
kafka_integration = KafkaIntegration.KafkaIntegration()

# Move config to SQL
TAIL_DIGITS = 4

test_offer_owner = 1312
test_offer_interest = 0.06

test_sum = 5000
test_duration = 13

test_bid_owner_1 = 911
test_bid_owner_2 = 582
test_bid_owner_3 = 781
test_bid_owner_4 = 343
test_bid_owner_5 = 216

test_bid_owners_list = [test_bid_owner_1, test_bid_owner_2, test_bid_owner_3, test_bid_owner_4, test_bid_owner_5]
test_bid_interest = 0.056

test_token = '1Aa@<>12'


@pytest.mark.container
@pytest.mark.functional
class TestMatchProduced(object):
    """
       In those tests we verify that:
       1. Matcher service produces valid serialized 'Match' messages to 'matches' Kafka topic when new match is created.
       2. Produced messages can be consumed and deserialized to a 'Match' instance
       3. Produced message content is verified against the expected match params (basing on placed offer and bid data)
    """

    match_input = {'offer_owner': test_offer_owner, 'offer_sum': test_sum, 'offer_duration': test_duration,
                   'offer_interest': test_offer_interest, 'bid_owners_list': test_bid_owners_list,
                   'bid_interest': test_bid_interest, 'offer_owner_token': test_token}

    @pytest.mark.parametrize('match_ready', [[match_input]], indirect=True)
    def test_match_from_kafka(self, match_ready):

        monthly_payment = Calculator.calculate_monthly_payment(Decimal(test_sum), Decimal(test_bid_interest),
                                                               Decimal(test_duration), TAIL_DIGITS)


        matches_from_kafka = kafka_integration.pull_produced_matches()

        # One Match pulled from 'matches' Kafka topic
        if len(matches_from_kafka) == 1:
            extracted_match = matches_from_kafka[0]
            print(f"Consumed and deserialized match: {extracted_match}")

            assert extracted_match.offer_id == self.offer_id
            assert extracted_match.bid_id == self.bid_id
            assert extracted_match.offer_owner_id == test_offer_owner

            assert extracted_match.bid_owner_id == test_bid_owner_1
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
                    assert extracted_match.offer_owner_id == test_offer_owner

                    assert extracted_match.bid_owner_id == test_bid_owner_1
                    assert Decimal(extracted_match.sum) == Decimal(test_sum)
                    assert extracted_match.final_interest == test_bid_interest

                    assert Decimal.__round__(Decimal(extracted_match.monthly_payment), TAIL_DIGITS) == monthly_payment

            assert found_match_flag, "Placed bid is missing in 'bids' Kafka topic"

        logging.info(f"----------------------- Pulled Match Message Validation - "
                     f"step passed ----------------------------------\n")
