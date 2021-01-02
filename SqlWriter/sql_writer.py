import pymysql
from datetime import datetime

class SqlWriter(object):

    hst = '127.0.0.1'
    usr = 'root'
    pwd = '123456'
    db_name = 'creditto'
    cursor = None

    def __init__(self):
        SqlWriter.cursor = self.connect_me(self.hst, self.usr, self.pwd, self.db_name)
        self.create_validate_tables(SqlWriter.cursor)



    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):
        try:
            conn = pymysql.connect(host=hst, user=usr, password=pwd, db=db_name, autocommit='True')
            cursor = conn.cursor()
            return cursor

        # Wrong Credentials error
        except pymysql.err.OperationalError:
            print("Wrong Credentials or Host")

        # Wrong DB name error
        except pymysql.err.InternalError:
            print("Unknown Database")

    # Validates that all the required tables exist, if they arent - the method creates them.
    def create_validate_tables(self, cursor):

        cursor.execute('show tables')
        tups = cursor.fetchall()

        tables = [tup[0] for tup in tups]

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'offers' not in tables:
            print("Logs: 'offers' table is missing! Creating the 'offers' table")
            query = "CREATE TABLE offers (id int, owner_id int, sum varchar(255), " \
                    "duration int, offered_interest varchar(255), allow_partial_fill int, date_added varchar(255), " \
                    "status int);"

            cursor.execute(query)


if __name__=='__main__':
    swriter = SqlWriter()

    query = f"insert into offers values (2, 22, 100.0, 13, 0.05, 0, '{datetime.now()}', 1);"
    swriter.cursor.execute(query)
