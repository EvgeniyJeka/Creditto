import configparser
import os


def get_parser(config):
    parser = configparser.ConfigParser()
    with open(config, mode='r', buffering=-1, closefd=True):
        parser.read(config)
        return parser

class BaseConfig(object):

    config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')
    parser = get_parser(config_file)
    print(os.getcwd())

    # Running locally
    if os.getenv('BASE_URL') is None:
        BASE_URL = parser.get('URL', 'base_url')
        SQL_HOST = parser.get('SQL_DB', 'host')
        SQL_USER = parser.get('SQL_DB', 'user')
        SQL_PASSWORD = parser.get('SQL_DB', 'password')
        SQL_DB_NAME = 'creditto'
        WAIT_BEFORE_TIMEOUT = int(parser.get('URL', 'WAIT_BEFORE_TIMEOUT'))

    # Running in Docker container
    else:
        BASE_URL = os.getenv('BASE_URL')
        SQL_HOST = os.getenv('SQL_HOST')
        SQL_USER = os.getenv('SQL_USER')
        SQL_PASSWORD = os.getenv('SQL_PASSWORD')
        SQL_DB_NAME = 'creditto'
        WAIT_BEFORE_TIMEOUT = int(os.getenv('WAIT_BEFORE_TIMEOUT'))

    BOOTSTRAP_SERVERS = parser.get('KAFKA', 'bootstrap_servers')
    OFFERS_TOPIC = parser.get('KAFKA', 'offers_topic')
    BIDS_TOPIC = parser.get('KAFKA', 'bids_topic')
    MATCHES_TOPIC = parser.get('KAFKA', 'matches_topic')

    PULLING_TIMEOUT = int(parser.get('KAFKA', 'pulling_timeout'))


if __name__ == '__main__':
    bc = BaseConfig()
    print(bc.BASE_URL)