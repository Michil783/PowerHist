#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  PowerHist.py
#
#  based on MJRoBot.org 10Jan18
# enhancements and changes by
# Michael Leopoldseder Jan 2026

import io
import time

from flask import Flask, render_template, send_file, make_response, request, jsonify
app = Flask(__name__)

import sqlite3
import json
import configparser
import os
import sys
import argparse

DB_Name = "/home/pi/PowerHist/Power.db"
#cert = "server.crt"
#key = "server.key"
port = 8090
configFile = "PowerHist.conf"

def read_config( filename ):
    global DB_Name, cert, key, port
    config = configparser.ConfigParser()
    config.read(filename)
    DB_Name = str(config['Database']['db'])
    port = int(config['host']['port'])
    #cert = str(config['certificates']['crt'])
    #key = str(config['certificates']['key'])

def getHistDataSingle (sql_query):
    conn=sqlite3.connect(DB_Name)
    curs=conn.cursor()
    curs.execute(sql_query)
    data = curs.fetchall()
    conn.close()
    return data[0][0]


def deleteInvalidData (source):
    #sql_query = "delete from Temperature_Data where Date_n_Time < 28900 AND SensorID='"+source+"'"
    #conn=sqlite3.connect('/home/pi/Store_MQTT_Data_in_Database/IoT.db')
    #curs=conn.cursor()
    #curs.execute(sql_query)
    #conn.commit()
    #conn.close()
    return

@app.route("/power", methods=['GET'])
def powerQuery():
    conn=sqlite3.connect(DB_Name)
    curs=conn.cursor()
    Date_n_Time = ""
    for row in curs.execute("SELECT Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq FROM Power_Data ORDER BY Date_n_Time DESC LIMIT 1"):
        print( row )
        Date_n_Time = row[0]
        Total = float(row[1])
        Power = int(row[2])
        Voltage = float(row[3])
        Voltage_L2 = float(row[4])
        Voltage_L3 = float(row[5])
        Current = float(row[6])
        Current_L2 = float(row[7])
        Current_L3 = float(row[8])
        Freq = float(row[9])
    conn.close()
    templateData = {}
    if Date_n_Time != "":
        templateData = {
            'time': Date_n_Time,
            'Total': Total,
            'Power': Power,
            'Voltage': Voltage,
            'Voltage_L2': Voltage_L2,
            'Voltage_L3': Voltage_L3,
            'Current': Current,
            'Current_L2': Current_L2,
            'Current_L3': Current_L3,
            'Freq': Freq
        }
    response = app.response_class(
        response=json.dumps(templateData),
        status=200,
        mimetype='application/json'
    )
    return response

""" @app.route("/power1d", methods=['GET'])
def powerQuery1d():
    parameter = request.args.get('para')
    data = []
    conn=sqlite3.connect(DB_Name)
    curs=conn.cursor()
    print("SELECT Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq FROM Power_Data where datetime(Date_n_Time) >= (select datetime('now','localtime','"+parameter+"'))")
    for row in curs.execute("SELECT Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq FROM Power_Data where datetime(Date_n_Time) >= (select datetime('now','localtime','"+parameter+"'))"):
        #print( row )
        Date_n_Time = row[0]
        Total = float(row[1])
        Power = int(row[2])
        Voltage = float(row[3])
        Voltage_L2 = float(row[4])
        Voltage_L3 = float(row[5])
        Current = float(row[6])
        Current_L2 = float(row[7])
        Current_L3 = float(row[8])
        Freq = float(row[9])
        template = {
            'time': Date_n_Time,
            'Total': Total,
            'Power': Power,
            'Voltage': Voltage,
            'Voltage_L2': Voltage_L2,
            'Voltage_L3': Voltage_L3,
            'Current': Current,
            'Current_L2': Current_L2,
            'Current_L3': Current_L3,
            'Freq': Freq
        }
        data.append(template)
    conn.close()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response
 """
@app.route("/powerflex", methods=['GET'])
def powerQueryflex():
    select = request.args.get('select')
    data = []
    conn=sqlite3.connect(DB_Name)
    curs=conn.cursor()
    print(select)
    for row in curs.execute(select):
        #print( row )
        Date_n_Time = row[0]
        Total = float(row[1])
        Power = int(row[2])
        Voltage = float(row[3])
        Voltage_L2 = float(row[4])
        Voltage_L3 = float(row[5])
        Current = float(row[6])
        Current_L2 = float(row[7])
        Current_L3 = float(row[8])
        Freq = float(row[9])
        template = {
            'time': Date_n_Time,
            'Total': Total,
            'Power': Power,
            'Voltage': Voltage,
            'Voltage_L2': Voltage_L2,
            'Voltage_L3': Voltage_L3,
            'Current': Current,
            'Current_L2': Current_L2,
            'Current_L3': Current_L3,
            'Freq': Freq
        }
        data.append(template)
    conn.close()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

""""
@app.route("/powermonthflex", methods=['GET'])
def powerQueryMonthFlex():
    select = request.args.get('select')
    data = []
    conn=sqlite3.connect(DB_Name)
    curs=conn.cursor()
    print(select)
    for row in curs.execute(select):
        #print( row )
        Date_n_Time = row[0]
        Total = float(row[1])
        Used = int(row[2])
        template = {
            'time': Date_n_Time,
            'Total': Total,
            'Used': Used,
        }
        data.append(template)
    conn.close()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response
"""

@app.route("/powerhistory", methods=['GET'])
def powerHistoryQuery():
    select = request.args.get('select')
    data = []
    conn=sqlite3.connect(DB_Name)
    curs=conn.cursor()
    print(select)
    for row in curs.execute(select):
        #print( row )
        Date_n_Time = row[0]
        Total = float(row[1])
        Used = float(row[2])
        template = {
            'time': Date_n_Time,
            'Total': Total,
            'Used': Used,
        }
        data.append(template)
    conn.close()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser("PowerHist")
    parser.add_argument("-c", help="config file name") 
    args = parser.parse_args()
    argsdict = vars(args)
    print( args )
    print( argsdict )
    if argsdict["c"]:
        configFile = argsdict["c"]
    myPath = os.path.dirname(os.path.realpath(__file__))
    print("configFile: " + configFile)
    read_config( myPath+"/"+configFile )
    print("db", DB_Name)
    app.run(host='0.0.0.0', port=port, debug=True, extra_files=[])
