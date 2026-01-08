# Database

The database has four tables

```
CREATE TABLE Power_Data (
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
CREATE TABLE Power_Data_Month (
Date text primary key,
Total float,
Used float
);
CREATE TABLE Power_Data_Year (
Date text primary key,
Total float,
Used float
);
CREATE TABLE Power_Data_Day (
Date text primary key,
Total float,
Used float
);
```

The table Power_Data is used to store the actual values received from Tasmota device. In powerHist.py this table will be cleaned to keep only the data for 2 complete days. I configured my Tasmota device to transmit every 10 seconds data to the system. This means that this table normaly holds 6 * 60 * 24 * 3 (6 per minute * 60 minutes * 24 hours * 3 days) 25920 datasets.
The MQTT-to-DB.py cleans the oldes day after the third day is completed.

Table Power_Data_Day keeps the data for a complete day. PowerHist.py is filling up this table when a new day starts.
Currently no automatic cleaning of this table is done. It will be part of future enhancements of MQTT-to-DB.py. So you have to clean it manually once in a while before database file will be to large.

Table Power_Data_Month is used for the monthly values and is also filled up from MQTT-to-DB.py after a new month starts. No autocleaning is done here (future enhancements).

Table Power_Data_Year stores values from past years.
The web page PowerStation.py is fetching values from this table to display the current years used power and the useage from year before. You have to insert the value from last year manually by using the following SQLite3 SQL statement:

```
insert into power_data_year (date,total,used) values("YYYY-MM-DD",TTTT.T,UUUU.U);
```

YYYY = year\
MM = month (normaly 12)\
DD = day (normaly 31)\
TTTT.T last years total value of the power meter\
UUUU.U last years power consumption\

MQTT-to-DB.py module is inserting a new entry into this table when year number is changing
