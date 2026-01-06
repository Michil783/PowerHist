# Database

The database has four tables

```CREATE TABLE Power_Data (
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
