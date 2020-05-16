import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import datetime as dt
import numpy as np
import pandas as pd
from flask import Flask, jsonify
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

base = automap_base()
base.prepare(engine, reflect=True)
base.classes.keys()

Measurement = base.classes.measurement
Station = base.classes.station

session = Session(engine)

inspector = inspect(engine)
inspector.get_table_names()


app = Flask(__name__)


@app.route("/")
def home():
    return (f"Welcome to Hawai's Climate<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Here's a list of Available Routes: <br/>"
            f"/api/v1.0/precipitation ~~~~ lists all the precipitation data <br/>"
            f"/api/v1.0/stations ~~~~ lists all the stations <br/>"
            f"/api/v1.0/tobs ~~~~ lists all the temperature observations data")

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    latest_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    latest_date = list(np.ravel(latest_date))[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

    query_date = latest_date - dt.timedelta(days=365)
    results_prcp = session.query(Measurement.date, Measurement.prcp).\
                            filter(Measurement.date > query_date).\
                            order_by(Measurement.date).all()

    prcp_dict = {}

    for date, prcp in results_prcp: 
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations(): 

    station_active = (session.query(Measurement.station, func.count(Measurement.station))
                                .group_by(Measurement.station)
                                .order_by(func.count(Measurement.station).desc())
                                .all())

    station_list = []

    for station in station_active:
        station_list.append(station[0])
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    
    latest_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    latest_date = list(np.ravel(latest_date))[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

    query_date = latest_date - dt.timedelta(days=365)
    
    results_tobs = session.query(Measurement.tobs, Measurement.date).\
                            filter(Measurement.date > query_date).\
                            order_by(Measurement.date).all()

    temps_tobs = []

    for tob, date in results_tobs:
        temps_tobs.append({
            "date": date, 
            "tob": tob
        })
    
    return jsonify(temps_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start): 

    station_active = (session.query(Measurement.station, func.count(Measurement.station))
                                .group_by(Measurement.station)
                                .order_by(func.count(Measurement.station).desc())
                                .all())
    most_active_station = station_active[0][0]

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                           filter(Measurement.station == most_active_station).all()

    temp_data = {}

    temp_data[most_active_station] = temp_stats 

    return jsonify(temp_data)





if __name__ == "__main__":
    app.run(debug=True)
