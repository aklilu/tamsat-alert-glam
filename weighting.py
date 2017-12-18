# =============================================================================##
# Dagmawi Teklu Asfaw
# October 2017
#
# This module contain the weighting metric preparation function for
# TAMSAT-ALERT-GLAM. It take the arguments given and prepare the weighting
# metric of rainfall sum or mean temperature from the input data sets
# =============================================================================##
import numpy as np
import datetime as dt


def weight_metric_prep(climayears, wth_path, sta_name, f_date, weight_var,
                       wf_year, wf_month, wf_day, w_leadtime, weightfile):
    """
    This function takes the given weight forecast metrics variable and the
    dates and lead time for the weighting metrics and prepare the values
    from the input data set for GLAM. It can only work for rainfall sum and
    mean temperature.
    :param climayears: the climatological years array
    :param sta_name: the name of the station or point.
    :param wth_path: the path of the wth file (where the weather data is.)
    :param f_date: the date of forecast in a string format
    :param weight_var: the variable used for weighting the yield 0 for rainfall and 1 for temperature.
    :param wf_year: the year value for the forecast (this value is a dummy value to count dates)
    :param wf_month: the first month of the season for which weighting is considered (e.g. wf_month = 6 if season used is JJA)
    :param wf_day: the first day for the season for which weighting is considered
    :param w_leadtime: the length of the day for which values are summed or averaged to prepare the weight metric

    :return weighted mean of forcayearyield values.
    """
    # identify the Julian day of year of the forecast date
    fdoy = dt.datetime.strptime(f_date, '%d-%b-%Y')
    fdoy = fdoy.timetuple().tm_yday

    # the season starting dates of the 12 months
    # these dates are the dates set by the user for the forecast
    # if it chose 25th date then it will be the 25th date of every
    # month. When the 31st date is chosen it will keep the 30th date
    # for all the months with 30 days and 28th day for Feb.
    # These dates will be the start of the season for the weighting
    # by adding the user defined lead time (w_leadtime)on it.
    ss_date = []
    for m in range(1, 13):
        if m == 2 and wf_day > 28:
            ss_date.append(59)    
        elif m == 4 and wf_day > 30:
            ss_date.append(120)
        elif m == 6 and wf_day > 30:
            ss_date.append(181)
        elif m == 9 and wf_day > 30:
            ss_date.append(273)
        elif m == 11 and wf_day > 30:
            ss_date.append(334)   
        else:
            dd = dt.datetime(wf_year, m, wf_day)
            wdoy = dd.timetuple().tm_yday
            ss_date.append(wdoy)

    # for a single date forecast the weights are read from the ReadVar.py
    # and they will be interpreted as the 90 (lead time) days forecast from the next month
    # onwards.(e.g. if forecast month is 5 (May) the weights given will be considered as
    # June-July-August(182 + leadtime)).
