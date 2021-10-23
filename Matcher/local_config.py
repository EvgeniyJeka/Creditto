from enum import Enum

# class MatchingAlgorithm(Enum):
#     BEST_OF_FIVE_LOWEST_INTEREST_OLDEST = 1
#
#
# class Config(Enum):
#     MIN_BIDS_EXPECTED = 5
#     SELECTED_MATCHING_ALGORITHM = MatchingAlgorithm.BEST_OF_FIVE_LOWEST_INTEREST_OLDEST.value


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