
# Add monthly payment (self.monthly_payment) -  calculation should based on sum, duration (months) and interest
# MATCH object shall contain:
# Offer ID
# Bid ID
# Offer Owner ID
# Bid Owner ID
# Match exact time
from decimal import Decimal

from statuses import Types


class Match(object):

    def __init__(self, offer_id: int, bid_id: int, offer_owner_id: int,
                 bid_owner_id: int, match_time: str, partial: int, monthly_payment: Decimal = None):

        self.type = Types.MATCH.value

        self.offer_id = offer_id
        self.bid_id = bid_id
        self.offer_owner_id = offer_owner_id
        self.bid_owner_id = bid_owner_id
        self.match_time = match_time
        self.partial = partial
        self.monthly_payment = monthly_payment


    def __repr__(self):
        return f"Offer ID: {self.offer_id}, Bid ID: {self.bid_id}, " \
            f"Offer Owner ID: {self.offer_owner_id}, Bid Owner ID: {self.bid_owner_id}, " \
            f"Match Time: {self.match_time}, Partial: {self.patial}"