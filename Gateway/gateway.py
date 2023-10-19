from flask import Flask
from flask import request
import logging
import simplejson

from local_config import ConfigParams
from reporter import Reporter
from credittomodels import Bid
from credittomodels import Offer
from producer_from_api import ProducerFromApi
import uuid
from constants import *

from credittomodels import protobuf_handler

# 1. Add automated tests: match flow, API + SQL - D
# 2. Add validation on Offer/Bid placement - respond only after confirmation  - D
# 3. Start writing read.me file (will be also considered as a spec) - D
# 4. Matching logic - move to separate files, update existing - D
# 5. Matching logic - move config to SQL (needed for tests) - D
# 6. Add Cancel Bid flow (?)
# 7. In SQL - make a list of authorized lenders and borrowers, verify each customer is limited to X offer/bids (?)
# 8. Kafka messages - PROTOBUF  - D
# 9. Add API methods -  offers_by_status, get_my_bids (by CID) - D
# 10. Offer - add 'matching bid' to SQL, on match creation update offer status in SQL - D
# 11. Bid validation - add a new limitation: each lender can place only ONE bid on each offer - D
# 12. Offer - add property 'final_interest', add in package and in DB as well - D
# 13. Consider adding Expirator/TimeManager service (?)
# 14. Test framework - request must be printed and/or logged - D
# 15. Add headers to Kafka records, message type should be in record header - D
# 16. Make tests to run in a separate container - D
# 17. Negative tests needed - invalid data type in requests (service must NOT crash) - D
# 18. Solve the 'duplicates' problem (bug)  UUID - D
# 19. Offer/Bid validation in SQL - consider to change the logic, since customer is notified that 
# his bid/offer wasn't placed since it can't be found in SQL, but the message was produced by Gateway - D
# and consumed by the Matcher and it is in the pool and possibly can be matched - D
# Perhaps a confirmation should be sent after the message was successfully produced to Kafka.
# 20. Consider save logs to a file, file should be saved in container volumes
# 21. Monthly payment rounding im Matcher - move the tail digits to config in SQL - D
# 22. Add Gateway instance on port 80 (?)
# 23. Consider to add a new API method to Gateway - 'get_match_by_offer(offer_id)'
# 24. Test container - consider adding retries when SQL is unavailable (catch exception, retry x times before failing) - D
# 25. Authorization module - D

logging.basicConfig(level=logging.INFO)


# Initiating API Server
app = Flask(__name__)

# Initiating producer
producer = ProducerFromApi()

# Initiating Reporter - needed for contact with SQL DB
reporter = Reporter()

# Protobuf handler - used to serialize bids and offers to proto
proto_handler = protobuf_handler.ProtoHandler


@app.route('/sign_in', methods=['GET'])
def sign_in():
    try:
        # Headers parsing
        username = request.headers.get('username')
        password = request.headers.get('password')

        if not (username and password):
            logging.warning("Credentials missing in request headers")
            return {"Authorization": "Credentials missing in request headers"}

        logging.info(f"Authorization: Sign In request received, username {username} password {password}")

        produced_token = reporter.generate_token(username, password)

        if 'JWT' in produced_token.keys():
            return {"Token": produced_token['JWT']}

        elif 'error' in produced_token.keys():
            return {"Error": produced_token['error']}

    except (KeyError, TypeError) as e:
        logging.error(f"Sign In method called - credentials weren't provided: {e}")
        return {"Error": "Authorization: please provide valid credentials in request"}


@app.route('/sign_out', methods=['GET'])
def sign_out():
    try:
        # Headers parsing
        token = request.headers.get('jwt')

        if not token:
            logging.warning("Credentials missing in request headers")
            return {"Authorization": "Credentials missing in request headers"}

        logging.info(f"Authorization: Sign Out request received, JWT in request: {token}")

        sign_out_performed = reporter.sign_out(token)

        if 'error' not in sign_out_performed.keys():
            return {"Authorization": "Sign out confirmed", "Token": token}

        return sign_out_performed

    except (KeyError, TypeError) as e:
        logging.error(f"Sign Out method called - invalid request: {e}")
        return {"Error": "Authorization: please provide valid credentials in request"}


