#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  PowerStation.py
#  
# Michael Leopoldseder April 2025

#import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import matplotlib.patches as mpatches
import numpy as np
import io
import time
import json
import requests
from user_agents import parse
from datetime import datetime, timedelta
import logging
import logging.config
import configparser
import os
import sys
import locale

from functools import wraps

from flask import Flask, render_template, send_from_directory, make_response, redirect, url_for, request, session
from flask_mobility import Mobility

app = Flask(__name__)
Mobility(app)

# logging
path = os.path.dirname(os.path.realpath(__file__))
#logging.basicConfig(filename='mqtt_listen_sensor_data.log', encoding='utf-8', level=logging.INFO)
logging.config.fileConfig("PowerStation.conf")

ownPort = 8091
dbInterfaceHost = "hap-nodejs"
dbInterfacePort = 8090
cert = ""
key = ""

def read_config_data( filename ):
	global ownPort, cert, key, dbInterfaceHost, dbInterfacePort
	config = configparser.ConfigParser()
	config.read(filename)
	dbInterfaceHost = str(config['DBInterface']['host'])
	dbInterfacePort = int(config['DBInterface']['port'])
	ownPort = int(config['host']['port'])
	cert = str(config["certificates"]["cert"])
	key = str(config["certificates"]["key"])

# define and initialize global variables
time_of_update = 0
timeFormat = "%d.%m.%y %H:%M:%S"

templateData = {}

toMatch = ["Android", "webOS", "iPhone", "iPad", "iPod", "BlackBerry", "Windows Phone"]

def check_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.info(request)
        ###  Here I need the IP address and port of the client
        logging.info("The client IP is: {}".format(request.environ['REMOTE_ADDR']))
        logging.info("The client port is: {}".format(request.environ['REMOTE_PORT']))
        return f(*args, **kwargs)
    return decorated_function

# main route
@app.route("/")
@check_auth
def index():
	global templateData
	user_agent = request.headers.get('User-Agent')
	logging.info("user_agent: %s", user_agent)
	user_agent_parsed = parse(user_agent)
	device_type = ("Mobile" if user_agent_parsed.is_mobile else
                   "Tablet" if user_agent_parsed.is_tablet else
                   "Desktop")
	logging.info( f"Device Type: {device_type}, Browser: {user_agent_parsed.browser.family}" )
	data = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/power").json()
	logging.info( "DB request result: " )
	logging.info( json.dumps(data, indent=2) )
	default_loc = locale.getlocale()
	locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
	date_n_time = data["time"]
	locale.setlocale(locale.LC_ALL, default_loc)
	total=float("{:06.1f}".format(data["Total"]))
	power=data["Power"]

	currentMonth = datetime.now().month
	logging.info( "currentMonth: %d", currentMonth )
	logging.info("currentMonth: %d %s", currentMonth, str(currentMonth-1).zfill(2))
	#select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Month where strftime('%m', Date) == strftime('%m', Date('now','-1 month')) order by Date desc limit 1;"
	select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powermonthflex?select=select * from Power_Data_Month where strftime('%m',Date) == '"+str(currentMonth-1).zfill(2)+"' order by date desc limit 1"
	if currentMonth == 1:
		select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powermonthflex?select=select * from Power_Data_Month where strftime('%m',Date) == '"+str(12)+"' order by date desc limit 1"
	data = requests.get(select).json()
	total_month_before = total_value_before = 0.0
	total_month = 0.0
	if( len(data) ):
		logging.info( "Power_Data_Month before: " )
		logging.info( data[0] )
		total_month_before = float("{:06.1f}".format(data[0]['Used']))
		total_value_before = float("{:06.1f}".format(data[0]['Total']))
		total_month = float("{:06.1f}".format(total - data[0]['Total']))
	# else:
	# 	logging.info("no month before in DB, insert it")
	# 	total_month_before = 0.0
	# 	total_month = 0.0
	# 	old_total = 0.0
	# 	old_date = "2025-04-30"
	# 	#select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Month where strftime('%m', Date) == strftime('%m', Date('now','-1 month')) order by Date desc limit 1;"
	# 	select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Month where strftime('%m', Date) == '"+str(currentMonth-1).zfill(2)+"' order by Date desc limit 1;"
	# 	if currentMonth == 1:
	# 		select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Month where strftime('%m', Date) == '"+str(12)+"' order by Date desc limit 1;"
	# 	data = requests.get(select).json()
	# 	if( len(data) ):
	# 		logging.info( "last data in month before: " )
	# 		logging.info( data[0] )
	# 		old_total = float("{:06.1f}".format(data[0]['Total']))
	# 		old_date = data[0]['Date_n_Time']
	# 		total_month = float("{:06.1f}".format(total - data[0]['Total']))
	# 	data = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data where datetime(Date_n_time) >= datetime('now','-1 months') and date(Date_n_Time) < date('now') ORDER BY Date_n_Time desc limit 1;").json()
	# 	if( len(data) ):
	# 		logging.info( "first data in month before: " )
	# 		logging.info( data[0] )
	# 		total_month_before = old_total - float("{:06.1f}".format(data[0]['Total']))
	# 	data = request.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=insert into Power_Data_Month(Date,Total,Used) values(strftime('%Y-%m-%d', '"+old_date+"'),"+old_total+","+total_month_before+");")
	# 	if( len(data) ):
	# 		logging.info( data[0] )

	data = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Year where strftime('%Y', Date) == strftime('%Y', Date('now','-1 year'));").json()
	total_year_before = 0.0;
	total_year = 0.0
	if( len(data) ):
		logging.info( data[0] )
		total_year_before = float("{:06.1f}".format(data[0]['Used']))
		total_year = float("{:06.1f}".format(total - data[0]['Total']))
	templateData = {
		'total': total,
		'date_n_time': datetime.strptime(date_n_time,"%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y %H:%M:%S"),
		'power': power,
		'total_month': total_month,
		'total_month_before': total_month_before,
		'total_value_before': total_value_before,
		'total_year': total_year,
		'total_year_before': total_year_before,
	}
	logging.info("templateData:")
	logging.info(templateData)
	if( device_type == "Mobile" ):
		return render_template('PowerStationMobile.html', **templateData)
	else:
		return render_template('PowerStation.html', **templateData)

