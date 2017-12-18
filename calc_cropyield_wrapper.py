# =======================================================================##
# Dagmawi T. Asfaw
# December, 2017
# =======================================================================##
# This module is a wrapper module which prepare the weather data and
# run the yield forecast. The input file required is the long term
# climatic variables used for forcing JULES model.
# The function main() contain 5 step processes:
# 1. prepare the ensemble files for the forecast year
# 2. prepare the ensemble files in GLAM data format.
# 3. run the GLAM command for yield simulation and risk calculation.
# ======================================================================##

from prepare_driving import *
import ensem_glam_data_prep
import os
import glob
import datetime as dt
import hydraulic_params
import glam_data_prep
import cropyield_est
import calcrisk
from ReadVar import *


def glam_run():
    """
    This is a wrapper function that combine the preparation of GLAM weather driving
    data preparation and running TAMSAT-ALERT to calculate risk.
    :return: None
    """
    starttime = dt.datetime.now()

    # 1. prepare the ensemble files for the forecast year
    outdata = prepare_historical_run(filename, leapremoved, datastartyear)
    output = prepare_ensemble_runs(forecastyear, forecastmonth, forecastday,
                                   periodstart_year, periodstart_month, periodstart_day,
                                   periodend_year, periodend_month, periodend_day, datastartyear,
                                   climstartyear, climendyear, leapinit, outdata[1], outdata[0])

    # 2. prepare the ensemble files in GLAM data format.
    # The files are for the forecast year based on all the
    # climatological weather data considered after the forecast date.
    climayears = np.arange(climstartyear, climendyear+1)
    for i in range(0, len(climayears)):
        ensemrun_path = './ensemrun/'
        ense_filename = ensemrun_path+"ensrun_"+str(climayears[i])+".txt"
        ensem_glam_data_prep.prepdata(ense_filename, sta_name, lat, lon, climastartyear,
                                      climaendyear, forecastyear, ensemrun_path)

    # 3. run the GLAM command for yield simulation and risk calculation

    # 3.1 import all the required variables from the ReadVar.py script
    # imported with the modules above !!!

    # 3.2 Prepare the .wth weather files for GLAM
    glam_data_prep.prepdata(filename, sta_name, lat, lon, datastartyear, dataendyear, wth_path)

    # 3.3 Soil properties vales are saved (soils.txt)
    hydraulic_params.pedoclass(soiltex, wth_path)

    # 3.4 Run the yield forecast for a single date and plot
    cropyield_est.yieldforecast(datastartyear, dataendyear, climastartyear, climaendyear,
                                forecastyear, forecastmonth, forecastday, wth_path, sta_name,
                                lat, lon, glam_command, weights, climafile, forecastfile)

    # 3.5 run TAMSAT-ALERT risk (result will be plots)
    calcrisk.risk_prob_plot(climastartyear, climaendyear, forecastyear, forecastmonth, forecastday,
                            stat, sta_name, wth_path, weights, weight_var, wf_year, wf_month,
                            wf_day, w_leadtime, climafile, forecastfile, weightfile)

    # remove all the weather data in the wth folder (This cleans folder for next run)
    files = glob.glob(wth_path + '/*')
    for f in files:
        os.remove(f)

    endtime = dt.datetime.now()
    time_diff = endtime - starttime
    print "Time it took to complete the task -> %s" % time_diff

    return None

# ============================================================================#


if __name__ == '__main__':
    glam_run()
