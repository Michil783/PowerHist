# PowerHist

PowerHist is used to provide a web based interface to the datbase. any other app could fetch data from datbase without having file access to the SQLite3 database file.

The web pages using the Python module flask and is configured via the PowerHist.conf file. The Module could be started with a command line parameter to use any specific config file. By default (without any parameter) the PowerHist.conf file in the working directory is used. To use a specific file the parameter is **"-c configFile"**

Content of the conf file is

```
[Database]
db = /home/pi/PowerHist/Power.db

[host]
port=8090
```

**[Database]** is the section for the database configuration. You have to specify the database name in field **"db"**

**[host]** is the section for spefifying the web server. IN this case the only parameter is the **port** on which the interface is provided.

## The following URLs are provided to access the database:

/power

This URL has no parameters and is fetching the latest entry in database for table Power_Data

/powerflex

This URL has a SQLite3 select statement as parameter to fetch data from the Power_Data table in the database.
e.g. http://powerhisthost:8090/powerflex?select=select * from power_data;

/powerhistory

This URL is used to fetch data from the tables Power_Data_Day, Power_Data_Month and Power_Data_Year. It uses a SQLite3 select statement as parameter.
e.g. http://powerhisthost:8090/powerhistory?select=select * from power_data_day;