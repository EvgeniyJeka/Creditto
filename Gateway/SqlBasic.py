import pymysql
import logging
from local_config import SqlConfig


class SqlBasic(object):
    hst = SqlConfig.SQL_HOST.value
    usr = SqlConfig.SQL_USER.value
    pwd = SqlConfig.SQL_PASSWORD.value
    db_name = SqlConfig.DB_NAME.value
    cursor = None

    def __init__(self):
        self.cursor = self.connect_me(self.hst, self.usr, self.pwd)
        self.create_validate_tables(self.cursor)

    # Connect to DB
    def connect_me(self, hst, usr, pwd):
        """
        This method can be used to connect  to MYSQL DB.
        :param hst: SQL Host
        :param usr: Username
        :param pwd: Password
        :param db_name: DB Name
        :return: SQL cursor
        """
        try:
            conn = pymysql.connect(host=hst, user=usr, password=pwd, autocommit='True')
            cursor = conn.cursor()

            cursor.execute('show databases')
            databases = [x[0] for x in cursor.fetchall()]

            if self.db_name in databases:
                query = f"USE {self.db_name}"
                logging.info(f"Executing query |{query}|")
                cursor.execute(query)

            else:
                query = f"CREATE DATABASE {self.db_name}"
                logging.info(f"Executing query | {query}|")
                cursor.execute(query)

            return cursor

        # Wrong Credentials error
        except pymysql.err.OperationalError as e:
            print(f"Wrong Credentials or Host: {e}")

        # Wrong DB name error
        except pymysql.err.InternalError:
            print("Unknown Database")

    def run_sql_query(self, query: str):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except pymysql.err.ProgrammingError as e:
            logging.error(f"Incorrect SQL syntax in query: {query} Error: {e}")
            raise e

        except Exception as e:
            logging.error(f"Failed to executed query: {query} Error: {e}")
            raise e

    # Validates that all the required tables exist, if they aren't - the method creates them.
    def create_validate_tables(self, cursor):
        """
        This method can be used to validate, that all needed table are exist.
        If they aren't the method will create them
        :param cursor: sql cursor
        """
        cursor.execute('show tables')
        tups = cursor.fetchall()

        tables = [tup[0] for tup in tups]

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'offers' not in tables:
            logging.warning("Logs: 'offers' table is missing! Creating the 'offers' table")
            query = "CREATE TABLE offers (id bigint, owner_id int, sum varchar(255), " \
                    "duration int, offered_interest varchar(255), final_interest varchar(255), allow_partial_fill int, date_added varchar(255), " \
                    "status int, PRIMARY KEY (ID));"

            cursor.execute(query)

        # Creating the 'bids' table if not exists - column for each "Bid" object property.
        if 'bids' not in tables:
            logging.warning("Logs: 'bids' table is missing! Creating the 'bids' table")
            query = "CREATE TABLE bids (id bigint, owner_id int, bid_interest varchar(255), target_offer_id bigint, " \
                    "partial_only int, date_added varchar(255), status int, PRIMARY KEY (ID));"

            cursor.execute(query)

        if 'matches' not in tables:
            logging.warning("Logs: 'matches' table is missing! Creating the 'bids' table")
            query = "CREATE TABLE matches (id bigint, offer_id bigint, bid_id bigint, offer_owner_id int, bid_owner_id int, " \
                    "match_time varchar(255), partial int, sum varchar(255), final_interest varchar(255), " \
                    "monthly_payment varchar(255)," \
                    " PRIMARY KEY (ID));"

            cursor.execute(query)

        if 'local_config' not in tables:
            logging.warning("Logs: 'local_config' table is missing! Creating the 'local_config' table")
            query = "CREATE TABLE local_config (id bigint, property varchar(255), " \
                    "value  varchar(255), description varchar(255), PRIMARY KEY (ID));"

            cursor.execute(query)
            logging.warning("Logs: ADDING THE DEFAULT CONFIG")

            query = f'insert into local_config values(1, "matching_logic", 1, "selected matching algorithm")'
            cursor.execute(query)
            query = f'insert into local_config values(2, "tail_digits", 4, "max tail digits allowed, rounding config")'
            cursor.execute(query)
            logging.warning("Logs: SETTING THE DEFAULT CONFIG")

    def get_columns(self, table):
        """
        Returns a list of column names
        @param table: existing table, str
        @return: list of str
        """
        query = 'show columns from ''%s'';' % table

        try:
            columns = self.run_sql_query(query)
            result = []

            for cl in columns:
                result.append(cl[0])

            return result

        except Exception as e:
            logging.error(f" Failed to fetch column names of table {table} - {e}")
            return False

    def pack_to_dict(self, query, table):
        """
        This method can be used to extract data from SQL table and pack it to list of dicts
        @param query: query to execute
        @param table: SQL table
        @return: list of dicts
        """
        try:
            columns = self.get_columns(table)
            data = self.run_sql_query(query)

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
            logging.error(f"Failed to get data from SQL, query: {query}, {e}")
            raise e

    def fetch_config_from_db(self, config_param):
        """
        This method can be used to fetch local config params from SQL DB table 'local_config'
        :param config_param: requested config property, string
        :return: current config (value), string
        """
        query = f"select value from local_config where property = '{config_param}';"
        result = self.run_sql_query(query)[0][0]
        return result


