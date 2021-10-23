from kafka import KafkaConsumer
import logging
from credittomodels import protobuf_handler


try:
    from Config.base_config import BaseConfig
except ModuleNotFoundError:
    from ..Config.base_config import BaseConfig

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

        # An array of Offers
        result = []

        consumer = KafkaConsumer(BaseConfig.OFFERS_TOPIC, bootstrap_servers=BaseConfig.BOOTSTRAP_SERVERS,
                                 auto_offset_reset='earliest', enable_auto_commit=True, group_id="func_tests")

        polled_messages = consumer.poll(timeout_ms=BaseConfig.PULLING_TIMEOUT)

        for p in polled_messages:
            for msg in polled_messages[p]:
                received_offer = proto_handler.deserialize_proto_to_offer(msg.value)

                if received_offer is False:
                    logging.critical("Invalid message in detected in 'offers' Kafka topic!")
                    return False

                result.append(received_offer)

        consumer.close()
        return result

    def pull_produced_bids(self):
        """
        This method can be used to pull all available and unread messages from 'bids' Kafka topic.
        Returns a list of 'Bid' objects. If the content of the pulled message can't be deserialized
        to a 'Bid' the method returns false. Empty list is returned if no messages were pulled.
        :return: list of 'Bids'
        """

        # An array of Bids
        result = []

        consumer = KafkaConsumer(BaseConfig.BIDS_TOPIC, bootstrap_servers=BaseConfig.BOOTSTRAP_SERVERS,
                                 auto_offset_reset='earliest', enable_auto_commit=True, group_id="func_tests")

        polled_messages = consumer.poll(timeout_ms=BaseConfig.PULLING_TIMEOUT)

        for p in polled_messages:
            for msg in polled_messages[p]:
                received_bid = proto_handler.deserialize_proto_to_bid(msg.value)

                if received_bid is False:
                    logging.critical("Invalid message in detected in 'bids' Kafka topic!")
                    return False

                result.append(received_bid)

        consumer.close()
        return result

    def pull_produced_matches(self):
        """
        This method can be used to pull all available and unread messages from 'matches' Kafka topic.
        Returns a list of 'Match' objects. If the content of the pulled message can't be deserialized
        to a 'Match' the method returns false. Empty list is returned if no messages were pulled.
        :return: list of 'Matches'
        """

        # An array of Matches
        result = []

        consumer = KafkaConsumer(BaseConfig.MATCHES_TOPIC, bootstrap_servers=BaseConfig.BOOTSTRAP_SERVERS,
                                 auto_offset_reset='earliest', enable_auto_commit=True, group_id="func_tests")

        polled_messages = consumer.poll(timeout_ms=BaseConfig.PULLING_TIMEOUT)

        for p in polled_messages:
            for msg in polled_messages[p]:
                received_match = proto_handler.deserialize_proto_to_match(msg.value)

                if received_match is False:
                    logging.critical("Invalid message in detected in 'matches' Kafka topic!")
                    return False

                result.append(received_match)

        consumer.close()
        return result

if __name__ == '__main__':
    kfi = KafkaIntegration()
    a = kfi.pull_produced_bids()
    print(a)
    print(len(a))

    for i in a:
        print(i)
        print("\n")