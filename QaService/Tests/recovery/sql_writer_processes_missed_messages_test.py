import time
from credittomodels import Offer
import pytest
import logging
from decimal import Decimal
from ..conftest import container_stop, container_start
import os


try:
    from Requests import postman
    from Tools import reporter, results_reporter
    from Config.container_names import DockerContainerNames

except ModuleNotFoundError:
    from ...Requests import postman
    from ...Tools import reporter, results_reporter
    from ...Config.container_names import DockerContainerNames


logging.basicConfig(level=logging.INFO)

postman = postman.Postman()
reporter = reporter.Reporter()
report_test_results = results_reporter.ResultsReporter()

# The time given for SQL Writer component to recover after container restart
sql_writer_recovery_time = 10


test_offer_interest_low = 0.05
test_sum = 30000
test_duration = 24

MATCH_EXPECTED = 3

test_bid_interest_1 = 0.046
test_bid_interest_2 = 0.045
test_bid_interest_3 = 0.044
test_bid_interest_4 = 0.037
test_bid_interest_5 = 0.037

test_id = 604
test_file_name = os.path.basename(__file__)


@pytest.mark.recovery
@pytest.mark.incremental
class TestSqlWriterRecovery:
    """
        In those tests we verify that:
        1. SQL Writer consumes all unread messages from Kafka after restart and updates the SQL DB.
    """

    offer_id = 0
    matching_bid_id = 0
    borrower = None
    lenders = None

    bid_interest_list = [test_bid_interest_1, test_bid_interest_2, test_bid_interest_3,
                         test_bid_interest_4, test_bid_interest_5]

    sql_writer_container = None

    @pytest.mark.parametrize('set_matching_logic', [[1]], indirect=True)
    @pytest.mark.parametrize('get_authorized_borrowers', [[1]], indirect=True)
    def test_placing_offer(self, set_matching_logic, get_authorized_borrowers):
        try:

            TestSqlWriterRecovery.borrower = get_authorized_borrowers[0]

            response = postman.gateway_requests.place_offer(TestSqlWriterRecovery.borrower.user_id, test_sum,
                                                            test_duration, test_offer_interest_low, 0,
                                                            TestSqlWriterRecovery.borrower.jwt_token)

            TestSqlWriterRecovery.offer_id = response['offer_id']
            logging.info(f"Offer placement: response received {response}")

            assert 'offer_id' in response.keys(), "Offer Placement error - no OFFER ID in response"
            assert isinstance(response['offer_id'], int), "Offer Placement error - invalid offer ID in response"

            self.offer_id = response['offer_id']

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Offer Placement - step passed ----------------------------------\n")

    def test_offer_in_sql(self):
        try:

            time.sleep(4)
            offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
            logging.info(offer_sql)
            assert offer_sql['id'] == self.offer_id, "Offer Placement error - placed offer wasn't saved to DB"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Offer ID validation in SQL - step passed ------------------------------\n")

    @pytest.mark.parametrize('get_authorized_lenders', [[5]], indirect=True)
    def test_placing_first_bids(self, get_authorized_lenders):
        try:

            TestSqlWriterRecovery.lenders = get_authorized_lenders

            for i in range(0, 3):
                response = postman.gateway_requests.\
                    place_bid(TestSqlWriterRecovery.lenders[i].user_id, self.bid_interest_list[i],
                              self.offer_id, 0, TestSqlWriterRecovery.lenders[i].jwt_token)
                logging.info(response)

                assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
                assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
                assert isinstance(response['bid_id'], int),  "BID Placement error - invalid BID ID in response "

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Bid Placement - step passed ----------------------------------\n")

    def test_verify_no_match_yet(self):
        try:

            logging.info(f"Offer SQL : {reporter.get_offer_by_id(self.offer_id)}")

            offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
            logging.info(offer_sql)
            assert offer_sql['status'] == Offer.OfferStatuses.OPEN.value, "Offer was matched before 3 bids were placed"
            assert offer_sql['final_interest'] == '-1'

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- No Match On Third Bid verification - step passed ----------"
                     f"------------------------\n")

    def test_sql_writer_container_stopped(self):
        try:

            logging.info("Stopping SQL Writer Docker Container")
            TestSqlWriterRecovery.sql_writer_container = container_stop(DockerContainerNames.SQL_WRITER.value)

            # Verifying the container was stopped
            assert TestSqlWriterRecovery.sql_writer_container
            time.sleep(sql_writer_recovery_time)

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Stopping SQL Writer docker container - step passed ----------"
                     f"------------------------\n")

    def test_placing_final_bids(self):
        try:

            for i in range(3, 5):
                response = postman.gateway_requests. \
                    place_bid(TestSqlWriterRecovery.lenders[i].user_id, self.bid_interest_list[i],
                              self.offer_id, 0, TestSqlWriterRecovery.lenders[i].jwt_token)
                logging.info(response)

                # The bid that is expected to create a match with the offer
                if i == MATCH_EXPECTED:
                    TestSqlWriterRecovery.matching_bid_id = response['bid_id']

                assert 'bid_id' in response.keys(), "BID Placement error - no BID ID in response"
                assert 'Added new bid' in response['result'], "BID Placement error - no confirmation in response"
                assert isinstance(response['bid_id'], int), "BID Placement error - invalid BID ID in response "

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Final Bid Placement - step passed ----------------------------------\n")

    def test_sql_writer_container_started(self):
        try:

            logging.info("Starting SQL Writer Docker Container")
            assert container_start(TestSqlWriterRecovery.sql_writer_container)

            time.sleep(sql_writer_recovery_time)

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Starting SQL Writer docker container - step passed ----------"
                     f"------------------------\n")

    def test_updated_offer_after_match(self):
        try:

            time.sleep(5)
            offer_sql = reporter.get_offer_by_id(self.offer_id)[0]
            logging.info(offer_sql)

            assert offer_sql['status'] == Offer.OfferStatuses.MATCHED.value,\
                "Offer status in SQL wasn't updated after match"
            assert offer_sql['final_interest'] == str(test_bid_interest_4), \
                "Final interest in SQL wasn't updated after match"

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Verifying Offer Data Updated in SQL - step passed --------------"
                     f"--------------------\n")

    def test_match_data_verified(self):
        try:

            match_sql = reporter.get_match_by_offer_id(self.offer_id)[0]
            logging.info(match_sql)

            assert match_sql['bid_id'] == TestSqlWriterRecovery.matching_bid_id
            assert match_sql['bid_owner_id'] == TestSqlWriterRecovery.lenders[MATCH_EXPECTED].user_id
            assert match_sql['final_interest'] == str(test_bid_interest_4)

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Verifying Match Data in SQL - step passed --------------------"
                     f"--------------\n")

    def test_get_offers_by_status(self):
        try:

            response = postman.gateway_requests.get_offers_by_status(Offer.OfferStatuses.MATCHED.value)
            logging.info(response)

            assert isinstance(response, list), "Invalid data type in API response"
            assert len(response) > 0, "Placed offer wasn't returned in API response "
            assert isinstance(response[0], dict), "Invalid data type in API response"

            for offer in response:
                if offer['id'] == TestSqlWriterRecovery.offer_id:
                    assert offer['owner_id'] == TestSqlWriterRecovery.borrower.user_id
                    assert Decimal(offer['sum']) == Decimal(test_sum)
                    assert offer['duration'] == test_duration
                    assert offer['offered_interest'] == str(test_offer_interest_low)
                    assert offer['status'] == Offer.OfferStatuses.MATCHED.value

        except AssertionError as e:
            logging.warning(f"Test {test_file_name} - step failed: {e}")
            report_test_results.report_failure(test_id, test_file_name)
            raise e

        except Exception as e:
            logging.warning(f"Test {test_file_name} is broken: {e}")
            report_test_results.report_broken_test(test_id, test_file_name, e)
            raise e

        logging.info(f"----------------------- Get All MATCHED Offers  API method - data verified "
                     f"------------------------------\n")

        report_test_results.report_success(test_id, test_file_name)
