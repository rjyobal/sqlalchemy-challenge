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
# Route ROOT
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'
        f'<a href="/api/v1.0/stations">/api/v1.0/stations</a><br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'
        f'<a href="/api/v1.0/start">/api/v1.0/start</a> Replace "start" with date: [yyyy-mm-dd]<br/>'
        f'<a href="/api/v1.0/start/end">/api/v1.0/start/end</a> Replace "start & end" with dates: [yyyy-mm-dd]<br/>'
    )

# Route Precipitations
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

# Route Stations
@app.route("/api/v1.0/stations")
def station():
    # Create session
    session = Session(engine)
    # Build Query
    results = (session
                .query(Measurement.station.distinct(), Station.name)
                .filter(Measurement.station==Station.station)
               .all()
          )
    session.close()
    #Create dictionary
    stations = []
    for station, name in results:
        stations.append({
            "station": station,
            "station name": name            
        })
    return jsonify(stations)

# Route Temperature Observations
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

# Route Start Date
@app.route("/api/v1.0/<start>")
def startdate(start):
    # Create session
    session = Session(engine)
    # Build Query
    results = (session
               .query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))
               .filter(Measurement.date>=start)
               .all()
          )
    session.close()
    #Create dictionary
    temps = []
    for m_min, m_max, m_avg in results:
        temps.append({
            "Min": m_min,
            "Max": m_max,
            "Avg": m_avg
        })
        return jsonify(temps)

# Route Start Date & End Date
@app.route("/api/v1.0/<start>/<end>")
def startenddate(start, end):
    # Create session
    session = Session(engine)
    # Build Query
    results = (session
               .query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))
               .filter(Measurement.date>=start)
               .filter(Measurement.date<=end)
               .all()
          )
    session.close()
    #Create dictionary
    temps = []
    for m_min, m_max, m_avg in results:
        temps.append({
            "Min": m_min,
            "Max": m_max,
            "Avg": m_avg
        })
        return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)