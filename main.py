from build_model import CreateDSSAT

# Path of the weather and managment files
wth_path = "Data\Weather\Essai irrigation.xlsx"
man_path = "Data\Probes\Sonde Robot 2.xlsx"

# Create DSSAT object
dssat = CreateDSSAT()

# Create stations
dssat.create_wth_station(wth_path)
dssat.create_management(man_path)

# dssat.create_wth_station()
# dssat.create_management()

# dssat.run_DSSAT()
# dssat.close_DSSAT()

# dates = ['15-1-2000', '28-1-2000', '25-2-2000', '24-2-2000']
dates = ['12-08-2022', '15-08-2022', '18-08-2022', '20-08-2022']
# dssat.next_dates =  dates
dssat.optimization_irri(dates)
# print(dssat.irri_cost([0, 0, 0, 0]))


# Execution time: 372.84
# The optimal values are (1.3, 0.0, 1.8, 0.8)
# 0.9702770177777776



