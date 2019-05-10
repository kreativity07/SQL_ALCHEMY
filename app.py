import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start<br/>/end<br/>"
        )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returning Precipitation"""
    # Query dates and precip
    results = session.query(Measurement.prcp, Measurement.date).all()

    # Convert list of tuples into normal list
    prcp_dict = []
    for result in results:
        prcp = {}
        prcp["precipitation"] = result.prcp
        prcp["date"] = result.date
        prcp_dict.append(prcp)
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Returning list of stations"""
    # Query all stations
    stations = session.query(Station.station).all()

    results = list(np.ravel(stations))
    return jsonify(results)


@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point.
Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # Query
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >='2016-08-23').all()
    tobs = list(np.ravel(tobs_results))
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def start_stats1(start=None):
    """Return a json list of the minimum temperature for a given start date"""

    # Query all the stations for Tmin. 
    low_results = session.query(Measurement.station, func.min(Measurement.tobs)).filter_by(station='USC00519281').all()

    # Query all the stations for Tmax. 
    high_results = session.query(Measurement.station, func.max(Measurement.tobs)).filter_by(station='USC00519281').all()

    # Query all the stations for Tavg. 
    avg_results = session.query(Measurement.station, func.avg(Measurement.tobs)).filter_by(station='USC00519281').all()
    
   
    # Create a dictionary from the row data and append to a list of for the low, high & average temperature data.
    low_temp = []
    high_temp = []
    avg_temp = []
    temp_dict = {}
  
    for Tmin in low_results:
        low_temp_dict = {}
        temp_dict["Minimum Temp"] = Tmin
        low_temp.append(low_temp_dict)
    
    for Tmax in high_results:
        high_temp_dict = {}
        temp_dict["Maximum Temp"] = Tmax
        high_temp.append(high_temp_dict)

    for Tavg in avg_results:
        avg_temp_dict = {}
        temp_dict["Average Temp"] = Tavg
        avg_temp.append(avg_temp_dict)
    
    return jsonify(temp_dict)
@app.route("/api/v1.0/<start>/<end>")
def calc_stats(start=None, end=None):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    
    # Query all the stations and for the given range of dates. 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= '2016-08-23').filter(Measurement.date <= '2017-08-23').all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    begin_end_stats = []
    
    for Tmin, Tmax, Tavg in results:
        begin_end_stats_dict = {}
        begin_end_stats_dict["Minimum Temp"] = Tmin
        begin_end_stats_dict["Maximum Temp"] = Tmax
        begin_end_stats_dict["Average Temp"] = Tavg
        begin_end_stats.append(begin_end_stats_dict)
    
    return jsonify(begin_end_stats)


if __name__ == '__main__':
    app.run(debug=True)