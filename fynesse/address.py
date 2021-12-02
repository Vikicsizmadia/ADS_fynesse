# This file contains code for suporting addressing questions in the data

from . import assess

"""# Here are some of the imports we might expect 
import sklearn.model_selection  as ms
import sklearn.linear_model as lm
import sklearn.svm as svm
import sklearn.naive_bayes as naive_bayes
import sklearn.tree as tree

import GPy
import torch
import tensorflow as tf

# Or if it's a statistical analysis
import scipy.stats"""

"""Address a particular question that arises from the data"""

import numpy as np
import statsmodels.api as sm
import osmnx as ox

#training the model for year & property_type
def train_model(conn, year, property_type, near_houses, bounding):

  #for all rows in pp_data which are in that year, with that property_type get:

  X_avgPrice_list = []
  X_numAmenities_list = []
  X_numShops_list = []
  X_numHealth_list = []
  X_numReligion_list = []
  X_numTransport_list = []
  Y_actualPrice_list = []

  for housedata in near_houses:

    # X:
    #avg_price of houses in the bounding box
    
    latitude = float(housedata[11]) #Decimal
    longitude = float(housedata[12])
    postcode = housedata[3]

    north = latitude + bounding/2
    south = latitude - bounding/2
    west = longitude - bounding/2
    east = longitude + bounding/2

    avg_price = assess.get_near_houses_avg_price(conn, north, south, west, east, property_type, year)

    X_avgPrice_list.append(float(avg_price[0][0]))

    tags = {"amenity": True,
        "religion": True, 
        "healthcare": True, 
        "shop": True, 
        "public_transport": True}

    #number of pois:
    pois = ox.geometries_from_bbox(north, south, east, west, tags)

    #number of amenities in bounding box
    num_amenities = 0
    if hasattr(pois, 'amenity'):
      amenities = pois[pois.amenity.notnull()]
      num_amenities = len(amenities)

    #number of shops in bounding box
    num_shops = 0
    if hasattr(pois, 'shop'):
      shops = pois[pois.shop.notnull()]
      num_shops = len(shops)

    #number of healthcare in bb
    num_healthcare = 0
    if hasattr(pois, 'healthcare'):
      healthcare_places = pois[pois.healthcare.notnull()]
      num_healthcare = len(healthcare_places)

    #number of religion in bb
    num_religion = 0
    if hasattr(pois, 'religion'):
      religion_places = pois[pois.religion.notnull()]
      num_religion = len(religion_places)

    #number of public transport in bb
    num_transport = 0
    if hasattr(pois, 'public_transport'):
      public_transport = pois[pois.public_transport.notnull()]
      num_transport = len(public_transport)

    X_numAmenities_list.append(num_amenities)
    X_numShops_list.append(num_shops)
    X_numHealth_list.append(num_healthcare)
    X_numReligion_list.append(num_religion)
    X_numTransport_list.append(num_transport)

    # Y:
    #actual price
    actual_price = assess.get_price(conn, postcode, year, property_type)
    Y_actualPrice_list.append(float(actual_price[0][0]))

  X_avgPrice = np.array(X_avgPrice_list)
  X_numAmenities = np.array(X_numAmenities_list)
  X_numShops = np.array(X_numShops_list)
  X_numHealth = np.array(X_numHealth_list)
  X_numReligion = np.array(X_numReligion_list)
  X_numTransport = np.array(X_numTransport_list)
  Y_actualPrice = np.array(Y_actualPrice_list)


  #make model
  design = np.concatenate((X_numAmenities.reshape(-1,1), X_avgPrice.reshape(-1,1), X_numShops.reshape(-1,1), X_numHealth.reshape(-1,1), X_numReligion.reshape(-1,1), X_numTransport.reshape(-1,1)),axis=1)
  m_linear_basis = sm.OLS(Y_actualPrice,design)
  results_basis = m_linear_basis.fit()

  return results_basis

