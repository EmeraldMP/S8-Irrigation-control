import numpy as np
import pandas as pd
import control as ct
import control.optimal as opt
import matplotlib.pyplot as plt
from scipy import optimize
import nevergrad as ng

# from analysis_irrigation import IrrigationAnalysis

# Trying out from the beggining.
from DSSATTools import (
    Crop, SoilProfile, WeatherData, WeatherStation,
    Management, DSSAT, TabularSubsection
)
from datetime import datetime, timedelta

# Random weather data
DATES = pd.date_range('2000-01-01', '2000-02-28')
N = len(DATES)
df = pd.DataFrame(
    {
    'tn':   np.random.gamma(10, 1, N),
    'rad':  np.random.gamma(10, 1.5, N),
    'prec': [0.0]* N,
    'rh':   100 * np.random.beta(1.5, 1.15, N),
    },
    index=DATES,
)
df['TMAX'] = df.tn + np.random.gamma(5., .5, N)

# Create a WeatherData instance
WTH_DATA = WeatherData(
                        df,
                        variables={
                        'tn': 'TMIN', 'TMAX': 'TMAX',
                        'prec': 'RAIN', 'rad': 'SRAD',
                        'rh': 'RHUM'
                    }
)
# Create a WheaterStation instance
wth = WeatherStation(
    WTH_DATA, 
    {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
)

# Soil instance from default soil profile
soil = SoilProfile(default_class='SIC')
# Crop
crop = Crop('potato')
# Check how the cultivar looks like
crop.cultivar['IB0001']

# Management instance
man = Management(
    cultivar='IB0001',
    planting_date=DATES[10],
)
# Modify harvest to Maturity
man.simulation_controls['HARVS'] = 'M'
# Set irrigation control as reported schedule
man.simulation_controls['IRRIG'] = 'R'

# The definition of this parameters is mandatory for roots (???)
man.planting_details['table']['PLWT'] = 1500
man.planting_details['table']['SPRL'] = 2

def optimization_irri(irval=[0,0,0,0]):

    max_val_irrig = 60
    TWAD_harvest  = 6000   # Value that we aim on the harvesting day
    weight = 8             # weighting on the loss term

    # Creating irrigation schedule
    schedule = pd.DataFrame([
        (datetime(2000,1,15), 0),
        (datetime(2000,1,28), 0),
        (datetime(2000,2,15), 0),
        (datetime(2000,2,24), 0)
    ], columns = ['date', 'IRVAL'])
    schedule['IDATE'] = schedule.date.dt.strftime('%y%j')
    schedule['IROP'] = 'IR001' # Code to define the irrigation operation
    schedule = schedule[['IDATE', 'IROP', 'IRVAL']]

    schedule['IRVAL'] = irval
    man.irrigation['table'] = TabularSubsection(schedule)

    # DSSAT Run
    dssat = DSSAT()
    dssat.setup()
    dssat.run(
    soil=soil, weather=wth, crop=crop, management=man,
    )

    # This output is an array with the values of TWAD
    # dssat.output['PlantGro']['TWAD'][:].to_numpy() 

    # The chosen output is the final value of TWAD encountered
    # TWAD_all = dssat.output['PlantGro']['TWAD'][:]
    TWAD = dssat.output['PlantGro']['TWAD'][-1]
    # possible objective: (TWAD_harvest - TWAD)**2
    # sum_objective = np.sum(dssat.output['PlantGro']['TWAD'][:].to_numpy())
    # np.sum(((TWAD_harvest - TWAD_all)/TWAD_harvest)**2) not a good loss because doesn't maximize final output

    return weight*((TWAD_harvest - TWAD)/TWAD_harvest)**2 + (np.sum(irval)/(max_val_irrig*len(irval)))**2