#    wf_month = forecastmonth + 1  # the weights will be starting from the next month + leadtime days
    
    # generating the 4 seasons starting date (the seasons used in the weighting 'weight.txt')
    if wf_month <= 9:
        svals = ss_date[wf_month - 1: (wf_month - 1) + 4]
    else:
        svals1 = ss_date[wf_month - 1:]
        svals2 = ss_date[:(4 - len(svals1))]
        svals1.extend(svals2)  # concatenate the dates
        svals = svals1
    s1s = svals[0] 
    s2s = svals[1]
    s3s = svals[2]
    s4s = svals[3]   

    if weight_var == 0:
        # read the file containing the climatological weather data
        daily_precip = []
        for i in range(0, len(climayears)):
            climaprecip = np.genfromtxt(wth_path + sta_name + '001001' + str(climayears[i])+'.wth', skip_header=4)[:, 4]
            daily_precip = np.append(daily_precip, climaprecip)

        # Precipitation value of the climatological periods
        outmat = np.reshape(daily_precip, (len(climayears), 365))

        if fdoy < s1s:
            if s1s <= (s1s + w_leadtime):
                metric = np.sum(outmat[:, s1s:s1s + w_leadtime], axis=1)  # weighted by JJA forecast
            else:
                metric1 = np.sum(outmat[:, s1s:], axis=1)
                metric2 = np.sum(outmat[:, :((s1s + w_leadtime) - 365)], axis=1)
                metric = metric1 + metric2   
           
        elif (fdoy >= s1s) and (fdoy < s2s):
            if s2s <= (s2s + w_leadtime):
                metric = np.sum(outmat[:, s2s:s2s + w_leadtime], axis=1)  # weighted by JAS forecast
            else:
                metric1 = np.sum(outmat[:, s2s:], axis=1)
                metric2 = np.sum(outmat[:, :((s2s + w_leadtime) - 365)], axis=1)
                metric = metric1 + metric2     # weighted by JAS forecast
           
        elif (fdoy >= s2s) and (fdoy < s3s):
            if s3s <= (s3s + w_leadtime):
                metric = np.sum(outmat[:, s3s:s3s + w_leadtime], axis=1)  # weighted by ASO forecast
            else:
                metric1 = np.sum(outmat[:, s3s:], axis=1)
                metric2 = np.sum(outmat[:, :((s3s + w_leadtime) - 365)], axis=1)
                metric = metric1 + metric2   
           
        elif (fdoy >= s3s) and (fdoy < s4s):
            if s4s <= (s4s + w_leadtime):
                metric = np.sum(outmat[:, s4s:s4s + w_leadtime], axis=1)  # weighted by JJA forecast
            else:
                metric1 = np.sum(outmat[:, s4s:], axis=1)
                metric2 = np.sum(outmat[:, :((s4s + w_leadtime) - 365)], axis=1)
                metric = metric1 + metric2   
           
        else:
            if s4s <= (s4s + w_leadtime):
                metric = np.sum(outmat[:, s4s:s4s + w_leadtime], axis=1)  # weighted by JJA forecast
            else:
                metric1 = np.sum(outmat[:, s4s:], axis=1)
                metric2 = np.sum(outmat[:, :((s4s + w_leadtime) - 365)], axis=1)
                metric = metric1 + metric2   

    elif weight_var == 1:
        # read the file containing the climatological weather data
        daily_tmin = []
        daily_tmax = []
        for i in range(0, len(climayears)):
            climatmin = np.genfromtxt(wth_path + sta_name + '001001' + str(climayears[i])+'.wth', skip_header=4)[:, 3]
            climatmax = np.genfromtxt(wth_path + sta_name + '001001' + str(climayears[i])+'.wth', skip_header=4)[:, 2]
            daily_tmin = np.append(daily_tmin, climatmin)
            daily_tmax = np.append(daily_tmax, climatmax)
        # mean temperature
        daily_tmean = (daily_tmin + daily_tmax) / 2.0

        # Precipitation value of the climatological periods
        outmat = np.reshape(daily_tmean, (len(climayears), 365))

        if fdoy < s1s:
            if s1s <= (s1s + w_leadtime):
                metric = np.mean(outmat[:, s1s:s1s + w_leadtime], axis=1)  # weighted by JJA forecast
            else:
                metric1 = np.mean(outmat[:, s1s:], axis=1)
                metric2 = np.mean(outmat[:, :((s1s + w_leadtime) - 365)], axis=1)
                metric = (metric1 + metric2) / 2.
         
        elif (fdoy >= s1s) and (fdoy < s2s):
            if s2s <= (s2s + w_leadtime):
                metric = np.mean(outmat[:, s2s:s2s + w_leadtime], axis=1)  # weighted by JAS forecast
            else:
                metric1 = np.mean(outmat[:, s2s:], axis=1)
                metric2 = np.mean(outmat[:, :((s2s + w_leadtime) - 365)], axis=1)
                metric = (metric1 + metric2) / 2.     # weighted by JAS forecast
          
        elif (fdoy >= s2s) and (fdoy < s3s):
            if s3s <= (s3s + w_leadtime):
                metric = np.mean(outmat[:, s3s:s3s + w_leadtime], axis=1)  # weighted by ASO forecast
            else:
                metric1 = np.mean(outmat[:, s3s:], axis=1)
                metric2 = np.mean(outmat[:, :((s3s + w_leadtime) - 365)], axis=1)
                metric = (metric1 + metric2) / 2.   
          
        elif (fdoy >= s3s) and (fdoy < s4s):
            if s4s <= (s4s + w_leadtime):
                metric = np.mean(outmat[:, s4s:s4s + w_leadtime], axis=1)  # weighted by JJA forecast
            else:
                metric1 = np.mean(outmat[:, s4s:], axis=1)
                metric2 = np.mean(outmat[:, :((s4s + w_leadtime) - 365)], axis=1)
                metric = (metric1 + metric2) / 2.   
          
        else:
            if s4s <= (s4s + w_leadtime):
                metric = np.mean(outmat[:, s4s:s4s + w_leadtime], axis=1)  # weighted by JJA forecast
            else:
                metric1 = np.mean(outmat[:, s4s:], axis=1)
                metric2 = np.mean(outmat[:, :((s4s + w_leadtime) - 365)], axis=1)
                metric = (metric1 + metric2) / 2.   
       
    else:
        raise ValueError('Weighting can be don by rain(0) or temperature(1). Please put 0 or 1 only!')

    # save the metric in a text file
    weightmetric_ts = np.array([climayears, metric])
    weightmetric_ts = weightmetric_ts.T
    np.savetxt(weightfile, weightmetric_ts, delimiter=' ', header='ClimaYears    WeightMetricValue', fmt='%i    %6.2f')
