from statuses import BidStatuses, Types


class Bid(object):
    id = 1
    owner_id = None
    bid_interest = None
    status = None
    target_offer = None
    sum = None
    partial_only = None
    partial_sum = 0

    def __init__(self, owner_id, bid_interest, target_offer_id, partial_only, partial_sum=None):
        self.id = Bid.id
        Bid.id += 1

        self.type = Types.BID.value

        self.owner_id = owner_id
        self.bid_interest = bid_interest
        self.target_offer_id = target_offer_id
        self.status = BidStatuses.PLACED.value

        if partial_only:
            self.partial_only = 1
            self.partial_sum = partial_sum

        else:
            self.partial_only = 0

    def __repr__(self):

        if self.partial_only and self.partial_sum:
            return f"Owner ID: {self.owner_id}, Bid Interest: {self.bid_interest}, Target Offer ID: {self.target_offer_id}, " \
                f"Bid Status: {self.status}, Partial Bid: {self.partial_only}, Sum suggested: {self.partial_sum}"
        else:
            return f"Owner ID: {self.owner_id}, Bid Interest: {self.bid_interest}, Target Offer ID: {self.target_offer_id}, " \
                f"Bid Status: {self.status}, Partial Bid: {self.partial_only}"