@app.route("/Total")
@check_auth
def Total():
	global templateData
	logging.info( "app.route(\"/Total\")" )
	logging.info( templateData )
	return render_template('Total.html', **templateData)

@app.route("/Power")
@check_auth
def Power():
	global templateData
	logging.info( "app.route(\"/Power\")" )
	logging.info( templateData )
	return render_template('Power.html', **templateData)

@app.route("/Current")
@check_auth
def Current():
	global templateData
	logging.info( "app.route(\"/Current\")" )
	logging.info( templateData )
	return render_template('Current.html', **templateData)

@app.route("/PowerThisWeek")
@check_auth
def PowerThisWeek():
	global templateData
	logging.info( "app.route(\"/PowerThisWeek\")" )
	logging.info( templateData )
	return render_template('PowerThisWeek.html', **templateData)

@app.route("/PowerThisMonth")
@check_auth
def PowerThisMonth():
	global templateData
	logging.info( "app.route(\"/PowerThisMonth\")" )
	logging.info( templateData )
	return render_template('PowerThisMonth.html', **templateData)

@app.route("/PowerHistory")
@check_auth
def PowerHistory():
	#history = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/power1d?para=-24 hour").json()
	history = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerflex?select=select * from Power_Data where datetime(Date_n_Time) > datetime('now', '-22 hours');").json()
	numSamples = len(history)
	logging.info( "entries in last 24 hours: %d", len(history) )
	powers = []
	times = []
	i = 0
	while i < numSamples:
		row = history[i]
		times.append(row["time"])
		powers.append(row['Power'])
		i += 1
	dateaxis = []
	ys = powers
	fig = Figure(figsize = (9,3), facecolor='#000000', edgecolor='#000000')
	axis = fig.add_subplot(1, 1, 1)
	fig.subplots_adjust(left=0.1, right=0.99, top=0.99, bottom=0.2)
	fig.tight_layout()

	axis.grid(True)
	xs = range(0,numSamples,1)
	i = 0
	steps = int( round((len(xs)/24)+0.5) )
	while i < len(xs):
		past = datetime.strptime(times[xs[i]], '%Y-%m-%dT%H:%M:%S')
		dateaxis.append(str( int(round((datetime.now() - past).total_seconds()/60/60)) * -1 ))
		i = i+steps
	axis.set_xticks(range(0,len(xs),steps))
	axis.set_xticklabels(dateaxis)
	axis.xaxis.label.set_color('white')
	axis.tick_params(axis='x', colors='white')
	axis.yaxis.label.set_color('white')
	axis.tick_params(axis='y', colors='white')
	axis.spines['bottom'].set_color('white')
	axis.spines['top'].set_color('white')
	axis.spines['left'].set_color('white')
	axis.spines['right'].set_color('white')
	axis.set_facecolor((0,0,0))
	axis.set_ylabel("W", color="white")

	axis.grid(True)
	axis.plot(xs, ys)
	#make_axes_area_auto_adjustable(axis.get_xaxis(), pad=0.1)
	#make_axes_area_auto_adjustable(axis.get_yaxis(), pad=0.1)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	response.headers['Cache-Control'] = 'no-store'
	return response

