from decimal import Decimal


from credittomodels import Offer
from credittomodels import Bid
from SqlBasic import SqlBasic
import logging


logging.basicConfig(level=logging.INFO)


class SqlRecoveryReader(SqlBasic):

    def __init__(self):
        super().__init__()


    def recover_offers_bids_sql(self):
        """
         This method is used to fetch all offers and bids available for matching from MySQL.
         It is used in Matcher recovery flow (when the service starts).
         Returns a dict, where offer is a key and list of related bids is value.
         This dict becomes the Matcher's Pool
        :return: dict
        """
        recovery_pool = {}

        relevant_offers_db = self.get_relevant_offers()

        # Converting offer tuple extracted from SQL DB to Offer object
        for db_offer in relevant_offers_db:
            recovered_offer = Offer.Offer(db_offer[0], db_offer[1], db_offer[2], db_offer[3], Decimal(db_offer[4]),
                                    db_offer[6], db_offer[7], db_offer[8])

            logging.info(f"SqlRecoveryReader: Recovered offer from DB on system start: {recovered_offer}")

            # Adding the recovered Offer as a key to the recovery pool
            recovery_pool[recovered_offer] = []

        logging.info(f"SqlRecoveryReader: Recovery pool - all offers recovered: {recovery_pool}")

        for offer in recovery_pool.keys():
            recovered_bids_db = self.get_relevant_bids(offer.id)

            if len(recovered_bids_db) > 0:
                for recovered_bid in recovered_bids_db:
                    print(recovered_bid)
                    bid = Bid.Bid(recovered_bid[0], recovered_bid[1], Decimal(recovered_bid[2]), recovered_bid[3],
                              recovered_bid[4], date_added=recovered_bid[5], status=recovered_bid[6])

                    recovery_pool[offer].append(bid)

        logging.info(f"SqlRecoveryReader: Recovery pool - all bids recovered: {recovery_pool}")

        return recovery_pool


