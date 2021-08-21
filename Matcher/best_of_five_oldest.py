from decimal import Decimal
from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from datetime import datetime

class BestOfFiveOldest:

    @staticmethod
    def find_best_bid(bids_for_offer, offer: Offer):
        print([x.bid_interest for x in bids_for_offer])

        bids_for_offer.sort(key=lambda x: Decimal(x.bid_interest))

        selected_bid = bids_for_offer[0]

        print(f"MATCHER: MATCHED BID {selected_bid.id} WITH OFFER {offer.id}")

        created_match = Match.Match(offer.id, selected_bid.id, offer.owner_id, selected_bid.owner_id,
                                    str(datetime.now()), offer.allow_partial_fill)

        return created_match