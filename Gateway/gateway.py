from flask import Flask
from flask import request
import logging
import json
from models.Offer import Offer
from Gateway.producer_from_api import ProducerFromApi

logging.basicConfig(level=logging.INFO)

# System start will be performed by Python script
# Start Kafka, Zoo Keeper, MySQL Server => will be performed by docker-compose (SQL will be added on later stages)
# Start all consumers: ConsumerToSql, ConsumerToMatcher = > Script (phase 4)
# Start Gateway => Script (phase 4)


# Add methods that can be used to check Offer and Bid statuses (Reporter addressed)
# Add methods that can be used to cancel Offer/Bid (message produced only after Offer/Bid status is verified in SQL DB,
# Reporter addressed)

# Initiating API Server
app = Flask(__name__)

# Initiating producer
producer = ProducerFromApi()




@app.route("/place_offer", methods=['POST'])
def place_offer():
    """

    """
    verified_offer_params = ['owner_id', 'sum', 'duration', 'offered_interest', 'allow_partiall_fill']

    offer = request.get_json()
    logging.info(f"Offer received: {offer}")

    # Validation

        # Once passed - create new Offer object and fill it with data received in the request
        # Use producer method to produce new kafka message - send Offer as JSON

    if offer['type'] != 'offer':
        return {"error": "Invalid object type for this API method"}

    for param in verified_offer_params:
        if param not in offer.keys():
            return {"error": "Required parameter is missing in provided offer"}

    # In future versions it is possible that the offer will be converted to Google Proto message
    placed_offer = Offer(offer['owner_id'], offer['sum'], offer['duration'], offer['offered_interest'],
                         offer['allow_partiall_fill'])

    offer_to_producer = json.dumps(placed_offer.__dict__)

    logging.info(offer_to_producer)
    logging.info("Using Producer instance to send the offer to Kafka topic 'offers' ")
    print(producer.produce_message(offer_to_producer, 'offers'))

    return {"result": ".."}
#
#
# @app.route('/add_json/<action_type>', methods=['POST'])
# def receive_json(action_type):
#     """
#     Receiving request that contains JSON. It's content is added to DB.
#     In this method  API request is processed, it's body is parsed and the content is passed to "add_json" method
#     of Core class. If there is a table which name is identical to received file name, table content is
#     appended to existing table. Otherwise a new table is created.
#     :return: JSON - confirmation on success, error message otherwise.
#     """
#     data = request.get_json()
#     result = core.add_json(data, action_type)
#
#     return result
#
#
#
# @app.route('/table_to_json/<table_name>', methods=['GET'])
# def table_to_json(table_name):
#     """
#     This method is used to get the content of SQL table as JSON.
#     :param table_name: String
#     :return: Table content as JSON
#     """
#     if table_name:
#         return core.table_as_json(table_name)
#
#     else:
#         return {"error": "Must enter valid table name."}


if __name__ == "__main__":

    app.run()