@app.route("/get_jwt_ttl/<jwt>", methods=['GET'])
def get_token_ttl(jwt):
    logging.info(f"Authorization: request for {jwt} token TTL received")

    token_ttl_checked = reporter.jwt_token_ttl_remains(jwt)

    if isinstance(token_ttl_checked, dict) and 'error' in token_ttl_checked.keys():
        return {"Error": token_ttl_checked['error']}

    return {f"JWT": f"{jwt}", "TTL": token_ttl_checked}


@app.route("/place_offer", methods=['POST'])
def place_offer():
    """
    This API method can be used to place new offers.
    Offer is placed only if it passes validation.
    Expecting for a POST request with JSON body, example:
    {
    "type":"offer",
    "sum":110000,
    "duration":12,
    "offered_interest":0.09,
    "allow_partial_fill":0
    }
    """
    offer = request.get_json()
    logging.info(f"Gateway: Offer received: {offer}")
    auth_token = request.headers.get('jwt')
    # Verifying the user is authorized to place an offer (JWT belongs toa  BORROWER, verifying user type)
    permissions_verification_result = reporter.verify_token(auth_token, PLACE_OFFER)

    if 'error' in permissions_verification_result.keys():
        return {"error": permissions_verification_result['error']}

    try:
        offer['owner_id'] = reporter.get_user_data_by_jwt(auth_token)[0]

    except TypeError as e:
        logging.error(f"Failed to get user by user ID - {e}")
        return {"error": "Invalid object type for this API method"}

    # Generating new offer ID
    next_id = uuid.uuid4().int & (1 << ConfigParams.generated_uuid_length.value)-1

    logging.info("Validating offer placement request")
    response = reporter.validate_offer(offer, ConfigParams.verified_offer_params.value)

    if 'error' in response.keys():
        logging.warning(f"Offer {next_id} has failed validation and was rejected")
        return response

    # Using the 'Offer' class from 'credittomodels' package - creating new Offer instance.
    placed_offer = Offer.Offer(next_id, offer['owner_id'], offer['sum'], offer['duration'], offer['offered_interest'],
                         offer['allow_partial_fill'])

    # Offer instance - serializing to proto
    offer_to_producer = proto_handler.serialize_offer_to_proto(placed_offer)

    # Handling invalid user input -  provided data can't be used to create a valid Bid and serialize it to proto
    if not offer_to_producer:
        return {"error": f"Failed to place a new offer, invalid data in request"}

    # Setting headers for Kafka message
    offer_record_headers = [("type", bytes('offer', encoding='utf8'))]

    # Producing the 'Offer' message to Kafka
    logging.info(f"Using Producer instance to send the offer to Kafka topic 'offers': {offer_to_producer} ")
    producer.produce_message(offer_to_producer, 'offers', offer_record_headers)

    return {"result": f"Added new offer, ID {next_id} assigned", "offer_id": next_id}


