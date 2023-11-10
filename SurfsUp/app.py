# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """ List all availabe api routes """
    return(
        f"<h1>Available Routes:</h1><br/>"
        f"<h3>Precipitation data of the last twelve months:</h3> /api/v1.0/precipitation<br/>"
        f"<h3>All the stations list:</h3> /api/v1.0/stations<br/>"
        f"<h3>Temperature data of the last twelve months:</h3> /api/v1.0/tobs<br/>"
        f"<h3>Search for summary of specified starting date (format year-month-day):</h3> /api/v1.0/<start><br/>"
        f"<h3>Search for summary of specified date range (format start-date/end-date):</h3> /api/v1.0/<start>/<end><br/>"
    )

 # Find the most recent date in the data set.
date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
recent_date = date[0]
recent_date_year = int(date[0][:4])
recent_date_month = int(date[0][5:7])
recent_date_day = int(date[0][8:10])
# Calculate the date one year from the last date in data set.
year_ago = dt.date(recent_date_year,recent_date_month,recent_date_day) - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query the last 12 months of precipitation data
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    last_year_precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date.between(year_ago,recent_date)).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitation = list(np.ravel(last_year_precipitation))

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Query all the stations from the dataset
    session = Session(engine)

    stations = session.query(Station.station).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    # Find the most active stations (i.e. which stations have the most rows?)
    session = Session(engine)
    active_stations = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    most_active_station_id = active_stations[0][0]
    temp_active_station = session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.station == most_active_station_id).\
    filter(Measurement.date.between(year_ago,recent_date)).all()

    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(temp_active_station))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def search_start_date(start):
    session = Session(engine)
    # For a specified start, calculate TMIN, TAVG, and TMAX 
    # for all the dates greater than or equal to the start date.
    start_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= str(start)).all()

    session.close()

    # Convert list of tuples into normal list
    all_start_temp = list(np.ravel(start_temp))

    return jsonify(all_start_temp)

@app.route("/api/v1.0/<start>/<end>")
def search_start_end_date(start, end):
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX 
    # for the dates from the start date to the end date, inclusive.
    session = Session(engine)
    start_end_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date.between(start,end)).all()

    session.close()

    # Convert list of tuples into normal list
    all_start_end_temp = list(np.ravel(start_end_temp))

    return jsonify(all_start_end_temp)

if __name__ == "__main__":
    app.run(debug=True)