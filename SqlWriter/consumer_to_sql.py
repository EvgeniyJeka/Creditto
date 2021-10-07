from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import logging

from sql_writer import SqlWriter
from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from credittomodels import statuses
from local_config import KafkaConfig

from credittomodels import protobuf_handler


logging.basicConfig(level=logging.INFO)

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler


class ConsumerToSql(object):

    def __init__(self):
        logging.info("ConsumerToSql: Initiate ConsumerToSql instance")
        self.sql_writer = SqlWriter()

        logging.info("ConsumerToSql: Verifying essential topics, starting main consumer")
        self.start_consumer()

        self.consume_write()

    def start_consumer(self):
        # Creating Kafka topics or adding if the topic is missing
        admin_client = KafkaAdminClient(bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS.value, client_id='test')
        existing_topics = admin_client.list_topics()

        required_topics = ("offers", "bids", "matches")
        topic_list = [NewTopic(name=x, num_partitions=1, replication_factor=1) for x in required_topics
                      if x not in existing_topics]

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Existing topics: {admin_client.list_topics()}")

        # Initiating consumer
        self.consumer = KafkaConsumer('offers', 'bids', 'matches', bootstrap_servers=[KafkaConfig.BOOTSTRAP_SERVERS.value],
                                      auto_offset_reset='earliest', enable_auto_commit=True, group_id="sql_consumer")

    def extract_message_type(self, kafka_message):
        if kafka_message.headers is None or len(kafka_message.headers) < 1:
            logging.warning("Matcher Consumer: Kafka message with no valid metadata, no message type in header")
            return False

        message_header = kafka_message.headers[0]
        if message_header[0] == 'type':
            return message_header[1].decode('utf-8')

        else:
            logging.warning("Matcher Consumer: No message type in header")
            return False


    def consume_write(self):
        for msg in self.consumer:

            print(f"Extracted message type: {self.extract_message_type(msg)}")

            message_type = self.extract_message_type(msg)
            if not message_type:
                logging.warning("Matcher Consumer: Received a message with no valid type in headers, skipping.")

            message_content = msg.value
            # object_content = simplejson.loads(simplejson.loads(message_content))
            # print(object_content)
            logging.info(f"ConsumerToSql: Received message {message_content}")

            try:
                if message_type == statuses.Types.OFFER.value:
                    logging.info("ConsumerToSql: Processing OFFER")

                    added_offer = proto_handler.deserialize_proto_to_offer(msg.value)

                    # T.B.D. - Add handling for incoming offer with status CANCELLED (update DB, change status)
                    self.sql_writer.insert_offer(added_offer)

                elif message_type == statuses.Types.BID.value:
                    logging.info("ConsumerToSql: Processing BID")

                    added_bid = proto_handler.deserialize_proto_to_bid(msg.value)
                    self.sql_writer.insert_bid(added_bid)

                elif message_type == statuses.Types.MATCH.value:
                    logging.info("ConsumerToSql: Processing MATCH")

                    added_match = proto_handler.deserialize_proto_to_match(msg.value)

                    # Inserting match record, updating matched offer , matched bid and unmatched bids statuses
                    self.sql_writer.insert_match(added_match)

                    self.sql_writer.update_offer_status_sql(added_match.offer_id, statuses.OfferStatuses.MATCHED.value)
                    self.sql_writer.update_offer_final_interest_sql(added_match.offer_id, added_match.final_interest)

                    self.sql_writer.update_bid_status_sql(added_match.bid_id, statuses.BidStatuses.MATCHED.value)
                    self.sql_writer.cancel_remaining_bids_sql(added_match.offer_id, added_match.bid_id,)

            # Change the exception logic or remove try/catch
            except KeyError as e:
                logging.critical(f"Consumer To SQL: INVALID kafka message received: {msg.value}")
                logging.critical(f"Consumer To SQL: {e}")



if __name__ == "__main__":
    # Initiating component responsible for saving data to SQL DB
    sql_consumer = ConsumerToSql()