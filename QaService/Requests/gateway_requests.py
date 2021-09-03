import requests
from base_config import BaseConfig
import json
import logging

base_url = BaseConfig.BASE_URL


class GatewayRequests(object):

    def place_offer(self, owner_id, sum, duration_months, offered_interest, allow_partial_fill) -> json:
        """
        Sends HTTP POST request to Gateway in order to place a new Offer
        :return: Response body as a json.
        """

        url = base_url + 'place_offer'

        payload_composed = {
            "type": "offer",
            "owner_id": owner_id,
            "sum": sum,
            "duration": duration_months,
            "offered_interest": offered_interest,
            "allow_partial_fill": allow_partial_fill
        }

        payload = json.dumps(payload_composed, default=lambda o: vars(o), sort_keys=True, indent=4)

        try:
            print(f"URL used: {url}")
            response = requests.post(url, json=payload_composed,  timeout=BaseConfig.WAIT_BEFORE_TIMEOUT)
            body = json.loads(response.text)
            logging.info("Service Response: {0}".format(body))
            return body

        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to convert the response to JSON, response: {response}, text: {response.text}")
            raise e

        except Exception as e:
            logging.error(F"{e.__class__.__name__} cancel_order failed with error: {e}")
            raise e


if __name__ == '__main__':
    gr = GatewayRequests()
    print(gr.place_offer("1021", 100000, 12, 0.08, 0 ))