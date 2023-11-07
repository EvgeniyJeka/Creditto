from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import logging

from SqlBasic import SqlBasic
from credittomodels import statuses
from local_config import KafkaConfig

from credittomodels import protobuf_handler

logging.basicConfig(level=logging.INFO)

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler


class ConsumerToMessenger(object):

    def __init__(self):

        self.consumer = None
        self.db_manager = SqlBasic()

        logging.info("ConsumerToMessenger: Verifying essential topics, starting main consumer")
        self.start_consumer()
        self.consume_process()


    def start_consumer(self):
        """
        Creating Kafka client. Verifying all required topics exist, creating missing topics if required.
        Starting consumer, subscribing to 'matches' topic
        :return:
        """

        # Creating Kafka topics or adding if the topic is missing
        admin_client = KafkaAdminClient(bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS.value, client_id='messenger')
        existing_topics = admin_client.list_topics()

        required_topics = ("offers", "bids", "matches")
        topic_list = [NewTopic(name=x, num_partitions=1, replication_factor=1) for x in required_topics
                      if x not in existing_topics]

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        logging.info(f"Existing topics: {admin_client.list_topics()}")

        # Initiating consumer
        self.consumer = KafkaConsumer('matches', bootstrap_servers=[KafkaConfig.BOOTSTRAP_SERVERS.value],
                                    auto_offset_reset='earliest', enable_auto_commit=True, group_id="messenger_consumer")

    def extract_message_type(self, kafka_message):
        """
        Extracting kafka message type from record headers.
        :param kafka_message: consumed kafka record, serialized
        :return: message type on success, False on failure (invalid message, no headers e.t.c.)
        """
        if kafka_message.headers is None or len(kafka_message.headers) < 1:
            logging.warning("ConsumerToMessenger: Kafka message with no valid metadata, no message type in header")
            return False

        message_header = kafka_message.headers[0]
        if message_header[0] == 'type':
            return message_header[1].decode('utf-8')

        else:
            logging.warning("ConsumerToMessenger: No message type in header")
            return False

    def consume_process(self):
        """
        Iterating over consumed messages and handling them according to message type.
        Skipping invalid messages.
        Consumed matches are handled:
        1. Email is sent to the borrower (Offer owner)
        2. Email is sent to the lender (Bid owner)
        :return:
        """
        for msg in self.consumer:
            message_type = self.extract_message_type(msg)
            if not message_type:
                logging.warning("ConsumerToMessenger: Received a message with no valid type in headers, skipping.")

            message_content = msg.value
            logging.info(f"ConsumerToMessenger: Received message {message_content}")

            if message_type == statuses.Types.MATCH.value:
                logging.info("ConsumerToMessenger: Processing MATCH")

                received_match = proto_handler.deserialize_proto_to_match(msg.value)
                logging.info(f"ConsumerToMessenger: match received - {received_match}")
                borrower_notified = self.notify_borrower(received_match)



                # self.matcher.add_offer(received_offer)

    def notify_borrower(self, received_match):
        borrower_data = self.db_manager.get_user_name_by_id(received_match.offer_owner_id)[0]
        logging.info(f"ConsumerToMessenger: Notifying borrower {borrower_data['username']} on match. ")


if __name__ == "__main__":
    # Initiating component responsible for sending emails (and other messages if required)
    matcher_consumer = ConsumerToMessenger()

    # borrower_template = "Greetings! \n Dear %borrower_name%, we are pleased to inform you, that your offer %offer_id% " \
    #                     "was matched with bid %bid_id%, and $%loan_sum% will be transferred to your account in the next 24 hours.\n" \
    #                     "The loan interest will be %loan_interest% and the monthly payment will be %monthly_payment% - you" \
    #                     "will pass it to the lender, %lender_name% each month until the loan is closed.\n" \
    #                     "Have a nice day!"
    #
    # borrower_template = borrower_template.replace('%borrower_name%','Karl')
    # borrower_template = borrower_template.replace('%loan_sum%', '1200')
    #
    # print(borrower_template)

    # with open("template_borrower.txt", "r") as f:
    #     borrower_template = f.read()
    #
    # print(borrower_template)