from decimal import Decimal
from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from datetime import datetime
import logging


class BestOfTenNewest:

    @staticmethod
    def find_best_bid(bids_for_offer, offer: Offer):

        if len(bids_for_offer) < 10:
            logging.info(f"MATCHER: Not enough bids for offer {offer.id}, expecting for at least 10, no match")
            return False

        logging.info("Matcher: Selected matching logic - match the offer with the best bid when the 5th bid is received,"
                     "best has the lowest interest rate, "
                     "the oldest bit is selected if there are 2 or more bids with the same rate")

        print([x.bid_interest for x in bids_for_offer])

        # Sorting bids by interest rate
        bids_for_offer.sort(key=lambda x: Decimal(x.bid_interest))

        best_interest_bid = bids_for_offer[0]
        best_interest_rate = best_interest_bid.bid_interest

        # Filtering bids by interest rate - the list below contains the bids with the lowest rate found
        list_bids_best_interest = [x for x in bids_for_offer if x.bid_interest == best_interest_rate]

        # Sorting the bids by date in ascending order, selecting the oldest bid
        list_bids_best_interest.sort(key=lambda x: x.date_added, reverse=True)
        selected_bid = list_bids_best_interest[0]

        logging.info(f"MATCHER: MATCHED BID {selected_bid.id} WITH OFFER {offer.id}")
        created_match = Match.Match(offer.id, selected_bid.id, offer.owner_id, selected_bid.owner_id,
                                    str(datetime.now()), offer.allow_partial_fill, best_interest_rate)

        return created_match

