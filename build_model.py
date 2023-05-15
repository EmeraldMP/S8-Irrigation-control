import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import nevergrad as ng

pd.options.plotting.backend = "plotly"


from DSSATTools.base.formater import weather_data, weather_data_header, weather_station
from datetime import datetime, timedelta
from DSSATTools import (
    Crop, SoilProfile, WeatherData, WeatherStation, Management, DSSAT)
from DSSATTools.base.sections import TabularSubsection

def change_date(x):
    '''
    Return a valid date format
    '''
    y = datetime.fromisoformat(x)
    return y

class CreateDSSAT:

    def __init__(self):
        self.soil = SoilProfile(default_class='SIC')
        self.crop = Crop('Potato')
        self.wth = None
        self.man = None
        self.dates = pd.date_range('2000-01-01', '2002-12-31')
        self.dssat = None
        self.schedule = None
        self.next_dates = None
        self.max_val_irrig = 60

    def create_wth_station(self, wth_path = None, dates = ('2000-01-01', '2002-12-31'),
                           elev = 119, lat=49.56635317268511, long =2.4733156772560965):
        if wth_path is None:
            # Random weather data
            self.dates = pd.date_range(dates[0], dates[1])
            N = len(self.dates)
            df = pd.DataFrame({
                'tn':   np.random.gamma(10, 1, N),
                'rad':  np.random.gamma(10, 1.5, N),
                'prec': [0.0]* N,
                'rh':   100 * np.random.beta(1.5, 1.15, N),
                },
                index=self.dates,)
            df['TMAX'] = df.tn + np.random.gamma(5., .5, N)

            # Create a WeatherData instance
            WTH_DATA = WeatherData( df,
                                    variables={
                                    'tn': 'TMIN', 'TMAX': 'TMAX',
                                    'prec': 'RAIN', 'rad': 'SRAD',
                                    'rh': 'RHUM'})
            # Create a WheaterStation instance
            self.wth = WeatherStation(
                WTH_DATA, 
                {'ELEV': elev, 'LAT': lat, 'LON': long, 'INSI': 'dpoes'}
            )
            print(f"Wheather station created! Dates: {dates[0]} to {dates[1]}")
        else:
            try:
                df = pd.read_excel(wth_path)
            except:
                print(f'Path "{wth_path}" not recognized')
                return None
            df['DATE'] = df['dateLocale'].apply(change_date)[:]
            df['SRAD'] =  [8 for i in range(df.shape[0])][:]

            df_wth = df[['DATE', 'SRAD','TEMPERATURE_MAX', 'TEMPERATURE_MIN','RELATIVE_HUMIDITY', 'RAIN_FALL']][:]

            # Creation of the weather data
            wth_data = WeatherData(
                    df_wth,
                    variables={        
                        'TEMPERATURE_MIN': 'TMIN', 'TEMPERATURE_MAX': 'TMAX',
                        'RAIN_FALL': 'RAIN', 'SRAD': 'SRAD',
                        'RELATIVE_HUMIDITY': 'RHUM', 'DATE':'DATE'})            
            # Creation of the weather station
            self.wth = WeatherStation(
                wth_data,
                {'ELEV': elev, 'LAT': lat, 'LON': long})
            

    def create_management(self, man_path = None):
        if man_path is None:
            self.man = Management(
            cultivar='IB0001',
            planting_date= self.dates[10],
            )

            schedule = pd.DataFrame([
                (datetime(2000,1,15), 80),
                (datetime(2000,1,30), 60),
                (datetime(2000,2,15), 40),
                (datetime(2000,3,1),  20)
            ], columns = ['date', 'IRVAL'])
            schedule['IDATE'] = schedule.date.dt.strftime('%y%j')
            schedule['IROP'] = 'IR001' # Code to define the irrigation operation
            schedule = schedule[['IDATE', 'IROP', 'IRVAL']]
            self.schedule = schedule

            # Modify harvest to Maturity
            self.man.simulation_controls['HARVS'] = 'M'
            # Set the irrigation schedule
            self.man.irrigation['table'] = TabularSubsection(schedule)
            # Set irrigation control as reported schedule
            self.man.simulation_controls['IRRIG'] = 'R'

            # The definition of this parameters is mandatory for roots
            self.man.planting_details['table']['PLWT'] = 1500
            self.man.planting_details['table']['SPRL'] = 2
            print(f"Managment station created! Planting date: {self.dates[0].strftime('%d-%m-%Y')}")

        else:
            try:
                df = pd.read_excel(man_path, header=[0,1])
            except:
                print(f'Path "{man_path}" not recognized')
                return None

            # Defining planting date
            plant_date = df[('Unnamed: 0_level_0', 'Date/heure')].min()
            plant_date = datetime.strptime(plant_date, '%Y-%m-%d %H:%M:%S')

            self.man = Management(
                cultivar='IB0001',
                planting_date = plant_date, harvest = 'M',
                irrigation = 'R'
            )
            
            self.man.planting_details['table']['PLWT'] = 1500
            self.man.planting_details['table']['SPRL'] = 2

            # Create a irrigation schedule as a pandas.DataFrame
            schedule = pd.DataFrame({ 'date' : pd.to_datetime(df[('Unnamed: 0_level_0', 'Date/heure')]),
                                    'IRVAL': df[('Précipitations [mm]','Somme')]})
            schedule['IDATE'] = schedule.date.dt.strftime('%y%j')
            schedule['IROP'] = 'IR001' # Code to define the irrigation operation
            self.schedule = schedule
            self.man.irrigation['table'] = TabularSubsection(schedule[['IDATE', 'IROP', 'IRVAL']])   

    def run_DSSAT(self):
        if (self.man is None) and (self.wth is None):
            print("Managment and Wheater not defined")
        elif (self.man is None) and (self.wth is not None):
            print("Managment not defined")
        elif (self.man is not None) and (self.wth is None):
            print("Wheater not defined")
        else:
            self.dssat = DSSAT()
            self.dssat.setup()
            self.dssat.run(
                soil=self.soil, weather=self.wth, crop=self.crop, management=self.man,
            )

    def close_DSSAT(self, other_dssat = None):
        if other_dssat is None:
            dssat_to_close = self.dssat
        else:
            dssat_to_close = other_dssat
        
        if dssat_to_close:
            try:
                dssat_to_close.close()

            except:
                # Set the path to the file you want to modify
                file_path = dssat_to_close._RUN_PATH+'\\dscsm048.exe'

                # Build the command to remove the read-only attribute
                command = ['attrib', '-R', file_path]

                # Use the run() method to execute the command
                subprocess.run(command, capture_output=True, text=True)

                dssat_to_close.close()   

    def irri_cost(self, irval=[0,0,0,0]):
        if self.next_dates:
            
            new_schedule = pd.DataFrame({'date': self.next_dates,
                            'IRVAL' : irval})
            new_schedule['IDATE'] = new_schedule.date.dt.strftime('%y%j')
            new_schedule['IROP'] = 'IR001' # Code to define the irrigation operation
            new_schedule = new_schedule[['IDATE', 'IROP', 'IRVAL']]

            total_schedule = pd.concat([self.schedule, new_schedule])

            self.man.irrigation['table'] = TabularSubsection(total_schedule)

            dssat = DSSAT()
            dssat.setup()
            dssat.run(
            soil=self.soil, weather=self.wth, crop=self.crop, management=self.man,
            )

            TWAD = dssat.output['PlantGro']['TWAD'][-1]
            self.close_DSSAT(dssat)

            weight = 8
            return weight*-(1/TWAD+0.001) + (np.sum(irval)/(self.max_val_irrig*len(irval)))**2
        
        else:
            raise('There is not dates to optimize')

    def optimization_irri(self, next_dates):
        self.next_dates = [datetime.strptime(date_string, '%d-%m-%Y') for date_string in next_dates]
        rep = len(self.next_dates)
        print(self.next_dates)

        # Definition of the optimization problem

        # Discrete, ordered
        param = ng.p.TransitionChoice(range(self.max_val_irrig), repetitions=rep)
        optimizer = ng.optimizers.DiscreteOnePlusOne(parametrization=param, budget=100)
        # optimizer = ng.optimizers.DiscreteOnePlusOne(parametrization=param, budget=100, num_workers=1)

        recommendation = optimizer.provide_recommendation()
        for _ in range(optimizer.budget):
            x = optimizer.ask()
            loss = self.irri_cost(x.value)
            optimizer.tell(x, loss)

        recommendation = optimizer.provide_recommendation()
        print(f'The optimal values are {recommendation.value}')

        return recommendation.value
        



if __name__ == '__main__':
    dssat = CreateDSSAT()
    # dssat.create_wth_station('Data\Weather\Essai irrigation.xlsx')
    # dssat.create_management('Data\Probes\Sonde Robot 2.xlsx')
    dssat.create_wth_station()
    dssat.create_management()
    # dssat.run_DSSAT()
    dates = ['15-1-2000', '28-1-2000', '25-2-2000', '24-2-2000']
    dssat.optimization_irri(dates)
    # dssat.close_DSSAT()
