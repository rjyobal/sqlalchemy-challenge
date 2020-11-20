# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Connect to DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Start
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'
        f'<a href="/api/v1.0/stations">/api/v1.0/stations</a><br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'
        f'<a href="/api/v1.0/start">/api/v1.0/start</a><br/>'
        f'<a href="/api/v1.0/start/end">/api/v1.0/start/end</a><br/>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session
    session = Session(engine)
    # Build Query
    last_date = (session
                 .query(Measurement.date)
                 .order_by(Measurement.date.desc())
                 .first()
            )
    last_date = last_date.date
    year, month, day = last_date.split('-')
    year_ago = dt.date(int(year)-1,int(month),int(day))
    results = (session
               .query(Measurement.date,Measurement.prcp)
               .filter(Measurement.date > year_ago)
               .all()
          )
    session.close()
    #Create dictionary
    precipitations = []
    for date, prcp in results:
        precipitations.append({
            date: prcp
        })
    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def station():
    # Create session
    session = Session(engine)
    # Build Query
    results = (session
               .query(Measurement.station.distinct())
               .all()
          )
    session.close()
    #Create dictionary
    stations = []
    for station in results:
        stations.append({
            "station name": station
        })
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tob():
    # Create session
    session = Session(engine)
    # Build Query

    active_station = (session
                      .query(Measurement.station, func.count(Measurement.tobs))
                      .group_by(Measurement.station)
                      .order_by(func.count(Measurement.tobs).desc())
                      .first()
                      .station
                 )

    last_date = (session
                 .query(Measurement.date)
                 .order_by(Measurement.date.desc())
                 .first()
            )
    last_date = last_date.date
    year, month, day = last_date.split('-')
    year_ago = dt.date(int(year)-1,int(month),int(day))

    results = (session
               .query(Measurement.date, Measurement.tobs)
               .filter(Measurement.station==active_station)
               .filter(Measurement.date>=year_ago)
               .all()
          )

    session.close()
    #Create dictionary
    tobs_dict = []
    for date, tobs in results:
        tobs_dict.append({
            date: tobs
        })
    return jsonify(tobs_dict)


if __name__ == '__main__':
    app.run(debug=True)