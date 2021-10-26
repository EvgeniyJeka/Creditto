from enum import Enum


class DockerContainerNames(Enum):

    GATEWAY = 'creditto_creditto_gateway_1'
    MATCHER = 'creditto_creditto_matcher_1'
    SQL_WRITER = 'creditto_sql_writer_1'
    TESTS_CONTAINER = 'creditto_sanity_tests_container_1'
    KAFKA = 'kafka'
    ZOOKEEPER = 'zookeeper'
    MYSQL = 'creditto_cabin_db_1'
