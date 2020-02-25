# Ignore SQLITE warnings related to Decimal numbers in the Chinook database
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
# Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# List all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<strong>Available Routes:</strong><br/>"
        f"&emsp;/api/v1.0/precipitation<br/>"
        f"&emsp;/api/v1.0/stations<br>"
        f"&emsp;/api/v1.0/tobs<br>"
        f"&emsp;/api/v1.0/&lt;start&gt;<br>"
        f"&emsp;/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )


# Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    # Close the session after use.
    session.close()
    
    # Create a dictionary from the row data and append to a list
    all_precip_dict = {}
    for date, prcp in results:
        all_precip_dict[date] = prcp
        
    return jsonify(all_precip_dict)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Station.station).all()
    
    # Close the session after use.
    session.close()
    
    all_stations = []
    for station in results:
        all_stations.append(station[0])
        
    return jsonify(all_stations)


# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get last date in the database
    results = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Convert results to a date
    last_date = dt.datetime.strptime(results[0], '%Y-%m-%d').date()
    
    # Subtract 1 year from the last date
    year_ago = last_date - dt.timedelta(days=365)
    
    # Query
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    
    # Close the session after use.
    session.close()

    return jsonify(results)



# One Date:
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#
# Two Dates:
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def tobsbydaterange(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    if end == None:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    # end if
    
    # Close the session after use.
    session.close()

    return jsonify(results)


# Debug status
if __name__ == '__main__':
    app.run(debug=False)