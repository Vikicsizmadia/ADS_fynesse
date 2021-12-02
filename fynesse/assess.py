from .config import *

from . import access

"""These are the types of import we might expect in this file
import pandas
import bokeh
import matplotlib.pyplot as plt
import sklearn.decomposition as decomposition
import sklearn.feature_extraction"""
import pymysql
import matplotlib.pyplot as plt
import osmnx as ox
import mlai.plot as plot

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

def plot_pois(latitude, longitude, bounding, list_of_tags):
  north = latitude + bounding/2
  south = latitude - bounding/2
  west = longitude - bounding
  east = longitude + bounding

  # Retrieve POIs
  tags = {}
  for tag in list_of_tags:
    tags[tag] = True

  graph = ox.graph_from_bbox(north, south, east, west)
  pois = ox.geometries_from_bbox(north, south, east, west, tags)
  nodes, edges = ox.graph_to_gdfs(graph)

  fig, ax = plt.subplots(figsize=plot.big_figsize)

  # Plot street edges
  edges.plot(ax=ax, linewidth=1, edgecolor="dimgray")

  ax.set_xlim([west, east])
  ax.set_ylim([south, north])
  ax.set_xlabel("longitude")
  ax.set_ylabel("latitude")

  for tag in list_of_tags:
    pois[(getattr(pois, tag)).notnull()].plot(ax=ax, color="blue", alpha=1, markersize=50)

  plt.tight_layout()

def plot_houseprices_heatmap(conn, latitude, longitude, bounding, year, property_type):
    housedata = get_housedata_near_coordinates(conn, latitude, longitude, bounding, year, property_type)

    north = latitude + bounding/2
    south = latitude - bounding/2
    west = longitude - bounding
    east = longitude + bounding

    price_list = []
    latitude_list = []
    longitude_list = []
    for house in housedata:
        price_list.append(house[1])
        latitude_list.append(house[11])
        longitude_list.append(house[12])

    fig, ax = plt.subplots(figsize=plot.big_figsize)
    graph = ox.graph_from_bbox(north, south, east, west)
    nodes, edges = ox.graph_to_gdfs(graph)

    edges.plot(ax=ax, linewidth=1, edgecolor="dimgray")

    ax.set_xlim([west, east])
    ax.set_ylim([south, north])
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")

    plt.tricontourf(longitude_list, latitude_list, price_list)


def get_near_houses_avg_price(conn, north, south, west, east, property_type, year):
  with conn.cursor() as cur:
    cur.execute(f"SELECT AVG(pp.price) \
                  FROM (SELECT * FROM postcode_data WHERE postcode_data.lattitude < {north} AND postcode_data.lattitude > {south} \
                        AND postcode_data.longitude < {east} AND postcode_data.longitude > {west}) AS post \
                  INNER JOIN \
                        (SELECT * FROM pp_data WHERE (YEAR(pp_data.date_of_transfer) = {year}) AND (pp_data.property_type = '{property_type}')) AS pp \
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

def get_data(conn, postcode):
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

def get_housedata_near_coordinates(conn, latitude, longitude, bounding, year, property_type):
    north = latitude + bounding/2
    south = latitude - bounding/2
    west = longitude - bounding #need more longitude to match the latitude in kilometers
    east = longitude + bounding
    
    with conn.cursor() as cur:
        cur.execute(f"SELECT pp.transaction_unique_identifier, pp.price, pp.date_of_transfer, pp.postcode, pp.property_type, pp.new_build_flag, \
                          pp.locality, pp.town_city, pp.district, pp.county, post.country, post.lattitude, post.longitude, pp.db_id \
                    FROM (SELECT * FROM postcode_data WHERE postcode_data.lattitude < {north} AND postcode_data.lattitude > {south} \
                            AND postcode_data.longitude < {east} AND postcode_data.longitude > {west}) AS post \
                    INNER JOIN \
                            (SELECT * FROM pp_data WHERE (YEAR(pp_data.date_of_transfer) = {year}) AND (pp_data.property_type = '{property_type}') \
                            AND (pp_data.price IS NOT NULL)) AS pp \
                    ON post.postcode = pp.postcode")
    
    conn.commit()
    rows = cur.fetchall()
    return rows


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