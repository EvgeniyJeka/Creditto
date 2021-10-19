from credittomodels import Offer
import pytest
import logging

try:
    from Requests import postman
    from Tools import KafkaIntegration

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import KafkaIntegration

logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
kafka_integration = KafkaIntegration.KafkaIntegration()

test_offer_owner_1 = 1024
test_offer_interest_low = 0.05
test_sum = 20000
test_duration = 24


test_token = '1Aa@<>12'


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

    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    def test_placing_offer(self, set_matching_logic):
        response = postman.gateway_requests.place_offer(test_offer_owner_1, test_sum,
                                                        test_duration, test_offer_interest_low, 0)

        TestOffersProduced.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_offer_from_kafka(self):
        offers_from_kafka = kafka_integration.pull_produced_offers()

        # One Offer pulled from 'offers' Kafka topic
        if len(offers_from_kafka) == 1:
            extracted_offer = offers_from_kafka[0]
            logging.info(f"Consumed and deserialized bid: {extracted_offer}")

            assert extracted_offer.id == TestOffersProduced.offer_id
            assert extracted_offer.owner_id == test_offer_owner_1
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

                    assert extracted_offer.owner_id == test_offer_owner_1
                    assert str(extracted_offer.offered_interest) == str(test_offer_interest_low)
                    assert extracted_offer.sum == test_sum
                    assert extracted_offer.status == Offer.OfferStatuses.OPEN.value
                    assert extracted_offer.duration == test_duration
                    assert extracted_offer.matching_bid == 0
                    assert extracted_offer.date_added

            assert found_offer_flag, "Placed offer is missing in 'offers' Kafka topic"

        logging.info(f"----------------------- Pulled Offer Message Validation - "
                     f"step passed ----------------------------------\n")
