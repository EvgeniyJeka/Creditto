
# Add monthly payment (self.monthly_payment) -  calculation should based on sum, duration (months) and interest
# MATCH object shall contain:
# Offer ID
# Bid ID
# Offer Owner ID
# Bid Owner ID
# Match exact time

class Match(object):

    def __init__(self, offer_id: int, bid_id: int, offer_owner_id: int,
                 bid_owner_id: int, match_time: str, partial: int):
        self.offer_id = offer_id
        self.bid_id = bid_id
        self.offer_owner_id = offer_owner_id
        self.bid_owner_id = bid_owner_id
        self.match_time = match_time
        self.patial = partial