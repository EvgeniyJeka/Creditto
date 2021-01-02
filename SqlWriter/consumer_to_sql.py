from kafka import KafkaConsumer
import json
import logging
from kafka.admin import KafkaAdminClient, NewTopic
import logging

from SqlWriter.sql_writer import SqlWriter
from models.Offer import Offer
from statuses import Types

logging.basicConfig(level=logging.INFO)



class ConsumerToSql(object):

    def __init__(self):
        print("ConsumerToSql: Initiate ConsumerToSql instance")
        self.sql_writer = SqlWriter()


        # Creating Kafka topics or adding if the topic is missing
        admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092", client_id='test')
        existing_topics = admin_client.list_topics()

        required_topics = ("offers", "bids", "matches")
        topic_list = [ NewTopic(name=x, num_partitions=1, replication_factor=1) for x in required_topics
                      if x not in existing_topics]

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Existing topics: {admin_client.list_topics()}")


        # Initiating consumer
        self.consumer = KafkaConsumer('offers', 'bids', 'matches', bootstrap_servers = ['localhost:9092'],
                                      auto_offset_reset = 'earliest', enable_auto_commit=True, group_id="sql_consumer")

        self.consume_write()



    def consume_write(self):
        for msg in self.consumer:
            message_content = msg.value.decode('utf-8')
            object_content = json.loads(json.loads(message_content))
            print(object_content)
            logging.info(f"ConsumerToSql: Received message {object_content}")

            # def __init__(self, owner_id, sum, duration, offered_interest, allow_partial_fill, date_added=None,
            #              status=None):

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






if __name__ == "__main__":
    # Initiating component responsible for saving data to SQL DB
    sql_consumer = ConsumerToSql()