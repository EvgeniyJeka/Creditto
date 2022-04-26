import time

import logging
from credittomodels import statuses

from .SqlBasic import SqlBasic
from decimal import *

# Move to config or to global env. vars
fetch_from_sql_retries = 3
fetch_from_sql_delay = 5


class Reporter(SqlBasic):

    def __init__(self):
        super().__init__()

    # Remove unneeded legacy
    def get_offer_data(self, offer_id: int) -> dict:
        return self.get_offer_data_alchemy(offer_id)

    def get_offer_by_id(self, offer_id):
        return self.get_offer_data(offer_id)

    def get_match_by_offer_id(self, offer_id: int):
        return self.get_match_by_offer_id_alchemy(offer_id)


    def get_offers_by_status(self, status: int):
        """
         Fetches offers from SQL DB by provided status.
         Returns a list of dicts - each dict contains data on one offer.
         Returns an empty list if there are no offers in SQL DB with requested status.
         Special case: status '-1' is received - all offers are returned in that case.
        :param status: int
        :return: list of dicts
        """
        return self.get_offers_by_status_alchemy(status)

    def get_bids_by_lender(self, lender_id: int):
        return self.get_bids_by_lender_alchemy(lender_id)

    def get_offers_by_borrower(self, borrower_id: int):
        return self.get_offers_by_borrower_alchemy(borrower_id)

    def get_matches_by_owner(self, owner_id: int):
        return self.get_matches_by_owner_alchemy(owner_id)

    def validate_personal_data_request(self, request_data, verified_fields):
        try:
            if not isinstance(request_data, dict):
                return {"error": "Invalid object type for this API method"}

            # Rejecting invalid and malformed personal data requests
            if None in request_data.values():
                logging.warning(f"Gateway: Invalid personal data request received: {request_data}")
                return {"error": "Invalid object type for this API method"}

            # Rejecting invalid personal data requests with missing mandatory params
            for param in verified_fields:
                if param not in request_data.keys():
                    return {"error": "Required parameter is missing in provided personal data request"}

            return {"confirmed": "given personal data request can be placed"}

        except TypeError:
            return {"error": f"Personal data request is invalid, 'NULL' is detected in one of the key fields"}

    def validate_bid(self, bid: dict, verified_bid_params: list):
        """
        This method can be used to validate bid data.
        Bid can be placed only if it meets several criteria:
        a. Bid request is valid
        b. Target offer exist in DB
        c. Offer interest rate > Bid interest rate
        d. Offer status is OPEN
        e. Lender hasn't placed yet any bids on targeted offer
        :param verified_bid_params: list of str, params to verify
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

            offer_in_sql = self.get_offer_data_alchemy(bid['target_offer_id'])
            existing_bids_on_offer = self.get_bids_by_offer_alchemy(bid['target_offer_id'])

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

    def validate_offer(self, offer, verified_offer_params: list):
        """
        This method can be used to validate offer placement request.
        The value of 'type' field is expected to be 'offer'.
        The request body is expected to contain all mandatory params
        :param offer: offer placement request content
        :param verified_offer_params: list of str, mandatory params
        :return: JSON (confirmation message or an error message)
        """
        # Rejecting invalid and malformed offer placement requests
        if not isinstance(offer, dict) or 'type' not in offer.keys() or None in offer.values() \
                or offer['type'] != statuses.Types.OFFER.value:
            return {"error": "Invalid object type for this API method"}

        for param in verified_offer_params:
            if param not in offer.keys():
                return {"error": "Required parameter is missing in provided offer"}

        return {"confirmed": "given offer can be placed"}


# if __name__ == '__main__':
#     rep = Reporter()
#     a = rep.get_offer_data_alchemy(492829810550172999)
#     b = rep.get_matches_by_owner(1312)
#     print(a)



