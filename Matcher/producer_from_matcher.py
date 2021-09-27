import simplejson
from kafka import KafkaProducer
import time
import logging
from local_config import KafkaConfig

logging.basicConfig(level=logging.INFO)



class ProducerFromMatcher(object):

    def __init__(self):
        self.producer = KafkaProducer(value_serializer=lambda m: simplejson.dumps(m).encode('utf-8'),
                                      bootstrap_servers=[KafkaConfig.BOOTSTRAP_SERVERS.value])

    def produce_message(self, message, topic, headers=None):
        logging.info(f"ProducerFromApi: Producing message {message} to topic {topic}")
        if headers:
            self.producer.send(topic, value=message, headers=headers)
        else:
            self.producer.send(topic, value=message)

        self.producer.flush()
        time.sleep(0.01)
        logging.info(f"ProducerFromApi: Succssfully produced message {message} to topic {topic}")