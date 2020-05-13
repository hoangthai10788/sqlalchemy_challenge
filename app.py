import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import os

# Database Setup and create an engine
engine = create_engine(f"sqlite:///hawaii.sqlite")

# Reflect an existing database into a model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect = True)

# Save references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)


# Flask routes

@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session from Python to the DB

    session = Session(bind = engine)

    # Query the results with date and precipitation

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert the results to a dictionary using date as the key and prcp as the value

    results_dict = {}

    for record in results:
        results_dict[record[0]] = record[1]

    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Create a session from Python to the DB

    session = Session(bind = engine)

    # Query the results with station ID and name

    results = session.query(Station.station, Station.name).all()

    session.close()

    # Return a JSON list of station ID and name from the query
 
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create a session from Python to the DB

    session = Session(bind = engine)

    # Query the dates and temperature observations of the most active station for the last year of data

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= "2016-08-23").filter(Measurement.station == "USC00519281").all()

    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year

    return jsonify(results)

@app.route("/api/v1.0/start_date/<start_date>")
def start_date_stats(start_date):

    # Create a session from Python and DB

    session = Session(bind = engine)

    # Query the dates and temperature observations for a given date

    stats_dict = {}
    stats_dict_lst = []
    if start_date < "2010-01-01" or start_date > "2017-08-23":
        return (f"No information for this specific date. Please type another date.")
    else:
        results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).group_by(Measurement.date).all()
        for record in results:
            (date, min_temp, max_temp, avg_temp) = record
            stats_dict[date] = [{"Min_temp": min_temp, "Max_temp": max_temp, "Avg_temp": round(avg_temp, 2)}]
    
    stats_dict_lst.append(stats_dict)
    return jsonify(stats_dict_lst)

@app.route("/api/v1.0/start_end_date/<start_date>/<end_date>")
def start_end_date(start_date, end_date):

    # Create a session from Python to DB

    session = Session(bind = engine)

    # Query the dates and temperature observations for start and end date

    start_end_dict = {}
    start_end_list = []

    if (start_date > end_date) or (start_date == end_date) or (end_date < start_date) or (start_date < "2010-01-01") or (end_date > "2017-08-23"):
        return (f"Dates are out of range or end date needs to be greater than start_date. Please type other dates.")
    else:
        results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).\
                group_by(Measurement.date).all()
        for record in results:
            (date, min_temp, max_temp, avg_temp) = record
            start_end_dict[date] = [{"Min_temp": min_temp, "Max_temp": max_temp, "Avg_temp": round(avg_temp, 2)}]
    
    start_end_list.append(start_end_dict)
    return jsonify(start_end_list)




if __name__ == '__main__':
    app.run(debug=True)
