from enum import Enum

class Config(Enum):
    sql_port = "creditto_cabin_db_1"
    sql_usr = 'root'
    sql_pwd = '123456'
    db_name = 'creditto'
    kafka_bootstrap_servers = "kafka:9092"

