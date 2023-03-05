import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

class SlackResultsReporter:

    def send_report(self, data):
        # Set the Slack API token and channel name
        client = WebClient(token=os.environ['SLACK_API_TOKEN'])
        channel_name = os.environ['SLACK_RESULTS_REPORTING_CHANNEL_NAME']

        # Send a message to the specified Slack channel
        try:
            response = client.chat_postMessage(
                channel=channel_name,
                text=data
            )
            logging.info("Test Result Published To Slack Channel Successfully: ", response)
        except SlackApiError as e:
            logging.error("Error sending message: ", e)

    def report_success(self, test_id, test_file_name):
        pass

    def report_failure(self, test_id, test_file_name):
        pass

    def report_broken_test(self, test_id, test_file_name):
        pass