@app.route("/CurrentCurrent")
@check_auth
def CurrentCurrent():
	history = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerflex?select=select * from Power_Data order by Date_n_time desc limit 1;").json()
	logging.info(history)
	numSamples = len(history)
	logging.info( "last entry: %d, %d", len(history), numSamples )
	current = []
	labels = ["L1", "L2", "L3"]
	i = 0
	while i < numSamples:
		row = history[i]
		logging.info("row: %s", row)
		current.append(row["Current"])
		logging.info("Current L1: %2.1f", row["Current"])
		current.append(row["Current_L2"])
		logging.info("Current L2: %2.1f", row["Current_L2"])
		current.append(row["Current_L3"])
		logging.info("Current L3: %2.1f", row["Current_L3"])
		i = i + 1

	logging.info(current)
	logging.info(labels)
	fig, ax = plt.subplots(figsize=(4, 4), layout='constrained', facecolor='#000000', edgecolor='#FFFFFF')
	ax.tick_params(axis='x', colors='white')
	ax.tick_params(axis='y', colors='white')
	ax.set_facecolor((0,0,0))
	ax.grid(True, axis='y')
	ax.spines['bottom'].set_color('white')
	ax.spines['top'].set_color('white')
	ax.spines['left'].set_color('white')
	ax.spines['right'].set_color('white')
	ax.set_ylabel("A", color="white")
	ax.set_title("Aktueller Strom", loc="center")
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

	# Determine bar widths
	width_bar = 0.8

	# i = 0
	# while i < numSamples:
	# 	ax.bar(i, powers[i], width_bar, tick_label=times[i], align='center', color=colors[i])
	# 	i += 1
	ax.bar(labels, current)
	i = 0
	while i < 3:
		ax.text(i, current[i]+0.05, str("{:.1f}".format(current[i])), color="white", horizontalalignment='center', fontsize=12)
		i += 1

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	response.headers['Cache-Control'] = 'no-store'
	return response

