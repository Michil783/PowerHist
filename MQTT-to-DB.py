#------------------------------------------
#--- Author: Michael Leopoldseder
#--- Date: 02.01.2026
#--- Version: 1.0
#------------------------------------------


import paho.mqtt.client as mqtt
import json
import sqlite3
import time
import datetime
import sys
import logging
import logging.config
import logging.handlers
import configparser
import os

# SQLite DB Name
DB_Name =  ""
newDay = False
updateTodayData = False
lastMonth = 0
lastDay = 0

# MQTT Settings 
MQTT_Broker = "hap-nodejs"
MQTT_Port = 1884
Keep_Alive_Interval = 60
TASMOTA_TOPIC = "tele/CTS_tasmota_SML_C18A90/SENSOR"
MQTT_User = "raspi"
MQTT_Passwd = "trinitron"

# logging
path = os.path.dirname(os.path.realpath(__file__))
logging.config.fileConfig(path+"/MQTT-to-DB.conf")

def init():
	lastMonth = 0
	logging.info( "init()" )
	try:
		conn = sqlite3.connect(DB_Name)
		curs = conn.cursor()
		select = "select * from Power_Data_Month order by Date desc limit 1;"
		last_entry = curs.execute( select )
		rows = curs.fetchall()
		logging.info( last_entry )
		logging.info( rows )
		logging.info( len(rows) )
		if( len(rows) ):
			for row in rows:
				logging.info("last month")
				logging.info( row )
				logging.info("1. %s", datetime.datetime.strptime(row[0], "%Y-%m-%d"))
				logging.info("2. %s", datetime.datetime.strptime(row[0], "%Y-%m-%d").date())
				logging.info("3. %s", datetime.datetime.strptime(row[0], "%Y-%m-%d").date().month)
				lastMonth = datetime.datetime.strptime(row[0], "%Y-%m-%d").date().month
				logging.info("during init last month: %d", lastMonth)
	except:
		logging.info("error during getting last entry from month before")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()
	return lastMonth

def getFirstPowerDateFromDayBefore():
	firstEntryTotal = 0.0
	logging.info( "getFirstPowerDataFromDayBefore()" )
	try:
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "select * from Power_Data where date(Date_n_time) == date('now','localtime','-1 day') ORDER BY Date_n_Time limit 1;"
		logging.info("select: %s", select)
		first_entry = curs.execute( select )
		rows = curs.fetchall()
		logging.info( first_entry )
		logging.info( rows )
		logging.info( len(rows) )
		if( len(rows) ):
			for row in rows:
				logging.info("first entry of yesterday")
				logging.info( row )
				firstEntryTotal = float(row[1])
	except:
		logging.info("error during getting first entry from day before")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()
	return firstEntryTotal

def getLastPowerDataFromDayBefore():
	lastEntryTotal = 0.0
	lastEntryDate = ""
	logging.info("getLastDataFromDayBefore()")
	try:
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "select * from Power_Data where date(Date_n_time) == date('now','localtime','-1 day') ORDER BY Date_n_Time desc limit 1;"
		logging.info("select: %s", select)
		last_entry = curs.execute( select )
		rows = curs.fetchall()
		logging.info( last_entry )
		logging.info( rows )
		logging.info( len(rows) )
		if( len(rows) ):
			for row in rows:
				logging.info("last entry of yesterday")
				logging.info( row )
				lastEntryDate = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S").date().strftime("%Y-%m-%d")
				lastEntryTotal = float(row[1])
	except:
		logging.info("error during getting last entry from day before")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()
	return lastEntryDate, lastEntryTotal

def getLastMonthTotal():
	lastMonthTotal = 0.0
	logging.info("getLastMonthTotal()")
	try:
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "select * from Power_Data_Month order by Date desc limit 1;"
		logging.info("select: %s", select)
		last_entry = curs.execute( select )
		rows = curs.fetchall()
		logging.info( last_entry )
		logging.info( rows )
		logging.info( len(rows) )
		if( len(rows) ):
			for row in rows:
				logging.info("last month")
				logging.info( row )
				lastMonthTotal = float(row[1])
	except:
		logging.info("error during getting last entry from day before")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()
	return lastMonthTotal

def insertNewDayData(newDayDate, newDayTotal, newDayUsed):
	logging.info("insertNewDayData(%s,%6.0f,%3.0f)", newDayDate, newDayTotal, newDayUsed)
	try:
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "insert into Power_Data_Day (Date, Total, Used) values (\""+newDayDate+"\","+str(newDayTotal)+","+str(newDayUsed)+");"
		logging.info( select )
		curs.execute( select )
		logging.info("new day entry in Power_Data_Day")
		conn.commit()
	except:
		logging.info("error during insering new day data")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()

