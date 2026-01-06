# Tasmota confguration

The configuration of the Tasmota device depends on the powermeter which is installed in your environment. Depending on the manufacturer you have to configure your Tasmota device. Import for the project is that the following data are transmitted to MQTT broker:

Comsumption,kWh,Total
Actual Power,W,Power
Voltage L1,V,Voltage
Voltage L2,V,Voltage_L2
Voltage L3,V,Voltage_L3
Current L1,A,Current
Current L2,A,Current_L2
Current L3,A,Current_L3
Frequency,Hz,Freq

The values as well as the names within the JSON block is important for the project. If not all data is available with your powermeter or you want to name it different you have to adapt the complete tool chain MQTT-to-DB.py, PowerHist.py and PowerStation.py.