# PowerHist

This is a system to get data from a snart power meter using the Tasmota reading device. Details about Tasmota based reading devices could be found here:

https://tasmota.github.io/docs/Smart-Meter-Interface/#efr-sgm-c2c4d4-sml

This system is based on an Raspberry Pi hosting an MQTT broker (mosquitto broker) to receive the data from the device. How to setup the broker could be found on several places in the internet. For storing the data a sqlite3 database is used (how to install sqlite3 on Raspberry Pi could be found in the internet). If you want to use any other DB you probably have to adapt the code. I used plain SQL statements but probably they are sqlite3 specific.
For automatic starting and controlling the web pages and the MQTT client for storing data into DB I used pm2 (details could be found in the internet e.g. here: https://pm2.keymetrics.io).

So, the base system depends on four blocks

- Raspberry Pi
  (I used an Raspberry Pi 4)
- Mosquitto MQTT broker
- SQLite3
- PM2

In addition there are 3 parts which are in this repository.

- PowerHist.py
  Web server for fetching Database data for Stromzaehler Web Page PowerStation
  More details could be found here: [PowerHist](PowerHist.md)

- MQTT-to-DB.py
  Application connecting to MQTT broker and getting data from Tasmota Power meter reader to insert into database
  More details could be found here: [MQTT-to-DB](MQTT-to-DB.md)

- PowerStation
  This is an web application (or web pages) to display the power data received from Tasmota device and stored in the database. It will use the PowerHist.py part to access the database. This part could also be deployed on an other Raspberry Pi due to access to SQLite database via the PowerHist.py (no direct access to DB)
  More details could be found here: [PowerStation](PowerStation/README.md)

Currently I'm also working on an iOS application to display the data directly on an Apple device. This app is also using the interface to the Database provided by PowerHist.py adn the MQTT broker.
