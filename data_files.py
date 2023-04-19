import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

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

def create_wth_station(path, elev = 119, lat=49.56635317268511, long =2.4733156772560965):
    # read the file
    df = pd.read_excel(path)
    df['DATE'] = df['dateLocale'].apply(change_date)[:]
    df['SRAD'] =  [8 for i in range(df.shape[0])][:]

    df_wth = df[['DATE', 'SRAD','TEMPERATURE_MAX', 'TEMPERATURE_MIN','RELATIVE_HUMIDITY', 'RAIN_FALL']][:]

    # Creation of the weather data
    wth_data = WeatherData(
            df_wth,
            variables={        
                'TEMPERATURE_MIN': 'TMIN', 'TEMPERATURE_MAX': 'TMAX',
                'RAIN_FALL': 'RAIN', 'SRAD': 'SRAD',
                'RELATIVE_HUMIDITY': 'RHUM', 'DATE':'DATE'}
        )

    # Creation of the weather station
    wth_station = WeatherStation(
        wth_data,
        {'ELEV': elev, 'LAT': lat, 'LON': long}
    )

    return wth_station

def create_management(path):
    '''
    Creation of Management (in potato case)
    cultivar: srt
            Code of the cultivar
    planting_date: datetime
            Planting date.
    harvest: srt
            M: harvest at maturity
    irrigation: srt
            reported on days
    '''

    df = pd.read_excel(path, header=[0,1])

    # Defining planting date
    plant_date = df[('Unnamed: 0_level_0', 'Date/heure')].min()
    plant_date = datetime.strptime(plant_date, '%Y-%m-%d %H:%M:%S')

    man = Management(
        cultivar='IB0001',
        planting_date = plant_date, harvest = 'M',
        irrigation = 'R'
    )
    
    man.planting_details['table']['PLWT'] = 1500
    man.planting_details['table']['SPRL'] = 2

    # Create a irrigation schedule as a pandas.DataFrame
    schedule = pd.DataFrame({ 'date' : pd.to_datetime(df[('Unnamed: 0_level_0', 'Date/heure')]),
                             'IRVAL': df[('Précipitations [mm]','Somme')]})
    schedule['IDATE'] = schedule.date.dt.strftime('%y%j')
    schedule['IROP'] = 'IR001' # Code to define the irrigation operation

    man.irrigation['table'] = TabularSubsection(schedule[['IDATE', 'IROP', 'IRVAL']])   


    return man

def CDE_getDict(CDE_path = 'DATA.CDE'):
    with open(CDE_path, 'r') as file:
        sumOutCDE = file.readlines()

    sumOutCDEArr = [line.strip().split('\t') for line in sumOutCDE]
        
    sumOutCDEDic ={}

    idx_des = 23
    for line_0 in sumOutCDEArr:
        line = line_0[0]
        if len(line) != 0:
            if line[0] == '@':
                idx_des = line.find("DESCRIPTION") 
            if not line[0] in ['', '*', '@', ' ', '!']:
                CDE = line[0:7].replace(" ", "")
                description = line[idx_des:]
                sumOutCDEDic[CDE] = description

    return sumOutCDEDic

if __name__ == '__main__':
    # import DSSATTools
    # print(DSSATTools.__file__)
    ## C:\Users\Melanie Pacheco\AppData\Local\Programs\Python\Python38\lib\site-packages\DSSATTools

    dic_var = CDE_getDict('C:\DSSAT48\DETAIL.CDE')
    print(dic_var['SWC'])
    



    # Soil instance from default soil profile
    # soil = SoilProfile(default_class='SIC')

    # # Crop
    # crop = Crop('Potato')

    # wth = create_wth_station('Data\Weather\Essai irrigation.xlsx')
    # # wth_station.write('Files')

    # man = create_management('Data\Probes\Sonde Robot 2.xlsx')
    # # management.write('Files')

    # dssat = DSSAT()

    # dssat.OUTPUT_LIST = ['PlantGro',]

    # dssat.setup("C:\\Users\\MELANI~1\\AppData\\Local\\Temp\\Expe")
    # dssat.run(
    #     soil=soil, weather=wth, crop=crop, management=man,
    # )

    # print('-------------------------------------')

    # result_df = dssat.output['PlantGro']


    # # fig = result_df.plot(x='DAP', y=result_df.columns[4:], title='Plant grow')
    # # fig.show()

    # # fig2 = result_df.plot(x='DAP', y='LAID', title='LAID')
    # # fig2.show()

    # print(result_df.columns)



