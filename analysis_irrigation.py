import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import DSSATTools


from datetime import datetime, timedelta
from DSSATTools import (
    Crop, SoilProfile, WeatherData, WeatherStation, Management, DSSAT
)
from DSSATTools.base.sections import TabularSubsection
from tradssat import CULFile, ECOFile
from scipy.optimize import minimize


coeffs = {
    'IB0001':[2000,22.5,0.8,0.6,17,3.5,4],
    'IB0002':[1100,22.5,0.9,0.0,19,3.5,4],
    'IB0003':[1100,26.0,0.9,0.2,17,3.5,4],
    'IB0004':[2000,25.0,0.5,0.7,20,3.5,4],
    'IB0005':[1000,30.0,0.8,0.1,21,3.5,4],
    'CI0001':[1100,25.0,0.2,0.8,21,3.5,4],
    'CI0002':[1100,25.0,0.2,0.8,21,3.5,4],
    'AR0003':[1100,26.0,0.9,0.2,21,3.5,4],
    'DM0004':[1500,24.0,0.6,0.4,18,3.5,4],
    'IB0006':[2000,25.0,0.8,0.4,17,3.5,4],
    'IB0007':[2000,22.5,1.0,0.6,17,3.5,4],
    'IB0008':[2000,25.0,0.9,0.6,16,3.5,4],
    'IB0009':[2000,25.0,0.9,0.8,17,3.5,4],
    'IB0010':[2000,25.0,0.9,0.4,21,3.5,4],
    'IB0011':[2000,25.0,1.0,0.4,17,3.5,4],
    'IB0012':[2000,25.0,0.7,0.6,19,3.5,4],
    'IB0018':[1000,27.0,0.2,0.1,20,3.5,4],
    'UF0001':[2000,22.0,0.7,0.4,19,3.5,4],
     }

def change_date(x):
    '''
    Return a valid date format
    '''
    y = datetime.fromisoformat(str(x)) 
    return y

def dssat_date(x): #Les dates DSSAT ont un format particulier : 22123 pour le 123em de l'année 2022.
    '''
    Return dates in DSSAT format
        Ex: 22123 for the 123th day of the year 2022.
    '''
    x = str(x)
    y = int(datetime(int(x[0:4]),int( x[5:7]), int(x[8:10])).strftime('%y%j'))
    return y