def insertNewMonthData(newMonthDate, newMonthTotal, newMonthUsed):
	logging.info("insertNewMonthData(%s,%6.0f,%3.0f)", newMonthDate, newMonthTotal, newMonthUsed)
	try:
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "insert into Power_Data_Month (Date, Total, Used) values (\""+newMonthDate+"\","+str(newMonthTotal)+","+str(newMonthUsed)+");"
		logging.info( select )
		curs.execute( select )
		logging.info("new month entry in Power_Data_Month")
		conn.commit()
	except:
		logging.info("error during insering new day data")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()

def insertNewData(Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq):
	logging.info("insertNewData(%s, %f, %d, %d, %d, %d, %f, %f, %f, %f)", Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq)
	try:
		logging.info( "Start inserting into DB" )
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "insert into Power_Data (Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq) values (\""+Date_n_Time+ \
			"\","+str(Total)+","+str(Power)+","+str(Voltage)+","+str(Voltage_L2)+","+str(Voltage_L3)+ \
			","+str(Current)+","+str(Current_L2)+","+str(Current_L3)+","+str(Freq)+");"
		logging.info( select )
		curs.execute( select )
		logging.info( "Execute" )
		conn.commit()
		logging.info( "commit" )
		logging.info( "inserted" )
		logging.info( "Inserted Power Data into Database." )
	except:
		logging.info("error during inserting new data")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()

def deleteDataFrom2DaysBefore():
	logging.info("deleteDataFrom2DaysBefore()")
	try:
		conn=sqlite3.connect(DB_Name)
		logging.info( "connection" )
		curs = conn.cursor()
		logging.info( "cursor" )
		select = "delete from Power_Data where date(Date_n_Time) <= date('now','localtime','-2 days');"
		logging.info("delete old day data: %s", select)
		curs.execute( select )
		conn.commit()
		logging.info("commit for delete")
		conn.execute( "vacuum;" )
		logging.info("vacuum executed")
	except:
		logging.info("error during deleteing 2 day old data")
		logging.info( "Unexpected error:", sys.exc_info()[0] )
	conn.close()
	return

# Function to save Temperature to DB Table
def Power_Data_Handler(topic, jsonData):
	global newDay, lastDay, lastMonth
	logging.info( "Power_data_Handler()" )
	logging.info("newDay: %d", newDay)
	json_Dict_root = {}
	try:
		#Parse Data
		if( topic == TASMOTA_TOPIC or topic == TASMOTA_TOPIC_NEW ):
			json_Dict_root = json.loads(jsonData)
		else:
			json_Dict = json.loads(jsonData)
			json_Dict_root = json_Dict["sn"]
		logging.info( json_Dict_root )
		Date_n_Time = json_Dict_root['Time']
		logging.info( "Date_n_Time: %s", Date_n_Time )
		json_Dict = json_Dict_root['ENERGY']
		logging.info( json_Dict )
		Total = float(json_Dict['Total'])
		logging.info( "Total: %6.1f", Total )
		Power = int(json_Dict['Power'])
		logging.info( "Power: %d", Power )
		Voltage = float(json_Dict['Voltage'])
		logging.info( "Voltage: %d", Voltage )
		Voltage_L2 = float(json_Dict['Voltage_L2'])
		logging.info( "Voltage_L2: %d", Voltage_L2 )
		Voltage_L3 = float(json_Dict['Voltage_L3'])
		logging.info( "Voltage_L3: %d", Voltage_L3 )
		Current = float(json_Dict['Current'])
		logging.info( "Current: %3.1f", Current )
		Current_L2 = float(json_Dict['Current_L2'])
		logging.info( "Current_L2: %3.1f", Current_L2 )
		Current_L3 = float(json_Dict['Current_L3'])
		logging.info( "Current_L3: %3.1f", Current_L3 )
		Freq = float(json_Dict['Freq'])
		logging.info( "Freq: %2.1f", Freq )
	except:
		logging.info( "error during reading json dict" )
		logging.info( json_Dict )
		logging.info( "Unexpected error:", sys.exc_info()[0] )

	insertNewData(Date_n_Time, Total, Power, Voltage, Voltage_L2, Voltage_L3, Current, Current_L2, Current_L3, Freq)		
	datetime_obj = datetime.datetime.strptime(Date_n_Time, "%Y-%m-%dT%H:%M:%S") 
	time = datetime_obj.time()
	day = datetime_obj.date().day
	#logging.info("time.hour: %d, newDay: %d", time.hour, newDay)
	#if( (time.hour < 4) and not newDay ):
	logging.info("time.hour: %d, Day: %d, lastDay: %d", time.hour, day, lastDay)
	if( (time.hour < 4) and day != lastDay ):
		logging.info( "Start inserting into day data" )
		#newDay = True
		lastDay = day
		firstEntryTotal = getFirstPowerDateFromDayBefore()
		logging.info("firstEntryTotal: %f", firstEntryTotal)
		result = getLastPowerDataFromDayBefore()
		lastEntryDate = result[0]
		lastEntryTotal = result[1]
		logging.info("lastEntryDate: %s", lastEntryDate)
		logging.info("lastEntryTotal: %f", lastEntryTotal)
		newDayEntry_date = lastEntryDate
		newDayEntry_Total = lastEntryTotal
		newDayEntry_Used =  float("{:06.1f}".format(lastEntryTotal - firstEntryTotal))
		insertNewDayData(newDayEntry_date, newDayEntry_Total, newDayEntry_Used)
		deleteDataFrom2DaysBefore()

		# logging.info( "start inserting actual day into day data" )
		# newDayEntry_date = datetime_obj.date()
		# newDayEntry_Total = Total
		# newDayEntry_Used = Total - newDayEntry_Total
		# logging.info("newDayEntry_date: %s", newDayEntry_date)
		# logging.info("newDayEntry_Total: %6.1f", newDayEntry_Total)
		# logging.info("newDayEntry_Used: %3.1f", newDayEntry_Used)
		# insertNewDayData(newDayEntry_date, newDayEntry_Total, newDayEntry_Used)
		# updateTodayData = True
	#elif( time.hour >= 4 and newDay ):
	elif( time.hour >= 4 and day != lastDay ):
		#logging.info( "set newDay to False" )
		#newDay = False
		logging.info( "set lastDay (%d) to day (%d)", lastDay, day )
		lastDay = day
	
	month = datetime_obj.date().month
	day = datetime_obj.date().day
	#logging.info("day: %d, lastMonth: %d, month: %d, newDay: %d", day, lastMonth, month, newDay)
	logging.info("day: %d, lastMonth: %d, month: %d", day, lastMonth, month)
	if( (day == 1) and (month != lastMonth) ):
		logging.info( "Start inserting into month data" )
		lastMonthTotal = getLastMonthTotal()
		logging.info("lastMonthTotal: %f", lastMonthTotal)
		result = getLastPowerDataFromDayBefore()
		lastEntryDate = result[0]
		lastEntryTotal = result[1]
		logging.info("lastEntryDate: %s", lastEntryDate)
		logging.info("lastEntryTotal: %f", lastEntryTotal)
		newMonthEntry_date = lastEntryDate
		newMonthEntry_Total = lastEntryTotal
		newMonthEntry_Used =  float("{:06.1f}".format(lastEntryTotal - lastMonthTotal))
		insertNewMonthData(newMonthEntry_date, newMonthEntry_Total, newMonthEntry_Used)
		lastMonth = month
	elif month != lastMonth:
		logging.info("day: %d set lastMonth: %d to actual month: %d", day, lastMonth, month)
		lastMonth = month

