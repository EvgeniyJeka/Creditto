from kafka import KafkaConsumer
import simplejson
from kafka.admin import KafkaAdminClient, NewTopic
import logging

from SqlWriter.sql_writer import SqlWriter
from models.Match import Match
from models.Offer import Offer
from models.Bid import Bid
from statuses import Types, OfferStatuses

logging.basicConfig(level=logging.INFO)



class ConsumerToSql(object):

    def __init__(self):
        logging.info("ConsumerToSql: Initiate ConsumerToSql instance")
        self.sql_writer = SqlWriter()

        logging.info("ConsumerToSql: Verifying essential topics, starting main consumer")
        self.start_consumer()

        self.consume_write()

    def start_consumer(self):
        # Creating Kafka topics or adding if the topic is missing
        admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092", client_id='test')
        existing_topics = admin_client.list_topics()

        required_topics = ("offers", "bids", "matches")
        topic_list = [NewTopic(name=x, num_partitions=1, replication_factor=1) for x in required_topics
                      if x not in existing_topics]

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Existing topics: {admin_client.list_topics()}")

        # Initiating consumer
        self.consumer = KafkaConsumer('offers', 'bids', 'matches', bootstrap_servers=['localhost:9092'],
                                      auto_offset_reset='earliest', enable_auto_commit=True, group_id="sql_consumer")




    def consume_write(self):
        for msg in self.consumer:
            message_content = msg.value.decode('utf-8')
            object_content = simplejson.loads(simplejson.loads(message_content))
            print(object_content)
            logging.info(f"ConsumerToSql: Received message {object_content}")

            try:
                if object_content['type'] == Types.OFFER.value:
                    logging.info("ConsumerToSql: Processing OFFER")

                    added_offer = Offer(object_content['id'],
                                        object_content['owner_id'],
                                        object_content['sum'],
                                        object_content['duration'],
                                        object_content['offered_interest'],
                                        object_content['allow_partial_fill'],
                                        object_content['date_added'],
                                        object_content['status'])

                    self.sql_writer.insert_offer(added_offer)

                elif object_content['type'] == Types.BID.value:
                    logging.info("ConsumerToSql: Processing BID")

                    added_bid = Bid(object_content['id'],
                                    object_content['owner_id'],
                                    object_content['bid_interest'],
                                    object_content['target_offer_id'],
                                    object_content['partial_only'],
                                    date_added=object_content['date_added'],
                                    status=object_content['status'])

                    self.sql_writer.insert_bid(added_bid)

                elif object_content['type'] == Types.MATCH.value:
                    logging.info("ConsumerToSql: Processing MATCH")

                    added_match = Match(object_content['offer_id'],
                                        object_content['bid_id'],
                                        object_content['offer_owner_id'],
                                        object_content['bid_owner_id'],
                                        object_content['match_time'],
                                        object_content['partial'])

                    self.sql_writer.insert_match(added_match)
                    self.sql_writer.update_offer_status_sql(object_content['offer_id'], OfferStatuses.MATCHED.value)
                    # Update status - matched bid
                    # Update status - all other bids on matched offer

            except KeyError as e:
                logging.critical(f"Consumer To SQL: INVALID kafka message received: {object_content}")
                logging.critical(f"Consumer To SQL: {e}")



if __name__ == "__main__":
    # Initiating component responsible for saving data to SQL DB
    sql_consumer = ConsumerToSql()