@app.route("/PowerThisWeekImg")
@check_auth
def PowerThisWeekImg():
	logging.info("PowerThisWeekImg()")
	numSamples = 7
	powers = [0, 0, 0, 0, 0, 0, 0]
	times = ["Mo","Di","Mi","Do","Fr","Sa","So"]
	colors = ["tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue"]
	cyanPatch = mpatches.Patch(color="cyan",label="letzte Woche")
	bluePatch = mpatches.Patch(color="blue", label="aktuelle Woche")
	greenPatch = mpatches.Patch(color="green",label="aktueller Tag")
	index = np.arange(len(times))
	dayOfWeek = currentDayOfWeek = datetime.weekday(datetime.now())
	logging.info( "dayOfWeek: %d", dayOfWeek )
	colors[dayOfWeek] = "tab:green"
	today = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerflex?select=select * from Power_Data where Date(Date_n_time) == Date('now','localtime') ORDER BY Date_n_Time desc limit 1;").json()
	logging.info( "today result:" )
	logging.info( today )
	currentTotal = today[0]['Total']
	logging.info("currentTotal: %3.1f", currentTotal)
	select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Day where Date(Date) == Date('now','localtime','-1 days');"
	logging.info( select )
	ending = requests.get( select ).json()
	if( len(ending) >= 1 ):
		powers[dayOfWeek] = currentTotal - ending[0]['Total']
	i = 0
	logging.info("fetch history day data");
	while i < 7:
		dayOfWeek -= 1
		if( dayOfWeek == -1 ):
			dayOfWeek = 6
		logging.info( "dayOfWeek: %d", dayOfWeek )
		logging.info( "day index: %d", i )
		select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerhistory?select=select * from Power_Data_Day where Date(Date) == Date('now','localtime','"+str((0-i-1))+" days');"
		logging.info( select )
		ending = requests.get( select ).json()
		logging.info( "DB query result:" )
		logging.info( ending )
		if( len(ending) >= 1):
			#endingTotal = ending[0]['Total']
			if( dayOfWeek == currentDayOfWeek ):
			#	powers[dayOfWeek] = currentTotal - endingTotal
				pass
			else:
				powers[dayOfWeek] = ending[0]['Used']
			if( dayOfWeek < datetime.weekday(datetime.now()) ):
				colors[dayOfWeek] = "tab:blue"
			elif( dayOfWeek == datetime.weekday(datetime.now()) ):
				colors[dayOfWeek] = "tab:green"
			else:
				colors[dayOfWeek] = "tab:cyan"
			#currentTotal = endingTotal
			i = i + 1
			#dayOfWeek -= 1
			#if( dayOfWeek == -1 ):
			#	dayOfWeek = 6
		else:
			i = i + 1
	logging.info( "week data:" )
	logging.info( powers )
	fig, ax = plt.subplots(figsize=(8, 5), layout='constrained', facecolor='#000000', edgecolor='#FFFFFF')
	ax.tick_params(axis='x', colors='white')
	ax.tick_params(axis='y', colors='white')
	ax.set_facecolor((0,0,0))
	ax.grid(True, axis='y')
	ax.spines['bottom'].set_color('white')
	ax.spines['top'].set_color('white')
	ax.spines['left'].set_color('white')
	ax.spines['right'].set_color('white')
	ax.set_ylabel("kW", color="white")
	ax.set_title("Verbrauch pro Tag", loc="center")
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
	plt.figlegend(loc='lower center', fancybox=True, shadow=True, handles=[cyanPatch,bluePatch, greenPatch])

	# Determine bar widths
	width_bar = 0.8

	# i = 0
	# while i < numSamples:
	# 	ax.bar(i, powers[i], width_bar, tick_label=times[i], align='center', color=colors[i])
	# 	i += 1
	ax.bar(times, powers, color=colors)
	i = 0
	while i < numSamples:
		ax.text(i, powers[i]+0.1, str("{:.1f}".format(powers[i])), color="white", horizontalalignment='center', fontsize=12)
		i += 1

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	response.headers['Cache-Control'] = 'no-store'
	return response