#Subscribe to all Sensors at Base Topic
def on_connect(mosq, obj, flags, rc):
	global mqttc
	logging.info( "on_connect" )
	mqttc.subscribe(TASMOTA_TOPIC, 0, )

#Save Data into DB Table
def on_message(mosq, obj, msg):
	# This is the Master Call for saving MQTT Data into DB
	# For details of "sensor_Data_Handler" function please refer "sensor_data_to_db.py"
	logging.info( "-------" )
	logging.info( "MQTT Data Received..." )
	logging.info( "MQTT Topic: " + msg.topic )
	#print( "Data: " + msg.payload )
	if( msg.topic == TASMOTA_TOPIC or msg.topic == TASMOTA_TOPIC_ALT or msg.topic == TASMOTA_TOPIC_NEW ):
		Power_Data_Handler(msg.topic, msg.payload)

def on_subscribe(mqttc, obj, mid, reason_code_list):
	print("Subscribed: " + str(mid) + " " + str(reason_code_list))

def read_config( filename ):
	global DB_Name, MQTT_Broker, MQTT_Port, Keep_Alive_Interval, TASMOTA_TOPIC, MQTT_User, MQTT_Passwd
	config = configparser.ConfigParser()
	config.read(filename)
	DB_Name = str(config['Database']['db'])
	MQTT_Broker = str(config['MQTT']['host'])
	MQTT_Port = int(config['MQTT']['port'])
	Keep_Alive_Interval = int(config['MQTT']['keepAlive'])
	TASMOTA_TOPIC = str(config['MQTT']['topic'])
	MQTT_User = str(config['MQTT']['user'])
	MQTT_Passwd = str(config['MQTT']['passwd'])

read_config("MQTT.conf")

lastMonth = init()

logging.info( "start creating mqtt client" )
logging.info("user: "+MQTT_User)
logging.info("passwd: "+MQTT_Passwd)
mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.username_pw_set(MQTT_User, MQTT_Passwd)

# Connect
logging.info( "connect to broker" )
mqttc.connect(MQTT_Broker, MQTT_Port, int(Keep_Alive_Interval))

# Continue the network loop
logging.info( "loop forever" )
mqttc.loop_forever()
