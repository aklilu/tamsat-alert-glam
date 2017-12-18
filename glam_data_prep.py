# =============================================================#
# Dagmawi T. Asfaw
# December, 2016
# ============================================================#
# This module is used to prepare the input .wth data files for
# GLAM:
# The data sets have five columns with date, swradiation, tmin,
# tmax, precip.
# each year data is saved as .wth file with the GLAM name format
# ==============================================================#
import numpy as np


def prepdata(filename, sta_name, lat, lon, datastartyear, dataendyear, wth_path):
    """
    This function will prepare the required weather data files
    to run the GLAM model for the location.
    :param filename: the file containing the long term weather data in the
                    format of JULES forcing file
    :param sta_name: name of station
           IMPORTANT --> this EXACT name should also be used in the glam config file
                         at 'WTHROOT'
    :param lat: the latitude of the location in degrees
    :param lon: the longitude of the location in degrees
    :param datastartyear: the year the data set start
    :param dataendyear: the the year the data set end
    :param wth_path: the path to the weather file (wth)
    """

    # reading the file containing all the environmental variables (JULES forcing file)
    data = np.genfromtxt(filename)
    daily_data(data, sta_name, lat, lon, datastartyear, dataendyear, wth_path)


def daily_data(data, sta_name, lat, lon, datastartyear, dataendyear, wth_path):
    """
    This function extract the required data values form the file
    used for the drought forecast (JULES forcing file). For the
    GLAM model short wave radiation, max temp., min temp, rainfall
    are required on a daily time scale.
    """
    # GLAM only takes 365 days in each year so we
    # remove leap year values from the long term time series
   
    if datastartyear % 4 == 1:  # if the start year is not a leap year (Matthew)
        for t in range(424, len(data), 1459):
            data = np.delete(data, t, axis=0)
    elif datastartyear % 4 == 2:  # if the start year is not a leap year (Mark)
        for t in range(789, len(data), 1459):
            data = np.delete(data, t, axis=0)
    elif datastartyear % 4 == 3:  # if the start year is not a leap year (Luke)
        for t in range(1154, len(data), 1459):
            data = np.delete(data, t, axis=0)
    elif datastartyear % 4 == 0:  # if the start year is a leap year (John)
        for t in range(59, len(data), 1459):
            data = np.delete(data, t, axis=0)
    else:
        raise ValueError('There is a problem on the datastartyear value. Please check on the config_file.txt')
    
    # extracting daily SHORTWAVE RADIATION 
    daily_sw = data[:, 0]

    # extracting daily RAINFALL 
    daily_precip = data[:, 2]
    # when new data added values are in kg-m2s-1 --> mm/day
    for i in range(0, len(daily_precip)):
        if daily_precip[i] < 0.002:  # up to 172 mm/day
            daily_precip[i] = daily_precip[i] * 86400 
        else:
            daily_precip[i] = daily_precip[i]
    del i
    # GLAM format do not accept daily rainfall above 99.9mm
    # therefore if there is a value above this 99.9 will be
    # set as a maximum value.
    for i in range(0, len(daily_precip)):
        if daily_precip[i] >= 100.0:
            daily_precip[i] = 99.9
        else:
            daily_precip[i] = daily_precip[i]

    # extracting daily TEMPERATURE (mean)
    daily_T = data[:, 4]

    # extracting daily DURATIONAL TEMPERATURE 
    daily_dtr = data[:, 9]

    # calculating MINIMUM TEMPERATURE 
    daily_tmin = []
    for i in range(0, len(daily_T)):
        T_min = ((2.0 * daily_T[i]) - daily_dtr[i]) / 2.0
        daily_tmin = np.append(daily_tmin, T_min)
    del i

    # calculating MAXIMUM TEMPERATURE
    daily_tmax = []
    for i in range(0, len(daily_T)):
        T_max = (2.0 * daily_T[i]) - daily_tmin[i]
        daily_tmax = np.append(daily_tmax, T_max)
    del i
    
    # extract each year data and save it according to GLAM format.
    # it requires unit conversion and format.
    year = np.arange(datastartyear, dataendyear+1)
    
    for i in range(0, len(daily_precip), 365):
        indata = []
        sw = (daily_sw[i:i+365]) * 0.0864  # unit (MJ m-2 day-1)
        indata = np.append(indata, sw)
        
        tmax = (daily_tmax[i:i+365]) - 273.15  # unit (celsius)
        indata = np.append(indata, tmax)
        
        tmin = (daily_tmin[i:i+365]) - 273.15  # unit (celsius)
        indata = np.append(indata, tmin)
        
        precip = daily_precip[i:i+365]  # unit (mm day-1)
        indata = np.append(indata, precip)
        
        # prepare the date in the GLAM format (yyddd)
        ddd = [format(item, "03d") for item in xrange(1, (len(precip)+1))]
        yy_tmp = map(int, str(year[int(i/365)]))
        yy = int(''.join(str(b) for b in yy_tmp[-2:]))
        yy = format(yy, "02d")
        date = []
        for v in range(0, len(ddd)):
            dateval = str(yy) + ddd[v]
            newdate = int(dateval)
            date = np.append(date, newdate)
        # concatenate date and data and save with filename format of GLAM
        indata = np.hstack((date, indata))
        indata = np.reshape(indata, (5, (len(indata)/5)))
        headval = '*WEATHER : Example weather file\n\
@INS   LAT  LONG  ELEV   TAV   AMP REFHT WNDHT\n\
ITHY %s  %s\n\
@DATE   SRAD   TMAX   TMIN   RAIN ' % (lat, lon)
        np.savetxt(wth_path + sta_name+'001001'+str(year[int(i/365)])+'.wth',
                   indata.T, header=headval, delimiter='', fmt='%05d%6.2f%6.2f%6.2f%6.2f')
        del indata
        del date
    return None
