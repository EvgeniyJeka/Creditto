import time

import logging
from credittomodels import statuses

import jwt
import time
import logging
from decimal import Decimal
from local_config import ConfigParams

logging.basicConfig(level=logging.INFO)

from constants import *
import hashlib
import random

from SqlBasic import SqlBasic

# Move to config or to global env. vars
fetch_from_sql_retries = 3
fetch_from_sql_delay = 5


class Reporter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.token_ttl = ConfigParams.jwt_time_to_live.value

    def verify_offer_by_id(self, offer_id):
        """
        Verifying offer with given ID was saved to SQL DB
        :param offer_id: int
        :return: bool
        """
        offer_data = self.get_offer_data_alchemy(offer_id)
        if offer_data == []:
            for i in range(0, fetch_from_sql_retries):
                time.sleep(fetch_from_sql_delay)
                offer_data = self.get_offer_data_alchemy(offer_id)

        return len(offer_data) > 0

    def get_bid_data(self, bid_id: int) -> dict:
        return self.get_bid_data_alchemy(bid_id)

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

    def hash_string(self, input_: str):
        """
        Hashing method
        :param input_: str
        :return: str
        """
        plaintext = input_.encode()

        # call the sha256(...) function returns a hash object
        hash_object = hashlib.sha256(plaintext)
        hash = hash_object.hexdigest()
        return hash

    def sign_out(self, token):
        """
        Sign out flow - verifying the provided JWT.
        If it is valid - the JWT is deleted, otherwise an error message is returned.
        :param token: JWT token
        :return:
        """
        # Check for provided token in SQL DB
        all_tokens = self.get_all_tokens()
        if token not in all_tokens:
            return {"error": f"Invalid JWT provided"}

        return self.terminate_token(token)

    def key_gen(self):
        return "key" + str(random.randint(1000, 10000))

    def generate_token(self, username: str, password: str):
        """
        This method is used to generate a JWT basing on provided credentials. JWT is generated after creds are verified
        :param username: str
        :param password: str
        :return: JWT on success
        """

        key = self.key_gen()  # The key will be generated on random basis and saved to DB

        # Check if given username exists in SQL DB, if it doesn't - return an error
        user_names_set = self.get_users()
        if username not in user_names_set:
            return {"error": f"Wrong credentials"}

        password_hash = self.get_password_by_username(username)

        # Verifying password against hashed password in SQL DB
        if self.hash_string(password) == password_hash:
            encoded_jwt = jwt.encode({"user": username, "password": password}, key, algorithm="HS256")
            token_creation_time = time.time()

            # Save the created JWT, KEY and token creation time to SQL
            if not self.save_jwt_key_time(username, encoded_jwt, key, token_creation_time):
                return {"error": "Token creation failed due to system issues"}

            return {"JWT": encoded_jwt}

        else:
            return {"error": "Wrong credentials"}

    def verify_token(self, token: str, action_id: int):
        """
        This method is used to verify JWT (without decoding it). Also verifies that given user has permissions
        required to perform the requested action
        :param token: str
        :param action_id: int
        :return: dict (confirmation on success)
        """

        logging.info(f"Authorization: User {token} tries to perform action {action_id}, "
                     f"addressing the Authorization module")

        if not token:
            logging.warning("JWT is missing in request headers")
            return {"error": "JWT is missing in request headers"}

        if token == "":
            return {"error": f"Wrong credentials"}

        # Check for provided token in SQL DB
        if not self.get_all_tokens().__contains__(token):
            return {"error": f"Wrong credentials"}

        _, token_creation_time = self.get_data_by_token(token)

        # Verify against SQL if the token is valid (not expired)
        #                                   - fetch the creation time and subtract it from the current time
        if not time.time() - token_creation_time < self.token_ttl:
            logging.error(f"Token TTL: {self.token_ttl}, current age: {time.time() - token_creation_time}")
            return {"error": "Token has expired"}

        # Bring the action types of all actions that current user is allowed to perform from SQL.
        # If the action types list contains the provided action type - return a confirmation.
        # Otherwise - return an error message.
        if int(action_id) not in self.get_allowed_actions_by_token(token):
            return {"error": "Forbidden action"}

        return {"Confirmed": "Permissions verified"}

    def decode_token(self, token):
        """
        This method can be used to decode a JWT if the former is saved in SQL DB
        :param token: valid JWT
        :return: dict, decoded JWT
        """
        # Check for provided token in SQL DB
        if not self.get_all_tokens().__contains__(token):
            return {"error": f"Unlisted token"}

        secret_key, _ = self.get_data_by_token(token)

        try:
            return jwt.decode(token, secret_key, algorithms="HS256")

        except jwt.exceptions.InvalidSignatureError:
            logging.error(f"Authorization: Invalid JWT received {token}")
            return {"error": "Invalid token provided"}

    def jwt_token_ttl_remains(self, token):
        creation_time = self.get_token_creation_time(token)

        if float(creation_time) > 0:
            logging.info(f"Authorization: token {token} creation time: {creation_time}")
            ttl = self.token_ttl - (time.time() - float(creation_time))
            if ttl > 0:
                return ttl
            return 0
        return {"error": "Non existing JWT"}

    def get_user_data_by_jwt(self, jwt):
        """
        Prompting SQL DB for user name
        :param jwt: str
        :return: str on success
        """

        result = self.get_user_by_token(jwt)
        if not result:
            return False

        return result


# if __name__ == '__main__':
#     rep = Reporter()
#     a = rep.get_offer_data_alchemy(492829810550172999)
#     b = rep.get_matches_by_owner(1312)
#     print(a)
#


