import requests
from base_config import BaseConfig
import json
import logging


class GatewayRequestsBodies:

    @staticmethod
    def place_offer_request_body(owner_id, sum, duration_months, offered_interest, allow_partial_fill):

        payload_composed = {
            "type": "offer",
            "owner_id": owner_id,
            "sum": sum,
            "duration": duration_months,
            "offered_interest": offered_interest,
            "allow_partial_fill": allow_partial_fill
        }

        return payload_composed