@app.route("/PowerThisMonthImg")
@check_auth
def PowerThisMonthImg():
	logging.info( "PowerThisMonthImg()" )
	numSamples = 12
	powers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	times = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
	colors = ["tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue"]
	cyanPatch = mpatches.Patch(color="cyan",label="letztes Jahr")
	bluePatch = mpatches.Patch(color="blue", label="aktuelles Jahr")
	greenPatch = mpatches.Patch(color="green",label="aktueller Monat")
	index = np.arange(len(times))
	currentMonth = datetime.now().month
	logging.info( "currentMonth: %d", currentMonth )
	colors[currentMonth-1] = "tab:green"
	powers[currentMonth-1] = 0.0
	currentTotal = 0.0
	today = requests.get("http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powerflex?select=select * from Power_Data where Date(Date_n_time) == Date('now','localtime') ORDER BY Date_n_Time desc limit 1;").json()
	if( len(today) ):
		#logging.info( today )
		currentTotal = today[0]['Total']
	logging.info("currentTotal: %6.1f", currentTotal)
	#strftime('%m',datetime('now','-1 Month')
	tempCurrentMonth = currentMonth
	if( currentMonth == 1 ):
		tempCurrentMonth = 12
	else:
		tempCurrentMonth = currentMonth - 1
	logging.info("currentMonth: %d %s", tempCurrentMonth, str(tempCurrentMonth).zfill(2))
	#select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powermonthflex?select=select * from Power_Data_Month where strftime('%m',Date) == strftime('%m',datetime('now','-1 Month') order by date desc limit 1"
	select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powermonthflex?select=select * from Power_Data_Month where strftime('%m',Date) == '"+str(tempCurrentMonth).zfill(2)+"' order by date desc limit 1"
	logging.info("requestStr: %s", select)
	data = requests.get(select).json() 
	if( len(data) ):
		powers[currentMonth-1] = float("{:03.1f}".format(currentTotal - data[0]["Total"]))
	logging.info( "currentMonth: %3.1f", powers[currentMonth-1] )

	i = 1
	diff = -1
	while i <= 12:
		logging.info("i: %d", i)
		if( i == currentMonth ):
			#diff = -11
			diff = 0
		else:
			if( i < currentMonth ):
				diff = i - currentMonth
				colors[i-1] = "tab:blue"
			else:
				diff = diff + 1 
				colors[i-1] = "tab:cyan"
			#select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powermonthflex?select=select * from Power_Data_Month where strftime('%m',Date) == strftime('%m',Date('now','"+str(diff)+" Month')) order by date desc limit 1;"
			select = "http://"+dbInterfaceHost+":"+str(dbInterfacePort)+"/powermonthflex?select=select * from Power_Data_Month where strftime('%m',Date) == '"+str(currentMonth+diff).zfill(2)+"' order by date desc limit 1;"
			logging.info(select)
			used = requests.get(select).json()
			if( len(used) >= 1):
				logging.info( "diff: %d", diff )
				logging.info( used )
				powers[i-1] = used[0]['Used']
		logging.info( powers )
		i = i + 1

	fig, ax = plt.subplots(figsize=(10,5), layout='constrained', facecolor='#000000', edgecolor='#FFFFFF')
	ax.tick_params(axis='x', colors='white')
	ax.tick_params(axis='y', colors='white')
	ax.set_facecolor((0,0,0))
	ax.grid(True, axis='y')
	ax.spines['bottom'].set_color('white')
	ax.spines['top'].set_color('white')
	ax.spines['left'].set_color('white')
	ax.spines['right'].set_color('white')
	ax.set_ylabel("kW", color="white")
	ax.set_title("Verbrauch pro Monat", loc="center")
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.95])
	plt.figlegend(loc='lower center', fancybox=True, shadow=True, handles=[cyanPatch,bluePatch, greenPatch])
	# Determine bar widths
	width_bar = 0.8

	# i = 0
	# while i < numSamples:
	# 	ax.bar(i, powers[i], width_bar, tick_label=times[i], align='center', color=colors[i])
	# 	i += 1
	ax.bar(times, powers, color=colors)
	i = 0
	while i < numSamples:
		ax.text(i, powers[i]+0.1, str("{:.1f}".format(powers[i])), color="white", horizontalalignment='center', fontsize=10)
		i += 1

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	response.headers['Cache-Control'] = 'no-store'
	return response

@app.after_request
def add_header(response):
	if 'Cache-Control' not in response.headers:
		response.headers['Cache-Control'] = 'no-store'
	return response

@app.route("/static/<path:path>")
def static_dir(path):
	logging.info( "fetching: %s", path)
	return send_from_directory("static", path)

if __name__ == "__main__":
	locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
	app.config["TEMPLATES_AUTO_RELOAD"] = True
	app.config['SECRET_KEY'] = os.urandom(24)
	app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours = 1)
	myPath = os.path.dirname(os.path.realpath(__file__))
	read_config_data( myPath+'/PowerStation.ini' )

	if( cert != "" and key != "" ):
		logging.info("starting webserver with https")
		logging.info("cert: %s", cert)
		logging.info("key:  %s", key)
		app.run(host='0.0.0.0', port=ownPort, debug=True, ssl_context=(cert,key))
	else:
		logging.info("starting webserver with http")
		app.run(host='0.0.0.0', port=ownPort, debug=True)



