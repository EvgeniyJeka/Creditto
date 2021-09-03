import requests
from base_config import BaseConfig
import json
import logging
from Requests.Body_Constructors.requests_constants import *


class GatewayRequestsBodies:

    @staticmethod
    def place_offer_request_body(owner_id, _sum, duration_months, offered_interest, allow_partial_fill):

        payload_composed = {
            TYPE: "offer",
            OWNER_ID: owner_id,
            SUM: _sum,
            DURATION: duration_months,
            OFFERED_INTEREST: offered_interest,
            ALLOW_PARTIAL_FILL: allow_partial_fill
        }

        return payload_composed

    @staticmethod
    def place_bid_request_body(owner_id, bid_interest, target_offer_id, partial_only):

        payload_composed = {
            TYPE: "bid",
            OWNER_ID: owner_id,
            BID_INTEREST: bid_interest,
            TARGET_OFFER_ID: target_offer_id,
            PARTIAL_ONLY: partial_only
        }

        return payload_composed

    @staticmethod
    def get_bids_by_owner(owner_id, token):
        payload_composed = {
            OWNER_ID: owner_id,
            TOKEN: token
        }

        return payload_composed
