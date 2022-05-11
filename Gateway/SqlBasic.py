import logging
from sqlalchemy import exc, or_, and_
from sqlalchemy import create_engine


from sqlalchemy_utils import database_exists, create_database
from local_config import SqlConfig
import sqlalchemy as db
import sqlalchemy

from credittomodels import objects_mapped, utils
from sqlalchemy.orm import sessionmaker

from constants import USERS_TABLE_NAME, ROLES_TABLE_NAME, ACTIONS_TABLE_NAME, ACTIONS_BY_ROLES_TABLE_NAME


class SqlBasic(object):
    hst = SqlConfig.SQL_HOST.value
    usr = SqlConfig.SQL_USER.value
    pwd = SqlConfig.SQL_PASSWORD.value
    db_name = SqlConfig.DB_NAME.value
    test_users_file_path = SqlConfig.TEST_USERS_FILE_PATH.value
    cursor = None

    def __init__(self):
        self.cursor, self.engine = self.connect_me(self.hst, self.usr, self.pwd, self.db_name)

        # Initiating a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.create_validate_tables()

    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):
        """
        This method is used to establish a connection to MySQL DB.
        Credentials , host and DB name are taken from "config.ini" file.

        :param hst: host
        :param usr: user
        :param pwd: password
        :param db_name: DB name
        :return: SqlAlchemy connection (cursor)
        """

        try:

            url = f'mysql+pymysql://{usr}:{pwd}@{hst}:3306/{db_name}'

            # Create an engine object.
            engine = create_engine(url, echo=True, isolation_level="READ UNCOMMITTED")

            # Create database if it does not exist.
            if not database_exists(engine.url):
                create_database(engine.url)
                cursor = engine.connect()
                return cursor, engine
            else:
                # Connect the database if exists.
                cursor = engine.connect()
                return cursor, engine

        # Wrong Credentials error
        except sqlalchemy.exc.OperationalError as e:
            logging.critical("SQL DB -  Can't connect, verify credentials and host, verify the server is available")
            logging.critical(e)

        # General error
        except Exception as e:
            logging.critical("SQL DB - Failed to connect, reason is unclear")
            logging.critical(e)


    def create_validate_tables(self):
        """
        This method can be used to validate, that all needed table are exist.
        If they aren't the method will create them
        :param engine: Sql Alchemy engine
        """
        tables = self.engine.table_names()

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'offers' not in tables:
            logging.warning("Logs: 'offers' table is missing! Creating the 'offers' table")
            self.offers_table = objects_mapped.OfferMapped()
            objects_mapped.Base.metadata.create_all(self.engine)

        # Creating the 'bids' table if not exists - column for each "Bid" object property.
        if 'bids' not in tables:
            logging.warning("Logs: 'bids' table is missing! Creating the 'bids' table")
            self.bids_table = objects_mapped.BidMapped()
            objects_mapped.Base.metadata.create_all(self.engine)

        # Creating the 'offers' table if not exists - column for each "Match" object property.
        if 'matches' not in tables:
            logging.warning("Logs: 'matches' table is missing! Creating the 'matches' table")
            self.matches_table = objects_mapped.MatchesMapped()

        # Creating the 'local_config' table if not exists
        if 'local_config' not in tables:
            logging.warning("Logs: 'local_config' table is missing! Creating the 'local_config' table")
            self.local_config_table = objects_mapped.LocalConfigMapped()
            objects_mapped.Base.metadata.create_all(self.engine)

            # Inserting a record
            configuration = [objects_mapped.LocalConfigMapped(id=1, property="matching_logic",
                                               value=1, description="selected matching algorithm"),
                             objects_mapped.LocalConfigMapped(id=2, property="tail_digits",
                                               value=4, description="max tail digits allowed, rounding config")]

            self.session.add_all(configuration)
            self.session.commit()

        # Creating the 'users' table if it doesn't exist.
        if USERS_TABLE_NAME not in tables:
            logging.info(f"{USERS_TABLE_NAME} table is missing! Creating the {USERS_TABLE_NAME} table")
            objects_mapped.Base.metadata.create_all(self.engine)

            # Inserting the default test users

            self.session.add_all(self.get_test_users_from_file())
            self.session.commit()

        if ROLES_TABLE_NAME not in tables:
            logging.info(f"{ROLES_TABLE_NAME} table is missing! Creating the {ROLES_TABLE_NAME} table")

            default_roles = [objects_mapped.RolesMapped(role_id=1, role="Borrower"),
                             objects_mapped.RolesMapped(role_id=2, role="Lender"),
                             objects_mapped.RolesMapped(role_id=3, role="Admin")]

            self.session.add_all(default_roles)
            self.session.commit()

        if ACTIONS_TABLE_NAME not in tables:
            logging.info(f"{ACTIONS_TABLE_NAME} table is missing! Creating the {ACTIONS_TABLE_NAME} table")

            default_actions = [objects_mapped.ActionsMapped(action_id=1, action="place bid"),
                               objects_mapped.ActionsMapped(action_id=2, action="place offer"),
                               objects_mapped.ActionsMapped(action_id=3, action="cancel bid"),
                               objects_mapped.ActionsMapped(action_id=4, action="cancel offer"),
                               objects_mapped.ActionsMapped(action_id=5, action="view private bids"),
                               objects_mapped.ActionsMapped(action_id=6, action="view private offers"),
                               objects_mapped.ActionsMapped(action_id=7, action="view private matches")]

            self.session.add_all(default_actions)
            self.session.commit()

        if ACTIONS_BY_ROLES_TABLE_NAME not in tables:
            logging.info(
                f"{ACTIONS_BY_ROLES_TABLE_NAME} table is missing! Creating the {ACTIONS_BY_ROLES_TABLE_NAME} table")

            actions_mapping = [objects_mapped.ActionsToRolesMapped(role_id=1, allowed_actions_id='2 4 6 7'),
                               objects_mapped.ActionsToRolesMapped(role_id=2, allowed_actions_id='1 3 5 7'),
                               objects_mapped.ActionsToRolesMapped(role_id=3, allowed_actions_id='1 2 3 4 5 6 7')]

            self.session.add_all(actions_mapping)
            self.session.commit()

    def get_users(self)-> set:
        result = set()

        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_])
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()

        for row in fetched_data:
            result.add(row[1])

        return result

    def get_all_tokens(self)->set:
        result = set()

        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_])
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()

        for row in fetched_data:
            result.add(row[3])

        return result

    def get_token_creation_time(self, jwt):
        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_]).where(table_.columns.jwt_token == jwt)
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()
        if fetched_data:
            return fetched_data[0][5]

        return -1

    def save_jwt_key_time(self, username, encoded_jwt, key, token_creation_time):

        try:
            metadata = db.MetaData()
            table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

            query = db.update(table_).\
                values(jwt_token=encoded_jwt, key=key, token_creation_time=token_creation_time)\
                .where(table_.columns.username == username)

            self.cursor.execute(query)
            return True

        except Exception as e:
            logging.critical(f"Authorization: Failed to insert the JWT token to SQL DB: {e}")
            return False

    def terminate_token(self, token):
        try:
            metadata = db.MetaData()
            table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

            query = db.update(table_).\
                values(token_creation_time=0)\
                .where(table_.columns.jwt_token == token)

            self.cursor.execute(query)
            return {"Token Termination": "Confirmed"}

        except Exception as e:
            logging.critical(f"Authorization: Failed to insert the JWT token to SQL DB: {e}")
            return {"error": "Token Termination failed"}

    def get_password_by_username(self, username):
        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_]).where(table_.columns.username == username)
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()
        return fetched_data[0][2]

    def get_data_by_token(self, token):
        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_]).where(table_.columns.jwt_token == token)
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()

        return fetched_data[0][4], float(fetched_data[0][5])

    def get_allowed_actions_by_token(self, token):
        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_]).where(table_.columns.jwt_token == token)
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()

        role_id = int(fetched_data[0][6])

        table_ = db.Table(ACTIONS_BY_ROLES_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_]).where(table_.columns.role_id == role_id)
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()

        return [int(x) for x in fetched_data[0][1].split(" ")]

    def get_user_by_token(self, token):
        metadata = db.MetaData()
        table_ = db.Table(USERS_TABLE_NAME, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_]).where(table_.columns.jwt_token == token)
        ResultProxy = self.cursor.execute(query)
        fetched_data = ResultProxy.fetchall()

        return fetched_data[0]

    def get_columns(self, table):
        """
        Returns a list of column names
        @param table: existing table, str
        @return: list of str
        """
        try:
            metadata = db.MetaData()
            table_ = db.Table(table, metadata, autoload=True, autoload_with=self.engine)

            return table_.columns.keys()

        except Exception as e:
            logging.error(f" Failed to fetch column names of table {table} - {e}")
            return False

    def get_table_content(self, table):
        """
        Get table content from DB
        :param table: table name, String
        :return: tuple
        """

        metadata = db.MetaData()
        table_ = db.Table(table, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_])
        ResultProxy = self.cursor.execute(query)
        result = ResultProxy.fetchall()

        return result

    def get_offer_data_alchemy(self, offer_id: int):
        """
        This method can be used to extract data on a selected offer from SQL DB
        :param offer_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.id == offer_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "offers")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_offer_by_status_internal(self, offer_status: int):
        """
        Returns offer status from SQL DB by offer ID, internal usage only
        :param offer_status: int
        :return: tuple
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.status == offer_status)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_bids_by_offer_alchemy(self, offer_id: int):
        """
        Returns bids by offer ID - all bids are placed on given offer
        :param offer_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.target_offer_id == offer_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "bids")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get bids data from SQL - {e}")

    def get_bid_data_alchemy(self, bid_id: int):
        """
        Returns data on the selected bid
        :param bid_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.id == bid_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "bids")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get bids data from SQL - {e}")

    def get_offers_by_status_alchemy(self, status: int):
        """
         Fetches offers from SQL DB by provided status.
         Returns a list of dicts - each dict contains data on one offer.
         Returns an empty list if there are no offers in SQL DB with requested status.
         Special case: status '-1' is received - all offers are returned in that case.
        :param status: int
        :return: list of dicts
        """
        if status == -1:
            data = self.get_table_content("offers")
        else:
            data = self.get_offer_by_status_internal(status)

        return self.pack_to_dict(data, "offers")

    def get_bids_by_lender_alchemy(self, lender_id: int):
        """
        Returns all bids placed by the provided lender
        :param lender_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.owner_id == lender_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "bids")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get bids data from SQL - {e}")

    def get_offers_by_borrower_alchemy(self, borrower_id: int):
        """
        Returns all offers placed by the given borrower
        :param borrower_id:
        :return:
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.owner_id == borrower_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "offers")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_matches_by_owner_alchemy(self, owner_id: int):
        """
        Returns matches by owner ID - the owner can be lender OR borrower
        :param owner_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("matches", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(or_(table_.columns.offer_owner_id == owner_id, table_.columns.bid_owner_id == owner_id))
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "matches")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_relevant_offers(self):
        """
        Returns all offers in status OPEN and PARTIALLY_MATCHED from SQL DB
        :return: list of tuples
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(
                or_(table_.columns.status == 1, table_.columns.status == 3))
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_relevant_bids(self, target_offer_id):
        """
        Returns all bids in status OPEN placed on given offer
        :param target_offer_id: int
        :return: list of tuples
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(
                and_(table_.columns.status == 1, table_.columns.target_offer_id == target_offer_id))
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def fetch_config_from_db(self, config_param):
        """
        This method can be used to fetch local config params from SQL DB table 'local_config'
        :param config_param: requested config property, string
        :return: current config (value), string
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("local_config", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.property == config_param)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return int(self.pack_to_dict(result, "local_config")[0]['value'])

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_next_id(self, table_name):
        """
        This method can be used to get the next valid number that can be used as ID for new record in given table
        :param table_name: existing table, str
        :param cursor: sql cursor
        :return: int
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table(table_name, metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_])
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            result.sort(key=lambda x: x[0], reverse=True)

            return result[0][0] + 1

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_users_by_role(self, role_id: int):
        """
        Returns all users in given role
        :param role_id: int
        :return: list of tuples
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("users", metadata, autoload=True, autoload_with=self.engine)

            query = db.select([table_]).where(table_.columns.role_id == role_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def pack_to_dict(self, data, table):
        """
        This method can be used to extract data from SQL table and pack it to list of dicts
        @param query: query to execute
        @param table: SQL table
        @return: list of dicts
        """
        try:
            columns = self.get_columns(table)

            if data is None:
                logging.warning(f"Couldn't find the requested data by provided param")
                return []

            elif len(data) == 1:
                cnt = 0
                result = {}
                for column in columns:
                    result[column] = data[0][cnt]
                    cnt += 1
                return [result]

            result = []
            for contact in data:
                cnt = 0
                record = {}
                for column in columns:
                    record[column] = contact[cnt]
                    cnt += 1
                result.append(record)
            return result

        except Exception as e:
            logging.error(f"Failed to pack data from SQL, {e}")
            raise e

    def get_test_users_from_file(self):
        with open(self.test_users_file_path, 'r') as f:
            content = f.readlines()
            processed_content = [x.split(",") for x in content]
            users = []

            for item in processed_content:
                users.append(objects_mapped.UsersMapped(id=item[0],
                                                        username=item[1].strip(),
                                                        password=utils.Calculator.hash_string(item[2].strip()),
                                                        jwt_token="",
                                                        key="",
                                                        token_creation_time="",
                                                        role_id=int(item[3])))

        return users

# if __name__ == '__main__':
#     sq_mn = SqlBasic()
#     sq_mn.session.add_all(sq_mn.get_test_users_from_file())
#     sq_mn.session.commit()
