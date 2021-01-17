from flask import Flask
from flask import request
import logging
import simplejson

from Gateway.reporter import Reporter
from models.Bid import Bid
from models.Offer import Offer
from Gateway.producer_from_api import ProducerFromApi
from statuses import Types

logging.basicConfig(level=logging.INFO)

# System start will be performed by Python script
# Start Kafka, Zoo Keeper, MySQL Server => will be performed by docker-compose (SQL will be added on later stages)
# Start all consumers: ConsumerToSql, ConsumerToMatcher = > Script (phase 4)
# Start Gateway => Script (phase 4)


# Add methods that can be used to check Offer and Bid statuses (Reporter addressed)
# Add methods that can be used to cancel Offer/Bid (message produced only after Offer/Bid status is verified in SQL DB,
# Reporter addressed)
# Add methods that can be used to check all available Offers/Bids
# Add methods that can be used to see all Bids for given Offer

# Offer/Bid ID assignation:
# Once new Offer is received, Gateway will call Reporter and check for last added Offer ID
# Received ID will be increased by 1, and the Offer will be sent to Kafka topic with the new ID
# Wait X sec
# Call Reporter and verify that Offer with the new ID was added to SQL DB
# Send response with the new ID ('Your Offer was successfully placed, ID: 1231')

# New Bids will be accepted only if bid_interest < offered_interest (validation will be added on Phase 3)

# Initiating API Server
app = Flask(__name__)

# Initiating producer
producer = ProducerFromApi()

# Initiating Reporter - needed for contact with SQL DB
reporter = Reporter()


@app.route("/place_offer", methods=['POST'])
def place_offer():
    """

    """
    verified_offer_params = ['owner_id', 'sum', 'duration', 'offered_interest', 'allow_partial_fill']

    offer = request.get_json()
    logging.info(f"Offer received: {offer}")

    # Validation

        # Once passed - create new Offer object and fill it with data received in the request
        # Use producer method to produce new kafka message - send Offer as JSON

    next_id = reporter.get_next_id('offers')

    if offer['type'] != Types.OFFER.value:
        return {"error": "Invalid object type for this API method"}

    for param in verified_offer_params:
        if param not in offer.keys():
            return {"error": "Required parameter is missing in provided offer"}

    # In future versions it is possible that the offer will be converted to Google Proto message
    placed_offer = Offer(next_id, offer['owner_id'], offer['sum'], offer['duration'], offer['offered_interest'],
                         offer['allow_partial_fill'])

    offer_to_producer = simplejson.dumps(placed_offer.__dict__, use_decimal=True)

    logging.info(offer_to_producer)
    logging.info("Using Producer instance to send the offer to Kafka topic 'offers' ")
    print(producer.produce_message(offer_to_producer, 'offers'))


    #T.B.D. Before responding with confirmation address reporter and verify offer was added to SQL DB
    return {"result": f"Added new offer, ID {next_id} assigned"}

@app.route("/place_bid", methods=['POST'])
def place_bid():
    """

    """
    verified_bid_params = ['owner_id', 'bid_interest', 'target_offer_id', 'partial_only']

    bid = request.get_json()
    logging.info(f"Bid received: {bid}")

    next_id = reporter.get_next_id('bids')

    if bid['type'] != Types.BID.value:
        return {"error": "Invalid object type for this API method"}

    for param in verified_bid_params:
        if param not in bid.keys():
            return {"error": "Required parameter is missing in provided bid"}

    # T.B.D : Before placing the bid, call Reporter and validate that the target offer exists
    logging.info("Validating target offer with provided ID exists")
    # T.B.D. : Before placing the bid, call Reporter and validate that bid interest
    # lower than the offered interest of target offer
    logging.info("Validating Bid interest against target offer")

    # In future versions it is possible that the bid will be converted to Google Proto message
    if bid['partial_only'] == 1:
        placed_bid = Bid(next_id, bid['owner_id'], bid['bid_interest'], bid['target_offer_id'], bid['partial_only'], bid['partial_sum'])

    else:
        placed_bid = Bid(next_id, bid['owner_id'], bid['bid_interest'], bid['target_offer_id'], bid['partial_only'])

    bid_to_producer = simplejson.dumps(placed_bid.__dict__, use_decimal=True)

    logging.info(bid_to_producer)
    logging.info("Using Producer instance to send the bid to Kafka topic 'bids' ")
    print(producer.produce_message(bid_to_producer, 'bids'))

    return {"result": f"Added new bid, ID {next_id} assigned"}





if __name__ == "__main__":

    app.run()




