import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging


class ResultsReporter:

    def send_report_slack(self, data):
        """
        This method is used to send test run reports to the designated Slack channel.
        Slack channel name and Slack token are taken from environment variables
        :param data: report text
        :return: True on success
        """

        slack_token = os.environ['SLACK_API_TOKEN']
        slack_channel_name = os.environ['SLACK_RESULTS_REPORTING_CHANNEL_NAME']

        if not slack_token or not slack_channel_name:
            logging.error("Can't send report to Slack - token or channel name missing in environment variables")
            return False

        if not len(slack_token) > 1:
            logging.error(f"Can't send report to Slack - invalid slack token: {slack_token}")

        client = WebClient(token=slack_token)

        try:
            response = client.chat_postMessage(
                channel=slack_channel_name,
                text=data
            )
            logging.info(f"Test Result Published To Slack Channel Successfully: {response}")
            return True

        except SlackApiError as e:
            logging.error("Error sending message: ", e)
            raise e

    def report_success(self, test_id, test_file_name):
        report = f"Test PASSED : #{test_id} , {test_file_name}"
        return self.send_report_slack(report)

    def report_failure(self, test_id, test_file_name):
        report = f"Test FAILED : #{test_id} , {test_file_name}"
        return self.send_report_slack(report)

    def report_broken_test(self, test_id, test_file_name, test_broken_exception):
        report = f"Test BROKEN : #{test_id} , {test_file_name} - note the exception: {test_broken_exception}"
        return self.send_report_slack(report)