@app.route("/place_bid", methods=['POST'])
def place_bid():
    """
    This API method can be used to place new bids on existing offer.
    Bid is placed only if it passes validation.
    Expecting for a POST request with JSON body, example:
    {
    "type":"bid",
    "bid_interest":0.061,
    "target_offer_id":2,
    "partial_only":0
    }
    """
    bid = request.get_json()
    logging.info(f"Gateway: Bid received {bid}")
    auth_token = request.headers.get('jwt')

    permissions_verification_result = reporter.verify_token(auth_token, PLACE_BID)

    if 'error' in permissions_verification_result.keys():
        return {"error": permissions_verification_result['error']}

    try:
        bid['owner_id'] = reporter.get_user_data_by_jwt(auth_token)[0]

    except TypeError as e:
        logging.error(f"Failed to get user by user ID - {e}")
        return {"error": "Invalid object type for this API method"}

    next_id = uuid.uuid4().int & (1 << ConfigParams.generated_uuid_length.value)-1

    logging.info("Validating target offer with provided ID is OPEN, validating Bid interest against target offer")
    response = reporter.validate_bid(bid, ConfigParams.verified_bid_params.value)

    if 'error' in response.keys():
        logging.warning(f"Bid {next_id} has failed validation and was rejected")
        return response

    if bid['partial_only'] == 1:
        placed_bid = Bid.Bid(next_id, bid['owner_id'], bid['bid_interest'],
                             bid['target_offer_id'], bid['partial_only'], bid['partial_sum'])

    else:
        placed_bid = Bid.Bid(next_id, bid['owner_id'], bid['bid_interest'], bid['target_offer_id'], bid['partial_only'])

    # Bid - serializing to proto
    bid_to_producer = proto_handler.serialize_bid_to_proto(placed_bid)

    # Handling invalid user input -  provided data can't be used to create a valid Bid and serialize it to proto
    if not bid_to_producer:
        return {"error": f"Failed to place a new bid, invalid data in request"}

    bid_record_headers = [("type", bytes('bid', encoding='utf8'))]

    logging.info(f"Using Producer instance to send the bid to Kafka topic 'bids': {bid_to_producer} ")
    producer.produce_message(bid_to_producer, 'bids', bid_record_headers)

    return {"result": f"Added new bid, ID {next_id} assigned", "bid_id": next_id}


@app.route("/get_offers_by_status/<status>", methods=['GET'])
def get_offers_by_status(status):
    return simplejson.dumps(reporter.get_offers_by_status(status))


@app.route("/get_all_offers", methods=['GET'])
def get_all_offers():
    return simplejson.dumps(reporter.get_offers_by_status(-1))


@app.route("/get_all_my_bids", methods=['GET'])
def get_my_bids():
    """
    This API method can be used to get all bids placed by customer by JWT (expected in headers).
    :return: JSON

    """
    auth_token = request.headers.get('jwt')
    logging.info(f"Gateway: get all my bids, lender token validated: {auth_token}")

    permissions_verification_result = reporter.verify_token(auth_token, VIEW_PRIVATE_BIDS)

    if 'error' in permissions_verification_result.keys():
        return {"error": permissions_verification_result['error']}

    lender_id = reporter.get_user_data_by_jwt(auth_token)[0]
    return simplejson.dumps(reporter.get_bids_by_lender(lender_id))


@app.route("/get_all_my_offers", methods=['GET'])
def get_my_offers():
    """
    This API method can be used to get all offers placed by customer by JWT (expected in headers).
    :return: JSON
    """

    auth_token = request.headers.get('jwt')
    logging.info(f"Gateway: get all my offers, borrower token validated: {auth_token}")

    permissions_verification_result = reporter.verify_token(auth_token, VIEW_PRIVATE_OFFERS)

    if 'error' in permissions_verification_result.keys():
        return {"error": permissions_verification_result['error']}

    borrower_id = reporter.get_user_data_by_jwt(auth_token)[0]
    return simplejson.dumps(reporter.get_offers_by_borrower(borrower_id))


@app.route("/get_all_my_matches", methods=['GET'])
def get_my_matches():
    """
    This API method can be used to get all matches related to given customer by JWT (expected in headers).
    :return: JSON
    """
    auth_token = request.headers.get('jwt')
    logging.info(f"Gateway: get all my matches, customer's token validated: {auth_token}")

    permissions_verification_result = reporter.verify_token(auth_token, VIEW_PRIVATE_MATCHES)

    if 'error' in permissions_verification_result.keys():
        return {"error": permissions_verification_result['error']}

    owner_id = reporter.get_user_data_by_jwt(auth_token)[0]
    return simplejson.dumps(reporter.get_matches_by_owner(owner_id))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')




