import simplejson
from kafka import KafkaProducer
import time
import logging
logging.basicConfig(level=logging.INFO)
from local_config import Config



class ProducerFromMatcher(object):

    def __init__(self):
        self.producer = KafkaProducer(value_serializer = lambda m: simplejson.dumps(m).encode('utf-8'),
                                      bootstrap_servers = [Config.kafka_bootstrap_servers.value])


    def produce_message(self, message, topic):
        logging.info(f"ProducerFromApi: Producing message {message} to topic {topic}")
        result = self.producer.send(topic, value=message)
        self.producer.flush()
        time.sleep(0.01)
        logging.info(f"ProducerFromApi: Succssfully produced message {message} to topic {topic}")