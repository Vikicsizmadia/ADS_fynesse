from .config import *

from . import access

"""These are the types of import we might expect in this file
import pandas
import bokeh
import matplotlib.pyplot as plt
import sklearn.decomposition as decomposition
import sklearn.feature_extraction"""

def create_connection(user, password, host, database, port=3306):
    """ Create a database connection to the MariaDB database
        specified by the host url and database name.
    :param user: username
    :param password: password
    :param host: host url
    :param database: database
    :param port: port number
    :return: Connection object or None
    """
    conn = None
    try:
        conn = pymysql.connect(user=user,
                               passwd=password,
                               host=host,
                               port=port,
                               local_infile=1,
                               db=database
                               )
    except Exception as e:
        print(f"Error connecting to the MariaDB Server: {e}")
    return conn

def get_near_houses_avg_price(conn, north, south, west, east, property_type, date):
  with conn.cursor() as cur:
    cur.execute(f"SELECT AVG(pp.price) \
                  FROM (SELECT * FROM postcode_data WHERE postcode_data.lattitude < {north} AND postcode_data.lattitude > {south} \
                        AND postcode_data.longitude < {east} AND postcode_data.longitude > {west}) AS post \
                  INNER JOIN \
                        (SELECT * FROM pp_data WHERE (YEAR(pp_data.date_of_transfer) = {date}) AND (pp_data.property_type = '{property_type}')) AS pp \
                  ON post.postcode = pp.postcode")

    conn.commit()
    rows = cur.fetchall()
    return rows

def get_price(conn, postcode, year, property_type):
  #possible that these data describe more than 1 row in the database, so we take the average
  with conn.cursor() as cur:
    cur.execute(f"SELECT AVG(price) \
                  FROM pp_data \
                  WHERE (YEAR(pp_data.date_of_transfer) = {year}) AND (pp_data.property_type = '{property_type}') \
                  AND (pp_data.postcode = '{postcode}')")

    conn.commit()
    rows = cur.fetchall()
    return rows

def get_data(conn, postcode, year, property_type):
  with conn.cursor() as cur:
    cur.execute(f"SELECT * \
                  FROM pp_data \
                  WHERE pp_data.postcode = '{postcode}' ")

    conn.commit()
    rows = cur.fetchall()
    return rows

def get_latitude_longitude(conn, postcode):
  with conn.cursor() as cur:
    cur.execute(f"SELECT lattitude, longitude \
                  FROM postcode_data \
                  WHERE postcode = '{postcode}'")
    conn.commit()
    rows = cur.fetchall()
    return rows

def get_listOf_postcodes(conn, year, property_type):
  with conn.cursor() as cur:
    cur.execute(f"SELECT postcode \
                  FROM pp_data \
                  WHERE (YEAR(date_of_transfer) = {year}) AND (property_type = '{property_type}')")
    conn.commit()
    rows = cur.fetchall()
    postcode_list = []
    for postcode in rows:
      if(postcode[0] != ''):
        postcode_list.append(postcode[0])
    return postcode_list

def get_list_of_postcodes_near_coordinates(conn, latitude, longitude, year, property_type):
  bounding = 0.02
  north = latitude + bounding/2
  south = latitude - bounding/2
  west = longitude - bounding/2
  east = longitude + bounding/2
  
  with conn.cursor() as cur:
    cur.execute(f"SELECT pp.postcode \
                  FROM (SELECT * FROM postcode_data WHERE postcode_data.lattitude < {north} AND postcode_data.lattitude > {south} \
                        AND postcode_data.longitude < {east} AND postcode_data.longitude > {west}) AS post \
                  INNER JOIN \
                        (SELECT * FROM pp_data WHERE (YEAR(pp_data.date_of_transfer) = {year}) AND (pp_data.property_type = '{property_type}') \
                         AND (pp_data.price IS NOT NULL)) AS pp \
                  ON post.postcode = pp.postcode")
    
    conn.commit()
    rows = cur.fetchall()
    postcode_list = []
    for postcode in rows:
      if(postcode[0] != ''):
        postcode_list.append(postcode[0])
    return postcode_list


"""
def data():
    #Load the data from access and ensure missing values are correctly encoded as well as indices correct, column names informative, date and times correctly formatted. Return a structured data structure such as a data frame.
    df = access.data()
    raise NotImplementedError

def query(data):
    #Request user input for some aspect of the data.
    raise NotImplementedError

def view(data):
    #Provide a view of the data that allows the user to verify some aspect of its quality.
    raise NotImplementedError

def labelled(data):
    #Provide a labelled set of data ready for supervised learning.
    raise NotImplementedError
"""