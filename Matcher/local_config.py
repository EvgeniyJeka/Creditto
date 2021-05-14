from enum import Enum

# class Config(Enum):
#     sql_port = "creditto_cabin_db_1"
#     sql_usr = 'root'
#     sql_pwd = '123456'
#     db_name = 'creditto'
#     kafka_bootstrap_servers = "kafka:9092"

class MatchingAlgorithm(Enum):
    BEST_OF_FIVE_LOWEST_INTEREST = 1


class Config(Enum):
    MIN_BIDS_EXPECTED = 5
    SELECTED_MATCHING_ALGORITHM = MatchingAlgorithm.BEST_OF_FIVE_LOWEST_INTEREST.value


class SqlConfig(Enum):
    SQL_HOST = "creditto_cabin_db_1"
    SQL_PORT = ""
    SQL_USER = 'root'
    SQL_PASSWORD = '123456'
    DB_NAME ='creditto'

class KafkaConfig(Enum):
    BOOTSTRAP_SERVERS = "kafka:9092"


class WebConfig(Enum):
    RUN_ON_HOST = ""