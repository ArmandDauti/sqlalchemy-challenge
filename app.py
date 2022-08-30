import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>  #start<br/>"
        f"/api/v1.0/<start>/<end> #start/end date"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    result = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()
    
    all_prcp = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()

    session.close

    station_list = list(np.ravel(results))

    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date.date, '%Y-%m-%d').date()

    query_date = last_date - dt.timedelta(days=364)

    active_station_lst = [Measurement.station, func.count(Measurement.station)]
    active_station = session.query(*active_station_lst).group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).first().station

    active_station_temp = session.query(Measurement.date, Measurement.tobs).\
                        filter(func.strftime('%Y-%m-%d', Measurement.date) > query_date).\
                        filter(Measurement.station == active_station).all()
    
    session.close()

    all_temp = []
    for date, temp in active_station_temp:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['Temperature'] = temp
        all_temp.append(temp_dict)

    return jsonify(all_temp)



@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= f'{start}').first()
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= f'{start}').first()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= f'{start}').first()

    session = Session(engine)

    return jsonify([f'minTemp = {TMIN[0]}, maxTemp = {TMAX[0]}, avgTemp = {round(TAVG[0],2)}'])



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session = Session(engine)
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= f'{start}').filter(Measurement.date <= f'{end}').first()
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= f'{start}').filter(Measurement.date <= f'{end}').first()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= f'{start}').filter(Measurement.date <= f'{end}').first()

    session = Session(engine)

    return jsonify([f'minTemp = {TMIN[0]}, maxTemp = {TMAX[0]}, avgTemp = {round(TAVG[0],2)}'])



if __name__ == '__main__':
    app.run(debug=True)