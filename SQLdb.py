import sqlite3 as sql3
from sqlite3 import Error


class SQLite_C:

    conn = None

    # need to create a connection to the sql database
    def create_connection(self, db_file):
        try:
            self.conn = sql3.connect(db_file)
            print(sql3.version)
        except Error as e:
            print(e)

    # create a table with parameters
    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def finalize(self):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":

    file = "test.db"
    sql_table ='''CREATE TABLE EMPLOYEE(
                FIRST_NAME CHAR(20) NOT NULL,
                LAST_NAME CHAR(20),
                AGE INT,
                SEX CHAR(1),
                INCOME FLOAT
            )'''
    sql = SQLite_C()
    sql.create_connection(file)
    sql.create_table(sql_table)
    print("cleaning up")
    sql.finalize()
    print('finished with table')