class IrrigationAnalysis:
    '''
    Initialize the irrigation analysis

    Arguments
    ----------
    dates: tuple
        Optional. Range of dates in format AAAA-MM-DD
    crop_type: str
        Optional. Type of crop to analyse
    '''

    def __init__(self, dates = ('2022-04-01', '2022-09-15'), crop_type='Potato', soil_class = 'SIL'):
        self.dates = pd.date_range(dates[0], dates[1])
        self.crop = Crop(crop_type)
        self.data_path = 'LAI Ex.xlsx'
        self.wth_path = 'Meteo.xlsx'
        self.soil = soil_class

    def reset_coeff(self): #pour prendre en compte les coefficients de base
        """
        Input:
            - Number of the variety
        Output:
            - New genetic files with basic varieties
        """
        variables = ['G2','G3','PD','P2','TC','RUE1','RUE2']
        for i in range(len(variables)) :
            self.crop.set_parameter(variables[i],coeffs['IB0001'][i],'IB0001')
    
    def results(self, irrig = None , Param = 'LAID', type_ir = 'R'):
        '''
        Inputs:

        Output
        '''
        if type_ir == 'R':
            if irrig is None:
                raise NameError('There is no irrigation given')

        df = pd.read_excel(self.wth_path)
        df['DATE'] = df['date'].apply(change_date)[:]
        df['SRAD'] =  [8 for i in range(df.shape[0])][:]
        df_wth = df[['DATE', 'SRAD','TEMPERATURE_MAX', 'TEMPERATURE_MIN','RELATIVE_HUMIDITY', 'RAIN_FALL']][:]
        
        # Creation of the weather data
        wth_data = WeatherData(
            df_wth,
            variables={
                'TEMPERATURE_MIN': 'TMIN', 'TEMPERATURE_MAX': 'TMAX',
                'RAIN_FALL': 'RAIN', 'SRAD': 'SRAD',
                'RELATIVE_HUMIDITY': 'RHUM'}
        )

        # Creation of the weather station
        wth_station = WeatherStation(
            wth_data,
            {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
        )

        # Creation of Management (in potato case)
        man = Management(
            cultivar='IB0001',
            planting_date = self.dates[0], harvest = 'M'
        )
        man.planting_details['table']['PLWT'] = 1500
        man.planting_details['table']['SPRL'] = 2
        man.simulation_controls['IRRIG'] = type_ir
        
        # Give the irrigation dataframe
        if type_ir == 'R':
            man.irrigation['table'] = TabularSubsection(irrig)
        
        # Creation of the soil profile
        soil = SoilProfile(default_class=self.soil)
        dssat = DSSAT()
        dssat.OUTPUT_LIST = ['PlantGro', 'SoilWat']

        dssat.setup("C:\\Users\\MELANI~1\\AppData\\Local\\Temp\\Expe")
        # dssat.setup(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'Expe'))
        dssat.run(soil=soil, weather=wth_station, crop=self.crop, management=man)
        
        if type_ir == 'R':
            result_df = dssat.output['PlantGro'][:][Param] 

        if type_ir == 'A':
            result_df = pd.Series( 
                index = list(dssat.output['SoilWat'].apply(lambda x: str(x['@YEAR'])[2:4]+str(x['DOY']), axis=1)),
                data = list(dssat.output['SoilWat']['IRRC']))

        #dssat.close() #On referme l'instance (cela supprime le fichier créé ). S'il y a une erreur sur cette ligne c'est qu'il y a un problème dans la fonction du module il faut changer la fonction close par celle qui est tout en bas de ce fichier
        return result_df
    
    def afficher(self, irchange = None, show_graph=True):
        '''
        Function to see the effect of irrigation on the Total plant weight (kg dm/ia)
        '''
        df_data = pd.read_excel(self.data_path)
        df_data.rename(columns={'Irval ': 'IRVAL'}, inplace=True)

        df_data['IDATES'] = df_data['Date'].apply(dssat_date)
        df_data['IROP'] =  ['IR001' for i in range(df_data.shape[0])]
        
        irrig = df_data[['IDATES','IROP','IRVAL']][0:5]

        # Verification of given irrigation list
        if irchange == None:
            irchange = [8 for i in range(irrig.shape[0])]
        if len(irchange) != irrig.shape[0]:
            raise NameError(f'Irrigation list has {len(irchange)} elements, expected {irrig.shape[0]}')
        
        # Caultation of results of TWAD with existing irrigation
        df = self.results(irrig , Param ='TWAD')

        # Calcutation of results of TWAD with given irrigation
        irrig1 = df_data[['IDATES','IROP']][0:5][:]
        irrig1['IRVAL'] = irchange 
        df1 = self.results(irrig1, Param = 'TWAD')

        if show_graph:
            # Plot  of the difference
            df.plot(label='Old Irrigation')
            df1.plot(label='New Irrigation')
            plt.title("TWAD comparison between irrigations")
            plt.ylabel("Total plant weight (kg dm/ia)")
            plt.xlabel("Dates")
            plt.legend()
            plt.show()

        # Create Dataframe with results
        df_twad = pd.DataFrame({'Dates': list(df1.keys()), 
                                 'TWAD': list(df),
                                 'NEW_TWAD': list(df1)
                                 })
        return df_twad
    
    def irrig_opti(self, next_date, irrig, show_graph=False):
        '''
        Function that gives the optimal amount of irrigation for the next day
        '''
        TWAD_max = []
        IRV = []
        self.reset_coeff()

        # Try diferents irrigation to find the optimal irragtion
        for i in range(0,30,3):
            irrig_new =  pd.concat([irrig, pd.DataFrame({'IDATES' : [dssat_date(next_date)],  'IROP' : ['IR001'],'IRVAL' : [i]})]) 
            df = self.results(irrig_new , Param = 'TWAD') 
            # df =df.astype(float)[:]
            IRV.append(i)
            TWAD_max.append(df.max())
        
        irrig_max = IRV[TWAD_max.index(max(TWAD_max))]
        i_max = TWAD_max.index(max(TWAD_max))
        # Treshold
        for i in range(len(TWAD_max)-1): 
            if TWAD_max[i+1] < 1.001 * TWAD_max[i]:
                irrig_max = IRV[i]  
                i_max = i    
        # Plot the curve graph
        if show_graph:
            plt.plot(IRV,TWAD_max, label='TWAD')
            plt.plot(IRV, [TWAD_max[i_max] for i in range(len(IRV))], color='red', linestyle='--',label='Theshold')
            plt.scatter(IRV[i], TWAD_max[i], label=f'Interest point: {IRV[i], TWAD_max[i]}',  marker='o', zorder=3)
            plt.title(f"TWAD in fuction of irrigation for day {next_date}")
            plt.ylabel("Total plant weight (kg dm/ia)")
            plt.xlabel("Irrigation")
            plt.legend()
            # plt.annotate(f'({IRV[i], TWAD_max[i]})', IRV[i], TWAD_max[i], textcoords="offset points", xytext=(0,10), ha='center', fontsize=10)
            plt.show() 

        return irrig_max
    
    def irrigation(self, next_date= "2022-05-08", New_LAI = [1.5,2,2,2], variables =['RUE1','PD','P2'], show_graph=False):
        """Programme qui compile toutes les fonctions: 
        sépration par coordonnées des données puis on 
        trouve les nouveaux coefficients, on trouve la dose d'eau puis 
        on réécrit le fichier actualisé."""
        # Read data
        df_data = pd.read_excel(self.data_path)
        df_data.rename(columns={'Irval ': 'IRVAL'}, inplace=True)
        df_data['IDATES'] = df_data['Date'].apply(dssat_date)
        df_data['IROP'] =  ['IR001' for i in range(df_data.shape[0])]

        New_doc = pd.DataFrame({df_data.columns.values[0] : [],df_data.columns.values[1] : [],df_data.columns.values[2] : [],df_data.columns.values[3] : [],df_data.columns.values[4] : []})
        
        coords = np.unique(df_data['GPS'])

        for i in range(coords.shape[0]):
            initial_params = [3.5, 0.8, 0.6]
            df_data_crop = df_data.loc[df_data['GPS'] == coords[i]][:]
            irrig = df_data_crop[['IDATES','IROP','IRVAL']]
            datas = np.append(df_data_crop['LAI'].to_numpy(), New_LAI[i])
            dates = pd.DataFrame.from_dict({"Date": df_data_crop['Date']})
            dates = dates.append({"Date": pd.to_datetime("2022-05-08")}, ignore_index=True)
            
            self.set_genetic_coeffs(initial_params, irrig, datas, dates, variables)
            IR = self.irrig_opti(next_date, irrig, show_graph=show_graph)
            new_df_data_crop = pd.concat([df_data_crop[:],pd.DataFrame({df_data.columns.values[0] : [coords[i]],df_data.columns.values[1] : [New_LAI[i]],df_data.columns.values[2] : [change_date(next_date)],df_data.columns.values[3] : [IR]})])
            New_doc = pd.concat([New_doc,new_df_data_crop[:]])

        return New_doc
    
    def set_genetic_coeffs(self, initial_params, irrig, data, dates, variables):
        """
        Function that calculates new genetic coefficients using the least squares 
        method instead of the old ones, which are taken as initial parameters 
        """
        fitted = minimize(self.fitting_function, initial_params , 
                          args=(irrig, data, dates, variables), 
                          method = 'Nelder-Mead', options={'maxiter' : 10}, 
                          bounds = [(3.5,4),(0.5,1),(0.3,0.9)])

        for i in range(len(variables)): #On fixe les paramètres
            self.crop.set_parameter(variables[i], fitted.x[i], 'IB0001')
    
    def fitting_function(self, params, irrig, data, dates, variables):
        '''
        Returns the evaluation with minimun squared
        '''
        # Change parametes
        for i in range(len(variables)): 
            self.crop.set_parameter(variables[i], params[i], 'IB0001')
        DATES = [date[0] for date in dates.values]

        model_prediction = self.results(irrig, Param ='LAID')[DATES].to_numpy()

        return np.sqrt(sum(abs((model_prediction - data)**2))) 


    
if __name__=='__main__':
    irri = IrrigationAnalysis()
    # print(irri.afficher(irchange=[300,40,5,70,8], show_graph=True)) 
    print( irri.results(type_ir='A'))
    # print(irri.irrigation(show_graph=True))