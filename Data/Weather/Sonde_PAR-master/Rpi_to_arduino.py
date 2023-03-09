import serial
import time
import datetime
import csv
import os.path
import numpy as np	
import os
import json
import setproctitle
from csv import writer
from time import strftime
from os import path
from pathlib import Path
from shutil import copyfile

setproctitle.setproctitle('par_sensor')
start_process = time.time()

s = serial.Serial('/dev/ttyUSB0', 9600) # change name, if needed
print("Init, wait 5 s")
time.sleep(5) # the Arduino is reset after enabling the serial connection
s.flush()
PATH = "/home/pi/Data_collect/FB/Log/"

try:
    last_time = datetime.datetime.today()
    first_loop = 0
    
    while True:
        mois = strftime("%m")
        jour = strftime("%d")
        if(not(path.exists(PATH+mois+"_"+jour))):
            print("Nouveau fichier")
            Path(PATH+mois+"_"+jour).mkdir(parents=True, exist_ok=True)
            copyfile(PATH+"log_par.csv",PATH+mois+"_"+jour+"/log_par.csv")        
        
        time_d = last_time-datetime.datetime.today()
        if(((time_d.total_seconds()/60)>5)or first_loop==0):
            print("Ask for data")
            s.write("1".encode())
            s.flush()
            time.sleep(1)
            
            response = s.readline().decode('utf-8').rstrip()
            print(response)
            list_response = response.split(";")
            print(list_response)
            print(len(list_response))
            
            if (len(list_response) == 10) :
                with open(PATH+mois+'_'+jour+'/log_par.csv', 'a+', newline='') as write_obj:
                    csv_writer = writer(write_obj)
                    row_contents = [strftime("%d/%m/%y at %I:%M%p")]+list_response
                    csv_writer.writerow(row_contents)
                last_time = datetime.datetime.today()
                first_loop = 1
        time.sleep(1)
        
        
        if (time.time() - start_process) > 600:
            sys.exit()

except KeyboardInterrupt:
    s.flush()
    while(s.in_waiting > 0):
        response = s.readline()
    print("end")
    s.close()