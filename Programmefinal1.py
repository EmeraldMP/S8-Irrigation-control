from DSSATTools import (
    Crop,SoilProfile, WeatherData, WeatherStation,
    Management, DSSAT
)
from DSSATTools.base.sections import TabularSubsection
from datetime import datetime, timedelta
import pandas as pd

from tradssat import CULFile, ECOFile
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import numpy as np
import os
import DSSATTools
print(DSSATTools.__file__)

DATES = pd.date_range('2022-04-01', '2022-09-15')
crop = Crop('Potato')

def change_date(x):
    y = datetime.fromisoformat(str(x)) #Format date de Python
    return y

def dssat_date(x): #Les dates DSSAT ont un format particulier : 22123 pour le 123em de l'année 2022.
    x = str(x)
    y = int(datetime(int(x[0:4]),int( x[5:7]), int(x[8:10])).strftime('%y%j'))
    return y

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

def reset_coeff(): #pour prendre en compte les coefficients de base
    global coeffs
    """
    Entrée:
        -Numéro de la variété
    Sortie:
        -Nouveaux fichiers génétiques avec les variétés de base
    """
    variables = ['G2','G3','PD','P2','TC','RUE1','RUE2']
    for i in range(len(variables)) :
        crop.set_parameter(variables[i],coeffs['IB0001'][i],'IB0001')


def results(irrig ,Wth,plant_date = DATES[0],Param = 'LAID'):
    df = pd.read_excel(Wth) #Mise en place du fichier d'irrigation
    df['DATE'] = df['date'].apply(change_date)[:]
    df['SRAD'] =  [8 for i in range(df.shape[0])][:]
    df_wth = df[['DATE', 'SRAD','TEMPERATURE_MAX', 'TEMPERATURE_MIN','RELATIVE_HUMIDITY', 'RAIN_FALL']][:]
    WTH_DATA = WeatherData(
        df_wth,
        variables={
            'TEMPERATURE_MIN': 'TMIN', 'TEMPERATURE_MAX': 'TMAX',
            'RAIN_FALL': 'RAIN', 'SRAD': 'SRAD',
            'RELATIVE_HUMIDITY': 'RHUM'
        }
    )
    wth_station = WeatherStation(
        WTH_DATA,
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}#Création du 
    )#Création de la station d'irrigation

    man = Management(
        cultivar='IB0001',
        planting_date = plant_date, harvest = 'M'
    )#Création du fichier de management
    man.planting_details['table']['PLWT'] = 1500#A préciser obligatoirement quand on choisit la pomme de terre de culture
    man.planting_details['table']['SPRL'] = 2#A préciser obligatoirement quand on choisit la pomme de terre de culture
    man.simulation_controls['IRRIG'] = 'R' #R pour irrigation suivant les dates données (Il y d'autres possibilités voir la doc)
    
    man.irrigation['table'] = TabularSubsection(irrig)#Prise en compte du fichier d'irrigation
    soil = SoilProfile(default_class='SIL')#Prise en compte du sol, il y a d'autres sol définis mais j'ai l'impression qu'il y a un problème pour les autres sols... Il faudrait vérifier
    dssat = DSSAT() #Ouverture de DSSAT
    #dssat.setup('C:\\Users\\v-i-n\\AppData\\Local\\Temp\\Expe')#Ecriture de tous les fichiers qu'on a fait auparavant dans le dossier spécifié en argument 
    dssat.setup("C:\\Users\\MELANI~1\\AppData\\Local\\Temp\\Expe")
    dssat.run(soil=soil, weather=wth_station, crop=crop, management=man) #On fait tourner le logiciel
    a = dssat.output['PlantGro'][:] 
    print(type(a))
    #dssat.close() #On referme l'instance (cela supprime le fichier créé ). S'il y a une erreur sur cette ligne c'est qu'il y a un problème dans la fonction du module il faut changer la fonction close par celle qui est tout en bas de ce fichier
    return a[Param] #On retourne le paramètre qui nous intéresse

