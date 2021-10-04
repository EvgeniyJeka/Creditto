from flask import Flask
from flask import request
import logging
import simplejson

from reporter import Reporter
from credittomodels import Bid
from credittomodels import Offer
from producer_from_api import ProducerFromApi
from credittomodels import statuses
import uuid

from credittomodels import protobuf_handler

# 1. Add automated tests: match flow, API + SQL - D
# 2. Add validation on Offer/Bid placement - respond only after confirmation  - P.D.
# 3. Start writing read.me file (will be also considered as a spec) - D
# 4. Matching logic - move to separate files, update existing - D
# 5. Matching logic - move config to SQL (needed for tests) - D
# 6. Add Cancel Bid flow (?)
# 7. In SQL - make a list of authorized lenders and borrowers, verify each customer is limited to X offer/bids (?)
# 8. Kafka messages - PROTOBUF  - In Progress - D
# 9. Add API methods -  offers_by_status, get_my_bids (by CID) - D
# 10. Offer - add 'matching bid' to SQL, on match creation update offer status in SQL - D
# 11. Bid validation - add a new limitation: each lender can place only ONE bid on each offer.
# 12. Offer - add property 'final_interest', add in package and in DB as well - D
# 13. Consider adding Expirator/TimeManager service (?)
# 14. Test framework - request must be printed and/or logged - D
# 15. Add headers to Kafka records, message type should be in record header - D
# 16. Make tests to run in a separate container (e2e test)
# 17. Negative tests needed - invalid data type in requests (service must NOT crash)
# 18. Solve the 'duplicates' problem (bug)  UUID - D


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
# Send response with the new ID ('Your Offer was successfully placed, ID: 1231') - D

# New Bids will be accepted only if bid_interest < offered_interest (validation will be added on Phase 3) - D

# Initiating API Server
app = Flask(__name__)

# Initiating producer
producer = ProducerFromApi()

# Initiating Reporter - needed for contact with SQL DB
reporter = Reporter()

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler


@app.route("/place_offer", methods=['POST'])
def place_offer():
    """
    This API method can be used to place new offers.
    Offer is placed only if it passes validation.
    Expecting for a POST request with JSON body, example:
    {
    "type":"offer",
    "owner_id":1200,
    "sum":110000,
    "duration":12,
    "offered_interest":0.09,
    "allow_partial_fill":0
    }
    """
    verified_offer_params = ['owner_id', 'sum', 'duration', 'offered_interest', 'allow_partial_fill']

    offer = request.get_json()
    logging.info(f"Offer received: {offer}")

    # Validation

        # Once passed - create new Offer object and fill it with data received in the request
        # Use producer method to produce new kafka message - send Offer as JSON

    next_id = uuid.uuid4().int & (1<<60)-1

    if offer['type'] != statuses.Types.OFFER.value:
        return {"error": "Invalid object type for this API method"}

    for param in verified_offer_params:
        if param not in offer.keys():
            return {"error": "Required parameter is missing in provided offer"}

    # In future versions it is possible that the offer will be converted to Google Proto message
    placed_offer = Offer.Offer(next_id, offer['owner_id'], offer['sum'], offer['duration'], offer['offered_interest'],
                         offer['allow_partial_fill'])

    # Offer - serializing to proto
    offer_to_producer = proto_handler.serialize_offer_to_proto(placed_offer)

    # Handling invalid user input -  provided data can't be used to create a valid Bid and serialize it to proto
    if not offer_to_producer:
        return {"error": f"Failed to place a new offer, invalid data in request"}

    offer_record_headers = [("type", bytes('offer', encoding='utf8'))]

    logging.info(offer_to_producer)
    logging.info("Using Producer instance to send the offer to Kafka topic 'offers' ")
    print(producer.produce_message(offer_to_producer, 'offers', offer_record_headers))

    # Verifying placed offer was saved to 'offers' SQL table
    if not reporter.verify_offer_by_id(next_id):
        return {"error": f"Failed to place a new offer"}

    return {"result": f"Added new offer, ID {next_id} assigned", "offer_id": next_id}


@app.route("/place_bid", methods=['POST'])
def place_bid():
    """
    This API method can be used to place new bids on existing offer.
    Bid is placed only if it passes validation.
    Expecting for a POST request with JSON body, example:
    {
    "type":"bid",
    "owner_id":"2032",
    "bid_interest":0.061,
    "target_offer_id":2,
    "partial_only":0
    }
    """
    verified_bid_params = ['owner_id', 'bid_interest', 'target_offer_id', 'partial_only']

    bid = request.get_json()
    logging.info(f"Gateway: Bid received {bid}")

    next_id = uuid.uuid4().int & (1<<60)-1

    if bid['type'] != statuses.Types.BID.value:
        return {"error": "Invalid object type for this API method"}

    for param in verified_bid_params:
        if param not in bid.keys():
            return {"error": "Required parameter is missing in provided bid"}

    logging.info("Validating target offer with provided ID is OPEN, validating Bid interest against target offer")
    response = reporter.validate_bid(bid)
    if 'error' in response.keys():
        return response

    # In future versions it is possible that the bid will be converted to Google Proto message
    if bid['partial_only'] == 1:
        placed_bid = Bid.Bid(next_id, bid['owner_id'], bid['bid_interest'], bid['target_offer_id'], bid['partial_only'], bid['partial_sum'])

    else:
        placed_bid = Bid.Bid(next_id, bid['owner_id'], bid['bid_interest'], bid['target_offer_id'], bid['partial_only'])

    # Bid - serializing to proto
    bid_to_producer = proto_handler.serialize_bid_to_proto(placed_bid)

    # Handling invalid user input -  provided data can't be used to create a valid Bid and serialize it to proto
    if not bid_to_producer:
        return {"error": f"Failed to place a new offer, invalid data in request"}

    bid_record_headers = [("type", bytes('bid', encoding='utf8'))]

    logging.info(bid_to_producer)
    logging.info("Using Producer instance to send the bid to Kafka topic 'bids' ")
    print(producer.produce_message(bid_to_producer, 'bids', bid_record_headers))

    return {"result": f"Added new bid, ID {next_id} assigned", "bid_id": next_id}


@app.route("/get_offers_by_status/<status>", methods=['GET'])
def get_offers_by_status(status):
    return simplejson.dumps(reporter.get_offers_by_status(status))


@app.route("/get_all_offers", methods=['GET'])
def get_all_offers():
    return simplejson.dumps(reporter.get_offers_by_status(-1))


@app.route("/get_all_my_bids", methods=['POST'])
def get_my_bids():
    """
    This API method can be used to get all bids placed by customer with provided customer ID.
    :return: JSON
    Body sample:
    {
    "owner_id":"1032",
    "token": "a#rf$1vc"
    }
    """
    bids_request = request.get_json()

    lender_id = bids_request['owner_id']
    token = bids_request['token']

    logging.info(f"Gateway: get all my bids, lender token validated: {token}")
    return simplejson.dumps(reporter.get_bids_by_lender(lender_id))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')




