import time

import pymysql
from datetime import datetime
import logging
from credittomodels import statuses

from credittomodels import Offer
from SqlBasic import SqlBasic
from decimal import *

# Move to config or to global env. vars
fetch_from_sql_retries = 3
fetch_from_sql_delay = 5

class Reporter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)

    def get_offer_data(self, offer_id: int) -> dict:
        query = f'select * from offers where id = {offer_id}'
        return self.pack_to_dict(query, "offers")

    def verify_offer_by_id(self, offer_id):
        """
        Verifying offer with given ID was saved to SQL DB
        :param offer_id: int
        :return: bool
        """
        offer_data = self.get_offer_data(offer_id)
        if offer_data == []:
            for i in range(0, fetch_from_sql_retries):
                time.sleep(fetch_from_sql_delay)
                offer_data = self.get_offer_data(offer_id)

        return len(offer_data) > 0

    def get_bid_data(self, bid_id: int) -> dict:
        query = f'select * from bids where id = {bid_id}'
        return self.pack_to_dict(query, "bids")


    def get_offers_by_status(self, status: int):
        """
         Fetches offers from SQL DB by provided status.
         Returns a list of dicts - each dict contains data on one offer.
         Returns an empty list if there are no offers in SQL DB with requested status.
         Special case: status '-1' is received - all offers are returned in that case.
        :param status: int
        :return: list of dicts
        """
        if status == -1:
            query = 'select * from offers'
        else:
            query = f'select * from offers where status = {status}'
        return self.pack_to_dict(query, "offers")

    def get_bids_by_lender(self, lender_id: int):
        query = f'select * from bids where owner_id = {lender_id}'
        return self.pack_to_dict(query, "bids")


    def validate_bid(self, bid: dict):
        """
        This method can be used to validate bid data.
        Bid can be placed only if it meets several criteria:
        a. Target offer exist in DB
        b. Offer interest rate > Bid interest rate
        c. Offer status is OPEN
        :param bid: dict
        :return: JSON
        """
        offer_in_sql = self.get_offer_data(bid['target_offer_id'])

        # Returning error message if bid is placed on non-existing offer
        if offer_in_sql == []:
            logging.warning(f"Reporter: detected an attempt to place a bid on non-existing offer: {bid['target_offer_id']}")
            return {"error": f"Offer {bid['target_offer_id']} does not exist"}

        offer_in_sql = offer_in_sql[0]

        # Returning error message if bid interest rate is above offer interest rate
        if Decimal(bid['bid_interest']) > Decimal(offer_in_sql['offered_interest']):
            logging.warning(f"Reporter: detected an attempt to place a bid with interest rate {bid['bid_interest']}, "
                            f"while offer interest rate is {offer_in_sql['offered_interest']}")
            return {"error": f"Interest rate above offer interest rate {offer_in_sql['offered_interest']}"}

        # Returning error message if target offer status isn't OPEN
        if offer_in_sql['status'] != statuses.OfferStatuses.OPEN.value:
            logging.warning(
                f"Reporter: detected an attempt to place a bid on an offer in status: {offer_in_sql['status']}")
            return {"error": f"Bids can't be placed on offers in status {offer_in_sql['status']}"}

        return {"confirmed": "given bid can be placed"}



if __name__ == '__main__':
    rp = Reporter()
    print(rp.get_offer_data(1))

