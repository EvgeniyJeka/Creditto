
from kafka import KafkaConsumer
import json

from kafka.admin import KafkaAdminClient, NewTopic





class SqlWriter(object):

    def __init__(self):
        print("Connecting to SQL")
        print("Validating/creating SQL tables")

        # Creating Kafka topics or adding if the topic is missing
        admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092", client_id='test')
        existing_topics = admin_client.list_topics()

        required_topics = ("offers", "bids", "matches")
        topic_list = [ NewTopic(name=x, num_partitions=1, replication_factor=1) for x in required_topics
                      if x not in existing_topics]

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Existing topics: {admin_client.list_topics()}")


        # Initiating consumer
        self.consumer = KafkaConsumer('offers', bootstrap_servers = ['localhost:9092'], auto_offset_reset = 'earliest',
                                 enable_auto_commit=True, group_id = "sql_consumer")


        # Need to consume from 2 topics!


    def consume_write(self):
        for msg in self.consumer:
            #print(msg)
            message_content = msg.value.decode('utf-8')
            object_content = json.loads(message_content)
            print(object_content)



