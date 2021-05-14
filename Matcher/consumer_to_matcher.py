
from kafka import KafkaConsumer
import json
from kafka.admin import KafkaAdminClient, NewTopic
import logging

from matcher import Matcher
from models.Offer import Offer
from models.Bid import Bid
from statuses import Types
from local_config import Config


logging.basicConfig(level=logging.INFO)

# Create one 'matcher' instance
# Create one 'producer_from_matcher' instance

# Once new Offer is received:
    #Call matcher.add_offer method

#Once new Bid is received:
    #Call matcher.add_bid method
    # If response = True - see it as confirmation
    # Else if response = Match object:
        #call producer_from_matcher.send and send the received Match object to 'matches' Kafka topic




class ConsumerToMatcher(object):

    def __init__(self):

        self.matcher = Matcher()

        logging.info("ConsumerToMatcher: Verifying essential topics, starting main consumer")
        self.start_consumer()

        self.consume_process()

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
        self.consumer = KafkaConsumer('offers', 'bids', bootstrap_servers=[Config.kafka_bootstrap_servers.value],
                                    auto_offset_reset='earliest', enable_auto_commit=True, group_id="matcher_consumer")


    def consume_process(self):
        for msg in self.consumer:
            message_content = msg.value.decode('utf-8')
            object_content = json.loads(json.loads(message_content))
            print(object_content)
            logging.info(f"ConsumerToSql: Received message {object_content}")

            if object_content['type'] == Types.OFFER.value:
                logging.info("ConsumerToMatcher: Processing OFFER")

                received_offer = Offer(object_content['id'],
                                    object_content['owner_id'],
                                    object_content['sum'],
                                    object_content['duration'],
                                    object_content['offered_interest'],
                                    object_content['allow_partial_fill'],
                                    object_content['date_added'],
                                    object_content['status'])

                self.matcher.add_offer(received_offer)



            elif object_content['type'] == Types.BID.value:
                logging.info("ConsumerToMatcher: Processing BID")

                received_bid = Bid(object_content['id'],
                                object_content['owner_id'],
                                object_content['bid_interest'],
                                object_content['target_offer_id'],
                                object_content['partial_only'],
                                date_added=object_content['date_added'],
                                status=object_content['status'])

if __name__ == "__main__":
    # Initiating component responsible for saving data to SQL DB
    matcher_consumer = ConsumerToMatcher()