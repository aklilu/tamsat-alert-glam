# ==================================================================#
# Dagmawi T. Asfaw
# December, 2016
# ==================================================================#
# This module is used to run the crop yield forecasting using
# historical climate data from the climatological period considered.
# "yieldforecast" function run a single day forecast (main function)
# "hindcast" function run hindcast mode for selected year, months and
# dates.
# ==================================================================#
import numpy as np
import datetime as dt
import os
import glob
import sys
from shutil import copyfile


def yieldforecast(datastartyear, dataendyear, climastartyear, climaendyear, forecastyear, forecastmonth, forecastday,
                  wth_path, sta_name, lat, lon, glam_command, weights, climafile, forecastfile):
    """
    This function is the function to extract data from climatological
    years add it to the forecast year and run the GLAM crop model to
    eatimate future crop yield for the forecast year we consider.
    
    :param datastartyear: the year the data set start
    :param dataendyear: the the year the data set end
    :param climastartyear: the year climatology value start.
    :param climaendyear: the year climatology value end.
    :param forecastyear: the year for which we are going to forecast yield
                         from historical climatic weather.
    :param forecastmonth: the month for which we are going to forecast yield
                         from historical climatic weather.
    :param forecastday: the day forecast start.(The last day for which
                        the forecast year has a data)
    :param wth_path: the file path where the .wth files are present (as string)
    :param sta_name: name of station or location
    :param lat: latitude of the location in degrees
    :param lon: longitude of the location in degrees
    :param glam_command: the GLAM command line to run the model (as string)
    :param weights: tercile forecast probabilities of the weighting metric used
    
    :return None 
    """
    path = wth_path 
    # 1. remove the # created by python since the FORTRAN can not read it
    filenames = glob.glob(path+'*.wth')
    for filename in filenames:
        filename = filename
        replace_word(filename, '#', '')

    # 2.1 create a folder to put the ensemble crop yield files
    if not os.path.isdir("./output/ensem_output"):
        os.makedirs("./output/ensem_output")

    # 2.2 create a folder to put the tamsat alert input files files
    if not os.path.isdir("./data_output"):
        os.makedirs("./data_output")

    # 2.3 create a folder to put the ensemble crop yield files
    if not os.path.isdir("./data_output/ensem_output"):
        os.makedirs("./data_output/ensem_output")

    # 3. identify the Julian day of year of the forecast date
    doy = dt.datetime(forecastyear, forecastmonth, forecastday).timetuple()
    doy = doy.tm_yday
    
    # 4. concatenate the weather data in the forecast year
    #    starting from the forecast day till the end of the
    #    year from all the climatological years considered.
    climayears = np.arange(climastartyear, climaendyear+1)

    # warning that certain number of years have been removed from the climatology
    # to make the length divisible by len(weight)
    ny_del = len(climayears) % len(weights)

    if ny_del != 0:
        climayears = climayears[:(len(climayears) - ny_del)]
        message = "WARNING: The last %s year of climatology years has been removed \n" \
                  "only %s ensembles are used!" % (ny_del, len(climayears))
        print message
    else:
        climayears = climayears
    
    path = wth_path
    # make a copy of the original weather file for the forecast year
    if not os.path.exists(path + 'origi_' + sta_name + '001001'+str(forecastyear)+'.wth'):
        copyfile(path + sta_name + '001001'+str(forecastyear)+'.wth',
                 path + 'origi_' + sta_name + '001001'+str(forecastyear)+'.wth')
    
    for i in range(0, len(climayears)):

        # copy the prepared ensemble data from the ensemrun path
        copyfile('.\ensemrun\ensrun_' + str(climayears[i]) + '.wth', path + sta_name + '001001' +  str(forecastyear)+'.wth')
        
        # prepare the forecast year weather data file in GLAM input file format

        replace_word(path + sta_name + '001001' + str(forecastyear)+'.wth', '#', '')
        
        # run the GLAM crop model
        command = glam_command
        os.system(command)

        # copy the model output file to the folder created on the first step
        os.system('cp ./output/maize.out ./output/ensem_output/maize_'+str(climayears[i])+'.out')

        # copy the model output file to the folder created on the first step
        os.system('cp ./output/maize.out ./data_output/ensem_output/maize_'+str(climayears[i])+'.out')

    # prepare the text files containing tamsat alert inputs
    # save the climatological time series
    climayield = np.genfromtxt('./output/ensem_output/maize_' + str(climayears[0])+'.out')[:len(climayears), 7]
    clima_ts = np.array([climayears, climayield])
    clima_ts = clima_ts.T
    np.savetxt(climafile, clima_ts, delimiter='   ', header='ClimaYears    MetricValue',
               fmt='%i    %0.2f')

    # yield data of forecast year based on all climatological year
    # weather data --> save the forecast ensemble time series
    years = np.arange(climastartyear, dataendyear+1)
    index = sorted(years).index(forecastyear)  # the index of the forecastyear to extract obs. yield from file

    forcayearyield = []
    for m in range(0, len(climayears)):
        filename = './data_output/ensem_output/maize_'+str(climayears[m])+'.out'
        x = np.genfromtxt(filename)[index, 7]  # yield data of forecast year
        forcayearyield = np.append(forcayearyield, x)
    foreca_ts = np.array([climayears, forcayearyield])
    foreca_ts = foreca_ts.T
    np.savetxt(forecastfile, foreca_ts, delimiter='   ', header='ClimaYears    MetricValue',
               fmt='%i    %0.2f')
    return None


def forecastyeardata_prep(forecayeardata, forecastyear, wth_path, sta_name, lat,lon):
    """
    This function will prepare the forecast year weather data
    file in the format required by GLAM input file format.
    """
    # extract each year data and save it according to GLAM format
    year = np.arange(forecastyear, forecastyear+1)
    path = wth_path 
    for i in range(0, 1):
        indata = forecayeardata[:, :]
        
        # prepare the date in the GLAM format (yyddd)
        ddd = [format(item, "03d") for item in xrange(1, (len(forecayeardata)+1))]
        yy_tmp = map(int, str(year[int(i/365)]))
        
        yy = int(''.join(str(b) for b in yy_tmp[-2:]))
        yy = format(yy, "02d")
        
        date = []
        for v in range(0, len(ddd)):
            dateval = str(yy) + ddd[v]
            newdate = int(dateval)
            date = np.append(date, newdate)
    
        indata[:, 0] = date
        
        headval = '*WEATHER : Example weather file\n\
@INS   LAT  LONG  ELEV   TAV   AMP REFHT WNDHT\n\
ITHY %s  %s\n\
@DATE   SRAD   TMAX   TMIN   RAIN ' % (lat, lon)
        np.savetxt(path + sta_name + '001001' +  str(year[int(i/365)])+'.wth',
                   indata, header=headval, delimiter='', fmt='%05d%6.2f%6.2f%6.2f%6.2f')
        del indata
        del date
        return None


def replace_word(infile, old_word, new_word):
    """
    This function helps to replace some characters not readable by the FORTRAN
    code in the GLAM input files

    :param infile: the file input where we want the characters to be changed.
    :param old_word: the old character to be changed.
    :param new_word: the new character to be changed with.

    :return None 
    """
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: "+infile)
        sys.exit(1)
    f1=open(infile, 'r').read()
    f2=open(infile, 'w')
    m=f1.replace(old_word, new_word)
    f2.write(m)
    return None


