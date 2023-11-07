from enum import Enum


class SqlConfig(Enum):
    #SQL_HOST = "creditto_cabin_db_1"
    SQL_HOST = "127.0.0.1"
    SQL_PORT = ""
    SQL_USER = 'root'
    SQL_PASSWORD = '123456'
    DB_NAME ='creditto'

class KafkaConfig(Enum):
    BOOTSTRAP_SERVERS = "kafka:9092"


class WebConfig(Enum):
    RUN_ON_HOST = ""