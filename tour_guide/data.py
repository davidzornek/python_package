import os

import pymysql as sql
import pandas as pd
import psycopg2 as postgres
from dotenv import load_dotenv


def get_environmental_variables(variables):
    '''Acquires envirnomental variables from .env file.

    Variables must be stored in a .env file located in the
    current working directory. The .env should be gitignored.

    Keyword arguments:
    variables -- a list of strings designating the names of environmental
    variables to be imported.
    '''
    dotenv_path = os.path.join(os.getcwd(), '.env')

    load_dotenv(dotenv_path)

    output = {}
    for variable in variables:
        output[variable] = os.environ.get(variable)

    return output


def query_mls_manager(query, username, password, host='127.0.0.1', port=3307):
    '''Queries MLS manager, returning a pandas data frame.

    Will work for any query, passed as a string, but in the context of
    Concierge, it is used for retrieving public_remarks data from MLS
    listings. Default settings assume that MLS manager is accessible at
    127.0.0.1:3307 (note that this differs from the default port of 3306).

    Keyword arguments:
    query -- SQL query appropriate for MLS manager, passed as a string
    username -- MySQL username, as a string
    password -- MySQL password, as a string
    host -- IP address of MySQL, as a string
    port -- access port for MySQL, as an integer.
    '''
    connection = sql.connect(host=host,
                             port=port,
                             user=username,
                             password=password,
                             db='mls_manager',
                             charset='utf8',
                             cursorclass=sql.cursors.Cursor)

    return pd.read_sql(query, connection)


def query_area_manager(query, username, password, host='127.0.0.1', port=5432):
    '''Queries area manager, returning a pandas data frame.

    Will work for any query, passed as a string, but in the context of
    TourGuide, it is used for retrieving polygons. Default settings assume
    that area manager is accessible at 127.0.0.1:5432

    Keyword arguments:
    query -- SQL query appropriate for area manager, passed as a string
    username -- Postgres username, as a string
    password -- Postgres password, as a string
    host -- IP address of Postgres, as a string
    port -- access port for Postgres, as an integer.
    '''
    try:
        connection = postgres.connect(dbname='area_manager',
                                      user=username,
                                      host=host,
                                      password=password,
                                      port=5432)
    except ConnectionError:
        print("Cannot connect to database.")

    cursor = connection.cursor()
    cursor.execute(query)

    column_names = []
    summary = cursor.description
    for item in summary:
        column_names.append(item[0])

    data = cursor.fetchall()
    data = pd.DataFrame(data, columns=column_names)

    return data
