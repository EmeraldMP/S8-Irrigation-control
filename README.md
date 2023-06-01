# S8 Irrigation Control

## Overview

This project focuses on irrigation control for potato crops. The code provided searches for optimal irrigation values based on a given date, with the aim of maximizing the total plant weight for wheat (TWAD) while minimizing water use. The model takes into account various factors, including weather parameters such as rainfall, humidity, and temperature, as well as management parameters like location, past irrigations, and the type of crop, which can be changed by the user.

## Installation

To run the code, ensure that you have a Windows 10 device with Python 3.8 installed. The code also requires the DSSAT (Decision Support System for Agrotechnology Transfer) version 4.8 library. You can download it by following the instructions here: [https://dssat.net/main-download/](https://dssat.net/main-download/).

Install the necessary libraries by running the following code in the terminal (Windows):

```bash
pip install -r requirements.txt
```

## Data

In order to improve the accuracy of the crop modeling, you can provide weather and management data by creating a weather and management station. The data should follow the formats described below:

### Weather File

The weather file should have at least the following columns: date, maximum temperature, minimum temperature, relative humidity, and rainfall. You can use the `Data\Weather\Essai irrigation.xlsx` file as an example.

The main column headers and data types are as follows:
- `dateLocale` (Date): The local date in the format "YYYY-MM-DD HH:MM:SS".
- `RAIN_FALL` (Numeric): Rainfall measurement in an unspecified unit.
- `RELATIVE_HUMIDITY` (Numeric): Relative humidity measurement.
- `TEMPERATURE_MAX` (Numeric): Maximum temperature measurement.
- `TEMPERATURE_MIN` (Numeric): Minimum temperature measurement.

Here's an example row of data from the Excel file:

| dateLocale          | RAIN_FALL | RELATIVE_HUMIDITY | TEMPERATURE | TEMPERATURE_MAX | TEMPERATURE_MIN | ... |
|---------------------|-----------|------------------|-------------|-----------------|-----------------|-----|
| 2022-04-01 00:00:00 | 0         | 84.65            | 1.16        | 1.88            | 1.16            | ... |

### Management File

The management file should have at least the following columns: date/time and irrigation (precipitation). You can use the `Data\Probes\Sonde Robot 2.xlsx` file as an example for the column format.

The main column headers and data types are as follows:
- `Date/heure` (Date/Time): The date and time in a specific format.
- `Précipitations [mm]` (Numeric): Precipitation measurement in millimeters.

Here's an example row of data from the Excel file:

|                     | Précipitations [mm] | ... |
|---------------------|---------------------|-----|
| Date/heure          | Somme               | ... |
| 2022-09-07 17:00:00 | 0.20                | ... |


## Running the Code

The `main.py` file runs the code and calls other functions and objects.

 It first creates an object called `CreateDSSAT`, which will be described later. Then, the weather and management stations should be created. There are three ways to build them:

1. Extract data from an Excel file: If you have your own data, you can provide the data paths, and the code will create the stations based on that. Use the following lines to create the stations:
```python
CreateDSSAT.create_wth_station("wth_path")
CreateDSSAT.create_management("man_path")
```

2. Create a default sample: If you don't provide any data paths, a random sample will be created for testing purposes. This is the default mode. However, please note that both paths should not be given simultaneously. Use the following lines to create the stations:
```python
CreateDSSAT.create_wth_station()
CreateDSSAT.create_management()
```

3. Use an external station: If you have already created a station, you can provide it as follows:
```python
CreateDSSAT.wth = weather_created
CreateDSSAT.man = management_created
```

Once the stations are created, you can run the model by calling the `run_DSSAT()` function (remember to always close with the `close_DSSAT()` function) or run the optimization method.

### Optimization

The model optimizes the irrigation based on given dates. To provide the dates, use the following code:
```python
dates = ['12-08-2022', '15-08-2022', '18-08-2022', '20-08-2022']
CreateDSSAT.optimization_irri(dates)
```

The output will be:
```bash
Execution time: 183.74
The optimal values are (0.0, 0.9, 1.5, 17.0)
```

### Testing

You can also try other values and get the cost function by using the following lines. It is important to predefine the dates if the previous code wasn't run.

```python
dates = ['12-08-2022', '15-08-2022', '18-08-2022', '20-08-2022']
CreateDSSAT.next_dates = dates
CreateDSSAT.optimization_irri(dates)
```


## Personalization

These are the default settings, but you can customize them according to your needs. The customizable variables, in addition to the one mentioned earlier, are:

- `soil`: You can provide another soil profile as presented in the DSSAT documentation (object of DSSAT).
- `crop`: You can provide another crop profile as presented in the DSSAT documentation (object of DSSAT).
- `max_val_irrig`: The maximum value of water that can be given to the plants per day (integer).
- `TWAD_weight`: Modify the weight representing the total crop weight in the cost function of the optimization (integer).
- `irr_weight`: Modify the weight representing the irrigation in the cost function of the optimization (integer).

To modify these variables, use the following code in Python:

```python
CreateDSSAT.variable = value
```