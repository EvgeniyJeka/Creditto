from kafka import KafkaConsumer
from credittomodels import Offer
from credittomodels import Bid
import logging

from credittomodels import protobuf_handler

logging.basicConfig(level=logging.INFO)

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler

class KafkaIntegration(object):

    def pull_produced_offers(self):
        """
        This method can be used to pull all available and unread messages from 'offers' Kafka topic.
        Returns a list of 'Offer' objects. If the content of the pulled message can't be deserialized
        to an 'Offer' the method returns false. Empty list is returned if no messages were pulled.
        :return: list of 'Offers'
        """

        # An array of TradeMessage objects
        result = []

        consumer = KafkaConsumer("offers", bootstrap_servers="kafka:9092",
                                 auto_offset_reset='earliest', enable_auto_commit=True, group_id="func_tests")

        polled_messages = consumer.poll(timeout_ms=6000)

        for p in polled_messages:
            for msg in polled_messages[p]:
                message_content = msg.value
                logging.info(f"ConsumerToSql: Received message {message_content}")
                received_offer = proto_handler.deserialize_proto_to_offer(msg.value)

                if received_offer is False:
                    logging.critical("Invalid message in detected in 'offers' Kafka topic!")
                    return False

                result.append(received_offer)

        consumer.close()
        return result

if __name__ == '__main__':
    kfi = KafkaIntegration()
    print(kfi.pull_produced_offers())