def results2(Wth = '/DSSAT47/Meteo.xlsx',plant_date = DATES[0],Param = 'LAID', soil_class='SIL'):
    """Même script que results mais en prenant l'irrigation automatique : ça renvoi le calendrier di'rrigation de dssat"""
    df = pd.read_excel(Wth)
    df['DATE'] = df['date'].apply(change_date)[:]
    df['SRAD'] =  [8 for i in range(df.shape[0])][:]
    df_wth = df[['DATE', 'SRAD','TEMPERATURE_MAX', 'TEMPERATURE_MIN','RELATIVE_HUMIDITY', 'RAIN_FALL']][:]
    WTH_DATA = WeatherData(
        df_wth,
        variables={
            'TEMPERATURE_MIN': 'TMIN', 'TEMPERATURE_MAX': 'TMAX',
            'RAIN_FALL': 'RAIN', 'SRAD': 'SRAD',
            'RELATIVE_HUMIDITY': 'RHUM'
        }
    )
    wth_station = WeatherStation(
        WTH_DATA,
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    man = Management(
        cultivar='IB0001',
        planting_date = plant_date,harvest = 'M'
    )
    man.planting_details['table']['PLWT'] = 1500
    man.planting_details['table']['SPRL'] = 2
    man.simulation_controls['IRRIG'] = 'A'  #Irrigation automatique ce qui diffère au programme result
    
    soil = SoilProfile(default_class=soil_class) #estaba en sil
    # print(soil.__repr__())
    dssat = DSSAT()
    dssat.setup("C:\\Users\\MELANI~1\\AppData\\Local\\Temp\\Expe")  #Ecriture du dossier dans le chemin qui est indiqué
    # dssat.setup()
    dssat.run(soil=soil, weather=wth_station, crop=crop, management=man)
    file = open('C:\\Users\\MELANI~1\\AppData\\Local\\Temp\\Expe\\SoilWat.OUT', "r") #Extraction de l'irrigation automatique dans le document SoilWat.OUT
    # file = open('SoilWat.OUT', "r")
    lines=[]
    dates = []
    values = []
    for line in file:
        lines.append(line)
    file.close()
    print(lines)
    for i in range(14,len(lines)):
        values.append(float(lines[i].split()[9]))
        dates.append(int(lines[i].split()[0][2:4]+lines[i].split()[1]))
    #dssat.close()
    result_df = pd.DataFrame( {'Date' : dates, 'Eau': values})
    return result_df
# print(results2())

def afficher(Data = '/DSSAT47/LAI Ex.xlsx',Wth = '/DSSAT47/Meteo.xlsx'):
    """Fonction pour voir un peu l'effet de l'irrigation sur rendement"""
    df_data = pd.read_excel(Data)
    df_data['IDATES'] = df_data['Date'].apply(dssat_date)[:]
    # print(df_data['IDATES'])
    df_data['IRVAL'] = df_data['Irval '][:]
    df_data['IROP'] =  ['IR001' for i in range(df_data.shape[0])][:]
    
    irrig = df_data[['IDATES','IROP','IRVAL']][0:5]
    
    df = results(irrig ,Wth,plant_date = DATES[0],Param = 'TWAD')
    df =df.astype(float)[:]

    irrig1 = df_data[['IDATES','IROP','IRVAL']][0:5][:]
    irrig1['IRVAL'] = [1,200,10,100,200] #changement de l'irrigation
    df1 = results(irrig1 ,Wth,plant_date = DATES[0],Param = 'TWAD')
    #On affiche les deux courbes
    df.plot()
    df1.plot()

    plt.show()
# afficher()


def trouver_bon(next_date,irrig,Wth):
    """Fonction qui trouve la dose d'eau à mettre après avoir fixé les coefficients"""
    TWAD_max = []
    IRV = []
    reset_coeff()
    for i in range(0,30,3):
        irrig1 =  pd.concat([irrig,pd.DataFrame({'IDATES' : [dssat_date(next_date)],  'IROP' : ['IR001'],'IRVAL' : [i]})]) #On modifie le calendrier d'irrigation pour ajouter une date avec la valeur i qu'on souhaite d'irrigation
        df = results(irrig1 ,Wth,plant_date = DATES[0],Param = 'TWAD') # Le poids des turbercules en fonction du temps
        df =df.astype(float)[:]
        IRV.append(i)
        TWAD_max.append(df.max()) #On ajoute le TWAD max dans la liste avec i

    plt.plot(IRV,TWAD_max)

    plt.show()
    for i in range(len(TWAD_max)-1): #Test pour savoir quelle dose on selectionne (1.001 arbitraire)
        if TWAD_max[i+1]<1.001*TWAD_max[i]:

            return IRV[i]     
    return IRV[TWAD_max.index(max(TWAD_max))]

def trouve_IRVAL2(Wth ='Meteo.xlsx' ):
    """Cette fonction retourne l'irrigation automatique pour les coefficients à leurs max et min our voir s'il y a une différence. 
    (On trouve les valeurs limites des coefficients dans les fichiers .CUL et .ECO dans DSSAT48 puis genotype."""
    variables = ['G2','G3','PD','P2','TC','RUE1','RUE2']
    min = [900,21,0.5,0.3,15,3.5,4]
    max = [2100,26,1,0.9,22,4,4.5]
    for i in range(len(variables)): 
        crop.set_parameter(variables[i],min[i],'IB0001')

    # print(results2(Wth = Wth,plant_date = DATES[0],Param = 'TWAD' ))

    for i in range(len(variables)): 
        crop.set_parameter(variables[i],max[i],'IB0001')

    # print(results2(Wth = Wth,plant_date = DATES[0],Param = 'TWAD' ))
# trouve_IRVAL2()


def fitting_function(params,plant_date,irrig,Wth, data,dates,variables):
    for i in range(len(variables)): #avant de réaliser la simulation on change les paramètres donnés par la fonction minimize
        crop.set_parameter(variables[i],params[i],'IB0001')
    DATES = [date[0] for date in dates.values]

    model_prediction = results(irrig,Wth,plant_date,Param ='LAID')[DATES].to_numpy()
    # print(np.sqrt(sum(abs((model_prediction - data)**2))))
    return np.sqrt(sum(abs((model_prediction - data)**2)))  #Fonction qui renvoi l'évaluation du critère des moindres carrés


def set_genetic_coeffs(initial_params,plant_date,irrig,Wth,data,dates, variables):
    """
    Fonction qui calcule les nouveaux coefficients génétiques par la méthode des moindres carrés à la place des anciens que l'on prend en paramètres initiaux 
    """
    fitted = minimize(fitting_function, initial_params, 
                      args=(plant_date, irrig, Wth, data,dates, variables), 
                      method = 'Nelder-Mead', options={'maxiter' : 10}, 
                      bounds = [(3.5,4),(0.5,1),(0.3,0.9)] )
    # print(fitted)
    for i in range(len(variables)): #On fixe les paramètres
        crop.set_parameter(variables[i],fitted.x[i],'IB0001')



def irrigation(Data = 'LAI Ex.xlsx',Wth = 'Meteo.xlsx', next_date= "2022-05-08",New_LAI = [1.5,2,2,2],variables =['RUE1','PD','P2'] ):
    """Programme qui compile toutes les fonctions: sépration par coordonnées des données puis on trouve les nouveaux coefficients, on trouve la dose d'eau puis on réécrit le fichier actualisé."""
    df_data = pd.read_excel(Data)
    df_data['IDATES'] = df_data['Date'].apply(dssat_date)[:]
    df_data['IRVAL'] = df_data['Irval '][:]
    df_data['IROP'] =  ['IR001' for i in range(df_data.shape[0])][:]
    New_doc = pd.DataFrame({df_data.columns.values[0] : [],df_data.columns.values[1] : [],df_data.columns.values[2] : [],df_data.columns.values[3] : [],df_data.columns.values[4] : []})
    # coords = set( df_data['GPS'].to_list())
    coords = np.unique(df_data['GPS'])
    print(coords.shape)
    i = 0
    # print(df_data)
    # print(coords)

    for coord in coords :         
        initial_params = [3.5,0.8,0.6]
        df_data_crop = df_data.loc[df_data['GPS'] == coord ][:]
        irrig = df_data_crop[['IDATES','IROP','IRVAL']]
        datas = np.append(df_data_crop['LAI'].to_numpy(), New_LAI[i])
        # dates = df_data_crop['Date']
        # dates = dates.astype(str)
        # dates = np.append(dates.to_numpy(), next_date)
        # dates = pd.to_datetime(dates)
        # dates= dates.to_frame(index = False)[:]
        # dates.columns = ["Date"]
        dates = pd.DataFrame.from_dict({"Date": df_data_crop['Date']})
        dates = dates.append({"Date": pd.to_datetime("2022-05-08")}, ignore_index=True)
        
        set_genetic_coeffs(initial_params, DATES[0], irrig,Wth, datas,dates, variables)
        IR = trouver_bon(next_date,irrig,Wth)
        new_df_data_crop = pd.concat([df_data_crop[:],pd.DataFrame({df_data.columns.values[0] : [coord],df_data.columns.values[1] : [New_LAI[i]],df_data.columns.values[2] : [change_date(next_date)],df_data.columns.values[3] : [IR]})])
        New_doc = pd.concat([New_doc,new_df_data_crop[:]])
        i =+1

    return New_doc
print(irrigation())


def afficher(Data = '/DSSAT47/LAI Ex.xlsx',Wth = '/DSSAT47/Meteo.xlsx'):
    df_data = pd.read_excel(Data)
    df_data['IDATES'] = df_data['Date'].apply(dssat_date)[:]
    df_data['IRVAL'] = df_data['Irval '][:]
    df_data['IROP'] =  ['IR001' for i in range(df_data.shape[0])][:]
    
    irrig = df_data[['IDATES','IROP','IRVAL']][0:5]
    
    #crop.set_parameter('RUE2',4,'IB0001')
    df = results(irrig ,Wth,plant_date = DATES[0],Param = 'LAID')
    df =df.astype(float)[:]
    #crop.set_parameter('RUE2',3.5,'IB0001')
    irrig1 = df_data[['IDATES','IROP','IRVAL']][0:5][:]
    # print(irrig1)
    irrig1['IDATES'] =[22110,22112,22115,22119,22125]
    irrig1['IRVAL'] = [10,10,10,10,10]
    df1 = results(irrig1 ,Wth,plant_date = DATES[0],Param = 'LAID')
    # print(df[['2022-04-20','2022-04-22','2022-04-25','2022-04-29','2022-05-05',]])
    df.plot()
    df1.plot()

    plt.show()
#afficher()


def afficher_twad_max(Data = '/DSSAT47/LAI Ex.xlsx',Wth = '/DSSAT47/Meteo.xlsx'):
    """Afficher twad max en fonction de l'eau apportée en un jour fixé"""
    df_data = pd.read_excel(Data)
    reset_coeff()
    df_data['IDATES'] = df_data['Date'].apply(dssat_date)[:]
    df_data['IRVAL'] = df_data['Irval '][:]
    df_data['IROP'] =  ['IR001' for i in range(df_data.shape[0])][:]
    L = []
    IR = []
    irrig = df_data[['IDATES','IROP','IRVAL']][0:5]
    irrig['IDATES'] =[22110,22112,22115,22119,22125]

    
    for i in range(0,100,10):
        irrig['IRVAL'] = [10,15,10,10,i]
        df = results(irrig ,Wth,plant_date = DATES[0],Param = 'TWAD')
        df =df.astype(float)[:]
        IR.append(i)
        L.append(df.max())

    plt.plot(IR,L)

    plt.show()

# afficher_twad_max()

"""
    def close(self):
        def removeReadOnly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        '''
        Removes the simulation environment (tmp folder and files).
        '''
        shutil.rmtree(self._RUN_PATH, onerror=removeReadOnly)
        sys.stdout.write(f'{self._RUN_PATH} and its content has been removed.\n')
    
"""