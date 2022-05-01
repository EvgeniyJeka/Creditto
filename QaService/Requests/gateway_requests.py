import requests
import json
import logging

try:
    from Requests.Body_Constructors.gateway_requests_bodies import GatewayRequestsBodies
    from Config.base_config import BaseConfig

except ModuleNotFoundError:
    from .Body_Constructors.gateway_requests_bodies import GatewayRequestsBodies
    from ..Config.base_config import BaseConfig


base_url = BaseConfig.BASE_URL


class GatewayRequests(object):

    def place_offer(self, owner_id, _sum, duration_months, offered_interest, allow_partial_fill) -> json:
        """
        Sends HTTP POST request to Gateway in order to place a new Offer
        :return: Response body as a json.
        """

        url = base_url + '/place_offer'

        payload = GatewayRequestsBodies.place_offer_request_body(owner_id, _sum, duration_months, offered_interest,
                                                                 allow_partial_fill)

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

        except Exception as e:
            logging.error(F"{e.__class__.__name__} place_offer failed with error: {e}")
            raise e

    def place_bid(self, owner_id, bid_interest, target_offer_id, partial_only) -> json:
        """
        Sends HTTP POST request to Gateway in order to place a new Bid
        :return: Response body as a json.
        """

        url = base_url + '/place_bid'

        payload = GatewayRequestsBodies.place_bid_request_body(owner_id, bid_interest, target_offer_id, partial_only)

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

        except Exception as e:
            logging.error(F"{e.__class__.__name__} place_offer failed with error: {e}")
            raise e
        
        
    def place_bid_custom_body(self, bid_body : json) -> json:
        """
        Sends HTTP POST request to Gateway in order to place a new Bid - receives Bid body as an arg
        :return: Response body as a json.
        """

        url = base_url + '/place_bid'

        payload = bid_body

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

        except Exception as e:
            logging.error(F"{e.__class__.__name__} place_offer failed with error: {e}")
            raise e

    def place_offer_custom_body(self, offer_body: json) -> json:
        """
        Sends HTTP POST request to Gateway in order to place a new Offer - receives Offer body as an arg
        :return: Response body as a json.
        """

        url = base_url + '/place_offer'

        payload = offer_body

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

        except Exception as e:
            logging.error(F"{e.__class__.__name__} place_offer failed with error: {e}")
            raise e

    def get_offers_by_status(self, requested_status) -> json:
        """
        Sends HTTP GET request to Gateway in order to receive all offers from DB in given status as JSON
        :return: Response body as a json.
        """

        url = base_url + f'/get_offers_by_status/{requested_status}'

        try:
            logging.info(url)
            response = requests.get(url, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

    def get_offers_by_owner(self, owner_id, token) -> json:
        """
        Sends HTTP POST request to Gateway in order to receive offers placed by given borrower as JSON
        :return: Response body as a json.
        """

        url = base_url + f'/get_all_my_offers'

        payload = GatewayRequestsBodies.get_offers_by_owner(owner_id, token)

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

    def get_all_offers(self) -> json:
        """
        Sends HTTP GET request to Gateway in order to receive all existing offers from DB
        :return: Response body as a json.
        """

        url = base_url + f'/get_all_offers'

        try:
            logging.info(url)
            response = requests.get(url, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

    def get_bids_by_owner(self, owner_id, token) -> json:
        """
        Sends HTTP POST request to Gateway in order to receive bids placed by given lender as JSON
        :return: Response body as a json.
        """

        url = base_url + f'/get_all_my_bids'

        payload = GatewayRequestsBodies.get_bids_by_owner(owner_id, token)

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

    def get_matches_by_owner(self, owner_id, token) -> json:
        """
        Sends HTTP POST request to Gateway in order to receive matches related to provided owner ID as JSON
        The method can be used both by Borrowers and Lenders - owner ID is used to filter the relevant matches
        :return: Response body as a json.
        """

        url = base_url + f'/get_all_my_matches'

        payload = GatewayRequestsBodies.get_matches_by_owner(owner_id, token)

        try:
            logging.info(url)
            response = requests.post(url, json=payload, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

    def sign_in_user(self, user_name, user_password) -> json:
        """
        Sends HTTP POST request to Gateway for sign in
        :return:  JWT token is expected
        """

        url = base_url + '/sign_in'
        headers = {'username': user_name, 'password': user_password}

        try:
            logging.info(url)
            response = requests.get(url, headers=headers, timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

        except Exception as e:
            logging.error(F"{e.__class__.__name__} place_offer failed with error: {e}")
            raise e


if __name__ == '__main__':
    gr = GatewayRequests()
    print(gr.sign_in_user('Joe Anderson', 'Truth'))

