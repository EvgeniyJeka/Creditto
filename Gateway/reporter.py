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

    def get_bids_by_offer(self, offer_id: int) -> list:
        query = f'select * from bids where target_offer_id = {offer_id};'
        return self.pack_to_dict(query, 'bids')

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


    def validate_bid(self, bid: dict, verified_bid_params: list):
        """
        This method can be used to validate bid data.
        Bid can be placed only if it meets several criteria:
        a. Bid request is valid
        b. Target offer exist in DB
        c. Offer interest rate > Bid interest rate
        d. Offer status is OPEN
        e. Lender hasn't placed yet any bids on targeted offer
        :param bid: dict
        :return: JSON
        """
        try:

            # Rejecting invalid and malformed bid placement requests
            if not isinstance(bid, dict) or 'type' not in bid.keys() or \
                    None in bid.values() or bid['type'] != statuses.Types.BID.value:
                logging.warning(f"Gateway: Invalid Bid request received: {bid}")
                return {"error": "Invalid object type for this API method"}

            # Rejecting invalid bid placement requests with missing mandatory params
            for param in verified_bid_params:
                if param not in bid.keys():
                    return {"error": "Required parameter is missing in provided bid"}

            offer_in_sql = self.get_offer_data(bid['target_offer_id'])
            existing_bids_on_offer = self.get_bids_by_offer(bid['target_offer_id'])

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

            # Returning error message if given lender has already placed a bid on the targeted offer
            if len(existing_bids_on_offer) > 0:
                for existing_bid in existing_bids_on_offer:
                    if existing_bid['owner_id'] == bid['owner_id']:
                        return {"error": f"Lender is allowed to place only one Bid on each Offer"}

            return {"confirmed": "given bid can be placed"}

        except TypeError:
            return {"error": f"Bid request is invalid, 'NULL' is detected in one of the key fields"}



if __name__ == '__main__':
    rp = Reporter()
    print(rp.get_offer_data(1))

