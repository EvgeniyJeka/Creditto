from flask import Flask
from flask import request
import logging
from consumer_to_sql import ConsumerToSql

logging.basicConfig(level=logging.INFO)

# Initiating API Server
app = Flask(__name__)

# Initiating component responsible for saving data to SQL DB
sql_consumer = ConsumerToSql()
#
#
# Initiating producer
#producer = KafkaProducer()
#

@app.route("/place_offer", methods=['POST'])
def place_offer():
    """

    """

    offer = request.get_json()
    logging.info(f"Offer received: {offer}")

    # Validation

        # Once passed - create new Offer object and fill it with data received in the request
        # Use producer method to produce new kafka message - send Offer as JSON

    return {"error": ".."}
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
