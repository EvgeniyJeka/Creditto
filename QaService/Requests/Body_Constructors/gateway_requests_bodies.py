import requests
from base_config import BaseConfig
import json
import logging


class GatewayRequestsBodies:

    @staticmethod
    def place_offer_request_body(owner_id, _sum, duration_months, offered_interest, allow_partial_fill):

        payload_composed = {
            "type": "offer",
            "owner_id": owner_id,
            "sum": _sum,
            "duration": duration_months,
            "offered_interest": offered_interest,
            "allow_partial_fill": allow_partial_fill
        }

        return payload_composed

    @staticmethod
    def place_bid_request_body(owner_id, bid_interest, target_offer_id, partial_only):

        payload_composed = {
            "type": "bid",
            "owner_id": owner_id,
            "bid_interest": bid_interest,
            "target_offer_id": target_offer_id,
            "partial_only": partial_only
        }

        return payload_composed

    @staticmethod
    def get_bids_by_owner(owner_id, token):
        payload_composed = {
            "owner_id": owner_id,
            "token": token
        }

        return payload_composed
