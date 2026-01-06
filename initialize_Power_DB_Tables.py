
import sqlite3
import argparse
import configparser
import os

DB_Name = "/home/pi/PowerHist/PowerTest.db"
port = 8090
configFile = "PowerHistTest.conf"

def read_config( filename ):
    global DB_Name, cert, key, port
    config = configparser.ConfigParser()
    config.read(filename)
    DB_Name = str(config['Database']['db'])

# """
# drop table if exists Power_Data ;
# create table Power_Data (
#   Date_n_Time text primary key,
#   Total float,
#   Power integer,
#   Voltage float,
#   Voltage_L2 float,
#   Voltage_L3 float,
#   Current float,
#   Current_L2 float,
#   Current_L3 float,
#   Freq float
# );
# drop table if exists Power_Data_Day ;
# create table Power_Data_Day (
#   Date text primary key,
#   Total float,
#   Used float
# );
# drop table if exists Power_Data_Month ;
# create table Power_Data_Month (
#   Date text primary key,
#   Total float,
#   Used float
# );
# drop table if exists Power_Data_Year ;
# create table Power_Data_Year (
#   Date text primary key,
#   Total float,
#   Used float
# );
# """

# SQLite DB Table Schema
TableSchema="""
drop table if exists Power_Data ;
create table Power_Data (
  Date_n_Time text primary key,
  Total float,
  Power integer,
  Voltage float,
  Voltage_L2 float,
  Voltage_L3 float,
  Current float,
  Current_L2 float,
  Current_L3 float,
  Freq float
);
drop table if exists Power_Data ;
create table Power_Data (
  Date_n_Time text primary key,
  Total float,
  Power integer,
  Voltage float,
  Voltage_L2 float,
  Voltage_L3 float,
  Current float,
  Current_L2 float,
  Current_L3 float,
  Freq float
);
drop table if exists Power_Data_Day ;
create table Power_Data_Day (
  Date text primary key,
  Total float,
  Used float
);
drop table if exists Power_Data_Month ;
create table Power_Data_Month (
  Date text primary key,
  Total float,
  Used float
);
drop table if exists Power_Data_Year ;
create table Power_Data_Year (
  Date text primary key,
  Total float,
  Used float
);
"""
parser = argparse.ArgumentParser("PowerHist")
parser.add_argument("-c", help="config file name") 
args = parser.parse_args()
argsdict = vars(args)
if argsdict["c"]:
    configFile = argsdict["c"]
myPath = os.path.dirname(os.path.realpath(__file__))
read_config( myPath+"/"+configFile )

#Connect or Create DB File
print("using database file: " + DB_Name)
conn = sqlite3.connect(DB_Name)
curs = conn.cursor()

#Create Tables
sqlite3.complete_statement(TableSchema)
curs.executescript(TableSchema)

#Close DB
curs.close()
conn.close()
