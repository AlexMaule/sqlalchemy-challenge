# Import Flask
from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# #---------------------------------------------------------------------------------

# # Find the most recent date in the data set.
# last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# # Starting from the most recent data point in the database. 

# # Calculate the date one year from the last date in data set.
# one_year_mark = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

# # Perform a query to retrieve the data and precipitation scores
# twelve_months_precp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_mark).order_by(Measurement.date).all()

# # Save the query results as a Pandas DataFrame and set the index to the date column
# precp_df = pd.DataFrame(twelve_months_precp)
# precp_df = precp_df.set_index('date')

# # Sort the dataframe by date
# sorted_precp_df = precp_df.sort_values('date')

# #---------------------------------------------------------------------------------

# # Design a query to calculate the total number stations in the dataset
# station_count = session.query(Station.name).count()

# # Design a query to find the most active stations (i.e. what stations have the most rows?)
# # List the stations and the counts in descending order.
# sel = [Measurement.station, Station.name, func.count(Measurement.station)]
# most_active_station = session.query(*sel).filter(Measurement.station == Station.station).\
#                         group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).limit(3)

# #---------------------------------------------------------------------------------


# # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
# most_active_id = most_active_station[0][0]
# num1 = session.query(Measurement.tobs).filter(Measurement.station == most_active_id).\
#         order_by(Measurement.tobs).first()
# lowest = num1[0]
# num2 = session.query(Measurement.tobs).filter(Measurement.station == most_active_id).\
#         order_by(Measurement.tobs.desc()).first()
# highest = num2[0]
# num3 = session.query(func.avg(Measurement.tobs)).filter(Measurement.station == most_active_id).first()
# average = num3[0]

# # Using the most active station id
# # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
# twelve_months_temp = session.query(Measurement.date,Measurement.tobs).\
#                     filter(Measurement.date >= one_year_mark).filter(Measurement.station == most_active_id).all()
# temp = []
# for item in twelve_months_temp:
#     temp.append(item[1])

# #---------------------------------------------------------------------------------

session.close()
# create an app, passing __name__
app = Flask(__name__)

measurements = pd.read_csv("Resources/hawaii_measurements.csv")
measurements["prcp"] = measurements["prcp"].fillna(0.00)

ordered_measure = measurements.sort_values('date')

stations_df = pd.read_csv("Resources/hawaii_stations.csv")

# index route
@app.route("/")
def home():
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    one_year_mark = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    # Perform a query to retrieve the data and precipitation scores
    twelve_months_precp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_mark).order_by(Measurement.date).all()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    precp_df = pd.DataFrame(twelve_months_precp)
    precp_df = precp_df.set_index('date')
    precip = precp_df.to_dict(orient = 'dict')

    # Close Session
    session.close()

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations_names = stations_df[["station","name"]]
    stations_names = stations_names.set_index("station")
    stat_name_dict = stations_names.to_dict(orient = 'dict')

    # Close Session
    session.close()

    return stat_name_dict

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    one_year_mark = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    sel = [Measurement.station, Station.name, func.count(Measurement.station)]
    most_active_station = session.query(*sel).filter(Measurement.station == Station.station).\
                            group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).limit(3)

    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active_id = most_active_station[0][0]
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    twelve_months_temp = session.query(Measurement.date,Measurement.tobs).\
                    filter(Measurement.date >= one_year_mark).filter(Measurement.station == most_active_id).all()
    temp_dict = dict(twelve_months_temp)

    # Close Session
    session.close()

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def starts(start):


    session = Session(engine)
    num1 = session.query(Measurement.tobs).\
        filter(Measurement.date >= start).\
        order_by(Measurement.tobs).first()
    tmin = num1[0] if num1 else None

    num2 = session.query(Measurement.tobs).\
        filter(Measurement.date >= start).\
        order_by(Measurement.tobs.desc()).first()
    tmax = num2[0] if num2 else None

    num3 = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).first()
    tavg = num3[0] if num3 else None

    # Close Session
    session.close()

    return (
        f"The Min, Max, and Avg temperature after {start} is:<br/>"
        f"Minimum: {tmin}<br/>"
        f"Maximum: {tmax}<br/>"
        f"Average: {round(tavg,2)}"
    )

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    session = Session(engine)
    num1 = session.query(Measurement.tobs).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        order_by(Measurement.tobs).first()
    tmin = num1[0] if num1 else None

    num2 = session.query(Measurement.tobs).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        order_by(Measurement.tobs.desc()).first()
    tmax = num2[0] if num2 else None

    num3 = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).first()
    tavg = num3[0] if num3 else None
    # Close Session
    session.close()

    return (
        f"The Min, Max, and Avg temperature between {start} and {end} is:<br/>"
        f"Minimum: {tmin}<br/>"
        f"Maximum: {tmax}<br/>"
        f"Average: {round(tavg,2)}"
    )


if __name__=="__main__":
    app.run(debug = True)

# Close Session
session.close()