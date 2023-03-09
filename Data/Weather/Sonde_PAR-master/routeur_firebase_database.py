import time
import setproctitle
import sys
from time import strftime
from firebase import firebase
from w1thermsensor import W1ThermSensor
from csv import writer
from os import path
from pathlib import Path
from shutil import copyfile

setproctitle.setproctitle('database')
start_process = time.time()

firebase = firebase.FirebaseApplication("https://test-routeur-osiris-default-rtdb.europe-west1.firebasedatabase.app/", None)
sensor = W1ThermSensor()

while True:
    mois = strftime("%m")
    jour = strftime("%d")
    if(not(path.exists("/home/pi/routeur_RUT950/Log/"+mois+"_"+jour))):
        print("Nouveau fichier")
        Path("/home/pi/routeur_RUT950/Log/"+mois+"_"+jour).mkdir(parents=True, exist_ok=True)
        copyfile("/home/pi/routeur_RUT950/Log/log_database.csv","/home/pi/routeur_RUT950/Log/"+mois+"_"+jour+"/log_database.csv")
        copyfile("/home/pi/routeur_RUT950/Log/log_storage.csv","/home/pi/routeur_RUT950/Log/"+mois+"_"+jour+"/log_storage.csv")

    date = strftime("%Y/%m/%d, %H:%M:%S")
    temp = sensor.get_temperature()
    
    data = {
        'Date':date,
        'Temperature':temp
    }

    result = firebase.post('/test-routeur-osiris-default-rtdb/Temperature', data)
    print(result)
    
    with open('/home/pi/routeur_RUT950/Log/'+mois+'_'+jour+'/log_database.csv', 'a+', newline='') as write_obj:
                    csv_writer = writer(write_obj)
                    row_contents = [date,temp,result]
                    csv_writer.writerow(row_contents)
                    
    #time.sleep(0.5)
    if (time.time() - start_process) > 300:
        sys.exit()
    