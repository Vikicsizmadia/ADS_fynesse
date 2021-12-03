# ADS_fynesse

This repo includes files and functions to do house price predictions by doing data analysis according to the Fynesse framework.

The Fynesse paradigm considers three aspects to data analysis, Access, Assess, Address.

## Access

Code that corresponds to the access part of the data analysis are in the .\fynesse\access.py file

I just collected the main sql queries I used for accessing the data, namely:

- Maing the connection to the MariaDB server
- Making the database
- Creating the pp_data table
- Populating the pp_data table with the downloaded dataframe
- Creating the postcode_data table
- Populating the postcode_data table with the downloaded dataframe

## Assess

Code that corresponds to the assess part of the data analysis are in the .\fynesse\assess.py file

This part contains functions that can be used for answering any types of questions and not specific to the price prediction question I addressed later.

- The ```create_connection``` function creates the connection to the database we created in the Access part.
- The ```plot_pois``` function plots points of interests provided in a list.
- The ```plot_houseprices_heatmap``` function plots a heatmap of the houseprices in the specified area, year and property type.
- The ```get_near_houses_avg_price``` function gets the average price of houses in the specified area, year and property type.
- The ```get_price``` function gets the price of a house with the provided postcode, year, propetry_type.
- The ```get_data``` function gets rows from the pp_data table where the postcode is equal to the provided postcode.
- The ```get_latitude_longitude``` function gets the corresponding latitude and longitude values of a postcode.
- The ```get_listOf_postcodes``` function gets the list of postcodes of houses where the year and property_type is provided.
- The ```get_list_of_postcodes_near_coordinates``` function similar as the above, but narrows down the postcodes to only those that are within a bounding box of the provided coordinates.
- The ```get_housedata_near_coordinates``` same function as above, but not only gives back a list of postcodes, but gives back the whole rows of pp_data, where the values match with the inputs.


## Address

Code that corresponds to the address part of the data analysis are in the .\fynesse\address.py file

This file contains functions of training a model and predicting house prices with that model.

The following 4 functions can be found in the file:

- The ```train_model``` function trains an OLS model on different number of points of interests and the average prices of the surrounding houses.
- The ```predict_price``` function uses the model trained by the ```train_model``` function, and predicts a price for a given latitude and longitude.
- The ```train2_model``` function trains an OLS model with the same features as the ```train_model```, but trains the model on a given list of postcodes of houses.
- The ```predict_prices``` function uses the model trained by the ```train2_model``` function, and predicts prices for a list of postcodes, and plots the predictions and the real prices for comparison.