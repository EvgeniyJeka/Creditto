from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import logging

from matcher import Matcher
from credittomodels import statuses
from local_config import KafkaConfig

from credittomodels import protobuf_handler

logging.basicConfig(level=logging.INFO)

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler


class ConsumerToMatcher(object):

    def __init__(self):

        logging.info("ConsumerToMatcher: Creating MATCHER instance")
        self.matcher = Matcher()
        self.consumer = None

        logging.info("ConsumerToMatcher: Verifying essential topics, starting main consumer")
        self.start_consumer()
        self.consume_process()

    def start_consumer(self):
        """
        Creating Kafka client. Verifying all required topics exist, creating missing topics if required.
        Starting consumer, subscribing to 'offers' and 'bids' topics
        :return:
        """

        # Creating Kafka topics or adding if the topic is missing
        admin_client = KafkaAdminClient(bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS.value, client_id='test')
        existing_topics = admin_client.list_topics()

        required_topics = ("offers", "bids", "matches")
        topic_list = [NewTopic(name=x, num_partitions=1, replication_factor=1) for x in required_topics
                      if x not in existing_topics]

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        logging.info(f"Existing topics: {admin_client.list_topics()}")

        # Initiating consumer
        self.consumer = KafkaConsumer('offers', 'bids', bootstrap_servers=[KafkaConfig.BOOTSTRAP_SERVERS.value],
                                    auto_offset_reset='earliest', enable_auto_commit=True, group_id="matcher_consumer")

    def extract_message_type(self, kafka_message):
        """
        Extracting kafka message type from record headers.
        :param kafka_message: consumed kafka record, serialized
        :return: message type on success, False on failure (invalid message, no headers e.t.c.)
        """
        if kafka_message.headers is None or len(kafka_message.headers) < 1:
            logging.warning("Matcher Consumer: Kafka message with no valid metadata, no message type in header")
            return False

        message_header = kafka_message.headers[0]
        if message_header[0] == 'type':
            return message_header[1].decode('utf-8')

        else:
            logging.warning("Matcher Consumer: No message type in header")
            return False

    def consume_process(self):
        """
        Iterating over consumed messages and handling them according to message type.
        Skipping invalid messages.
        Bids and Offers are deserialized and added to Matcher's Pool
        :return:
        """
        for msg in self.consumer:
            message_type = self.extract_message_type(msg)
            if not message_type:
                logging.warning("Matcher Consumer: Received a message with no valid type in headers, skipping.")

            message_content = msg.value
            logging.info(f"ConsumerToSql: Received message {message_content}")

            if message_type == statuses.Types.OFFER.value:
                logging.info("ConsumerToMatcher: Processing OFFER")

                received_offer = proto_handler.deserialize_proto_to_offer(msg.value)

                self.matcher.add_offer(received_offer)

            elif message_type == statuses.Types.BID.value:
                logging.info("ConsumerToMatcher: Processing BID")

                received_bid = proto_handler.deserialize_proto_to_bid(msg.value)

                self.matcher.add_bid(received_bid)

if __name__ == "__main__":
    # Initiating component responsible for saving data to SQL DB
    matcher_consumer = ConsumerToMatcher()