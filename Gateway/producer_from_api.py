import json
from kafka import KafkaProducer
import time
import logging
from local_config import Config
logging.basicConfig(level=logging.INFO)


# producer = KafkaProducer(value_serializer = lambda m: json.dumps(m).encode('utf-8'), bootstrap_servers = ['localhost:9092'])
# for x in range(1,15):
#     print(producer.send('t2', value={"beat":x}))
#     producer.flush()
#     time.sleep(0.01)

class ProducerFromApi(object):

    def __init__(self):
        # self.producer = KafkaProducer(value_serializer = lambda m: json.dumps(m).encode('utf-8'),
        #                               bootstrap_servers = ['localhost:9092'])
        self.producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                                      bootstrap_servers=[Config.kafka_bootstrap_servers.value])


    def produce_message(self, message, topic):
        logging.info(f"ProducerFromApi: Producing message {message} to topic {topic}")
        result = self.producer.send(topic, value=message)
        self.producer.flush()
        time.sleep(0.01)
        logging.info(f"ProducerFromApi: Succssfully produced message {message} to topic {topic}")