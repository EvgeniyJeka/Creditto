import json
from kafka import KafkaProducer
import time
import logging
logging.basicConfig(level=logging.INFO)
from local_config import KafkaConfig


# producer = KafkaProducer(value_serializer = lambda m: json.dumps(m).encode('utf-8'), bootstrap_servers = ['localhost:9092'])
# for x in range(1,15):
#     print(producer.send('t2', value={"beat":x}))
#     producer.flush()
#     time.sleep(0.01)

class ProducerFromApi(object):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=[KafkaConfig.BOOTSTRAP_SERVERS.value])

    # headers (optional): a list of header key value pairs. List items
    #                 are tuples of str key and bytes value.

    def produce_message(self, message, topic, headers=None):
        logging.info(f"ProducerFromApi: Producing message {message} to topic {topic}")
        if headers:
            self.producer.send(topic, value=message, headers=headers)
        else:
            self.producer.send(topic, value=message)

        self.producer.flush()
        time.sleep(0.01)
        logging.info(f"ProducerFromApi: Succssfully produced message {message} to topic {topic}")