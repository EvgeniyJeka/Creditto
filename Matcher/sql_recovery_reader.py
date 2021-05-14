from decimal import Decimal

from models.SqlBasic import SqlBasic
from models.Offer import Offer
from models.Bid import Bid
import logging


logging.basicConfig(level=logging.INFO)

class SqlRecoveryReader(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)


    def recover_offers_bids_sql(self):
        recovery_pool = {}

        # Getting all active offers from SQL DB
        query = "select * from offers where status in (1,3);"
        relevant_offers_db = self.run_sql_query(query)

        # Converting offer tuple extracted from SQL DB to Offer object
        for db_offer in relevant_offers_db:
            recovered_offer = Offer(db_offer[0], db_offer[1], db_offer[2], db_offer[3], Decimal(db_offer[4]),
                                    db_offer[5], db_offer[6], db_offer[7])

            logging.info(f"SqlRecoveryReader: Recovered offer from DB on system start: {recovered_offer}")

            # Adding the recovered Offer as a key to the recovery pool
            recovery_pool[recovered_offer] = []

        logging.info(f"SqlRecoveryReader: Recovery pool - all offers recovered: {recovery_pool}")

        for offer in recovery_pool.keys():
            query = f"select * from bids where status in (1) and target_offer_id = {offer.id};"
            recovered_bids_db = self.run_sql_query(query)

            if len(recovered_bids_db) > 0:
                for recovered_bid in recovered_bids_db:
                    print(recovered_bid)
                    bid = Bid(recovered_bid[0], recovered_bid[1], Decimal(recovered_bid[2]), recovered_bid[3],
                              recovered_bid[4], date_added=recovered_bid[5], status=recovered_bid[6])

                    recovery_pool[offer].append(bid)

        logging.info(f"SqlRecoveryReader: Recovery pool - all bids recovered: {recovery_pool}")

        return recovery_pool


if __name__ == '__main__':

    rreader = SqlRecoveryReader()
    rreader.recover_offers_bids_sql()