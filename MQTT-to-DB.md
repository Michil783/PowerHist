# MQTT-to-DB

This module connects to the MQTT broker and subscribes for the Tasmota topic which could be defined in MQTT.conf file.

```
[Database]
db = /home/pi/PowerHist/Power.db

[MQTT]
host = hap-nodejs
port = 1884
user = raspi
passwd = trinitron
topic = tele/CTS_tasmota_SML_C18A90/SENSOR
keepAlive = 60
```

The config file also holds an entry for the datbase fiule due to the fact, that this module are directly accessing the database. This means that it has to run on the same machine as the SQLite3 DB itself.
