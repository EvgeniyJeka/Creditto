from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import logging, os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from SqlBasic import SqlBasic
from credittomodels import statuses
from local_config import KafkaConfig, EmailConfig

from credittomodels import protobuf_handler

logging.basicConfig(level=logging.INFO)

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler


class ConsumerToMessenger(object):

    def __init__(self):

        self.consumer = None
        self.db_manager = SqlBasic()

        self.email_app_password = os.getenv("EMAIL_APP_PASSWORD")
        self.sender_name = os.getenv("SENDER_NAME")
        self.email_app_login = os.getenv("EMAIL_APP_LOGIN")

        if self.email_app_password is None or self.sender_name is None:
            self.email_app_password = EmailConfig.APP_PASSWORD.value
            self.sender_name = EmailConfig.SENDER_NAME.value
            self.email_app_login = EmailConfig.APP_LOGIN.value

        if len(self.email_app_password) < 3:
            logging.error("ConsumerToMessenger: - no valid email app password provided")

        else:
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
                # lender_notified = self.notify_lender(received_match)
                # if borrower_notified and lender_notified:
                #     logging.info("ConsumerToMessenger: both parties were notified via email")

    def notify_borrower(self, received_match):
        """
        This method is used to notify the borrower on the match.
        Data from the received match are inserted into the template, data is fetched from SQL DB
        and an email with a notification is sent to the borrower.
        :param received_match: Match instance
        :return: True on success
        """

        try:
            # Fetching the relevant data from SQL - it will be inserted into the template
            borrower_data = self.db_manager.get_user_name_by_id(received_match.offer_owner_id)[0]
            logging.info(f"ConsumerToMessenger: Notifying borrower {borrower_data['username']} on match. ")

            lender_data = self.db_manager.get_user_name_by_id(received_match.bid_owner_id)[0]
            offer_data = self.db_manager.get_offer_data_alchemy(received_match.offer_id)[0]
            borrower_email = borrower_data['user_email']

        except IndexError as e:
            logging.error(f"ConsumerToMessenger: failed to fetch data from DB: {e}")
            return

        with open("template_borrower.txt", "r") as f:
            borrower_template = f.read()

        # Filling the template
        borrower_template = borrower_template.replace("%borrower_name%", borrower_data['username'])
        borrower_template = borrower_template.replace("%offer_id%", str(received_match.offer_id))
        borrower_template = borrower_template.replace("%bid_id%", str(received_match.bid_id))
        borrower_template = borrower_template.replace("%loan_sum%", str(received_match.sum))
        borrower_template = borrower_template.replace('%loan_interest%', str(round(received_match.final_interest * 100, 4)))
        borrower_template = borrower_template.replace("%monthly_payment%", str(received_match.monthly_payment))
        borrower_template = borrower_template.replace('%lender_name%', lender_data['username'])
        borrower_template = borrower_template.replace("%loan_duration%", str(offer_data['duration']))

        result = self.send_email(self.sender_name, borrower_email, "Loan approved", borrower_template)

        if not result:
            logging.error(f"ConsumerToMessenger: failed to email {borrower_data['username']} - {borrower_email}")

        logging.info(f"ConsumerToMessenger: notified the borrower {borrower_data['username']} "
                     f"that his offer {received_match.offer_id} ")
        return True

    def send_email(self, sender_email, receiver_email, subject, message):
        """
        This method is used to send emails. Email app password and login are taken from instance variables
        (initiate in constructor).
        :param sender_email: str
        :param receiver_email: must be valid email address
        :param subject: str
        :param message: str
        :return:
        """

        try:
            logging.info(f"Emailing {receiver_email} - {message}")

            # Create a MIMEText object for the email content
            text = MIMEText(message)

            # Create a MIMEMultipart object to represent the email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            # Attach the text content to the email
            msg.attach(text)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            # GMAIL APP PASSWORD IS REQUIRED HERE
            server.login(self.email_app_login, self.email_app_password)

            # Send the email
            server.sendmail(sender_email, receiver_email, msg.as_string())

            # Close the SMTP server session
            server.quit()
            return True

        except Exception as e:
            logging.error(f"ConsumerToMessenger: failed to send email - {e}")
            return False



if __name__ == "__main__":
    # Initiating component responsible for sending emails (and other messages if required)
    matcher_consumer = ConsumerToMessenger()

