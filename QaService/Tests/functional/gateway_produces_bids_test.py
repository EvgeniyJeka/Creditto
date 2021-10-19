from credittomodels import Bid
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

test_bid_owner_10 = 883
test_bid_interest_10 = 0.041

test_token = '1Aa@<>12'


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
    
    @pytest.mark.parametrize('set_matching_logic', [[2]], indirect=True)
    def test_placing_offer(self, set_matching_logic):
        response = postman.gateway_requests.place_offer(test_offer_owner_1, test_sum,
                                                        test_duration, test_offer_interest_low, 0)

        TestBidProduced.offer_id = response['offer_id']
        logging.info(f"Offer placement: response received {response}")

        assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
        assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_placing_bid(self):

        response = postman.gateway_requests.\
            place_bid(test_bid_owner_10, test_bid_interest_10, self.offer_id, 0)
        logging.info(response)

        TestBidProduced.bid_id = response['bid_id']

        assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
        assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
        assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")

    def test_bid_in_kafka(self):
        bids_from_kafka = kafka_integration.pull_produced_bids()

        # One Bid pulled from 'bids' Kafka topic
        if len(bids_from_kafka) == 1:
            extracted_bid = bids_from_kafka[0]
            logging.info(f"Consumed and deserialized bid: {extracted_bid}")

            assert extracted_bid.id == TestBidProduced.bid_id
            assert extracted_bid.owner_id == test_bid_owner_10
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
                    assert extracted_bid.owner_id == test_bid_owner_10
                    assert str(extracted_bid.bid_interest) == str(test_bid_interest_10)
                    assert extracted_bid.target_offer_id == TestBidProduced.offer_id
                    assert extracted_bid.status == Bid.BidStatuses.PLACED.value
                    assert extracted_bid.date_added

            assert found_bid_flag, "Placed bid is missing in 'bids' Kafka topic"

        logging.info(f"----------------------- Pulled Bid Message Validation - "
                     f"step passed ----------------------------------\n")
