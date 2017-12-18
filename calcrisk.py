# ====================================================================#
# This script is a more generalized TAMSAT-ALERT risk assessment tool.
# Dagmawi Teklu Asfaw
# November, 2017
# ====================================================================#
import numpy as np
import datetime as dt
import os
import matplotlib.pyplot as plt
import scipy.stats as sps
from statsmodels.distributions.empirical_distribution import ECDF
import seaborn as sns
import weighting
# ====================================================================#
# calculate the risk probability and present results
# ====================================================================#


def risk_prob_plot(climastartyear, climaendyear, forecastyear, forecastmonth, forecastday,
                   stat, sta_name, wth_path, weights, weight_var, wf_year, wf_month, wf_day,
                   w_leadtime, climafile, forecastfile, weightfile):
    """
    This function plot the probability estimates for poor yield for a single date
    forecast given in the configuration file.

    :param climastartyear: the year climatology value start.
    :param climaendyear: the year climatology value end.
    :param forecastyear: the year for which we are going to forecast yield
                         from historical climatic weather.
    :param forecastmonth: the month for which we are going to forecast yield
                         from historical climatic weather.
    :param forecastday: the day forecast start.(The last day for which
                        the forecast year has a data)
    :param stat: statistical method to be used for probability distribution comparison (ecdf or norm)
    :param sta_name: name of station or location
    :param wth_path: the file path where the .wth files are present (as string)
    :param weights: tercile forecast probabilities of the weighting metric used
    :param weight_var: the weighting variable used (0=rainfall, 1=temperature)
    :param wf_year: just one year to calculate days (leave it default)
    :param wf_month: the month from which we calculate the weighting metric
    :param wf_day: the day from which the weighting metric is calculated
    :param w_leadtime: the number of days from the wf_day the weighting metric will be assumed
    :param climafile: file contain climatological values of the metric under investigation
    :param forecastfile: file contain ensembles forecast values of the metric under investigation
    :param weightfile: file contain the weighting metric values
  
    """
    # creating folders to put output data and plot
    if not os.path.isdir("./plot_output"):
        os.makedirs("./plot_output")
    if not os.path.isdir("./plot_output/gaussian"):
        os.makedirs("./plot_output/gaussian")
    if not os.path.isdir("./plot_output/ecdf"):
        os.makedirs("./plot_output/ecdf")
   
    # set up actual dates for the x axis representation
    date = dt.datetime(forecastyear, forecastmonth, forecastday).date()
    f_date = date.strftime('%d-%b-%Y')

    climayears = np.arange(climastartyear, climaendyear+1)

    # warning that certain number of years have been removed from the
    # climatology to make the length divisible by len(weight)
    ny_del = len(climayears) % len(weights)
    if ny_del != 0:
        climayears = climayears[:(len(climayears) - ny_del)]
        message = "WARNING: The last %s year of climatology years has been removed \n" \
                  "only %s ensembles are used!" % (ny_del, len(climayears))
        print message
    else:
        climayears = climayears

    # reading necessary files required for tamsat-alert
    # generate weighting metric file
    # This function will make a weighting file from rainfall or temperature
    # from the given GLAM weather inputs. If one wants to weight with a different
    # variable the text file should be given in tamsat_alert directory with two
    # column 1= climayears 2= weighing metric values. File should have one line of header.
    weighting.weight_metric_prep(climayears, wth_path, sta_name, f_date, weight_var,
                                 wf_year, wf_month, wf_day, w_leadtime, weightfile)

    # read climatology time series (This file is created during crop yield forecast)
    climametric = np.genfromtxt(climafile, skip_header=1)[:, 1]

    # read forecast ensemble time series (This file is created during crop yield forecast)
    forecametric = np.genfromtxt(forecastfile, skip_header=1)[:, 1]

    # read Weighting metric time series (This file is created by weighting metric prep)
    # this only work for GLAM format so one has to write its own code or provide specific
    # file with two column 1, climayears 2, weight metric value (header must be given in the file)
    wmetric = np.genfromtxt(weightfile, skip_header=1)[:, 1]

    # calculating probability distribution
    # threshold probability 
    thresholds = np.arange(0.01, 1.01, 0.01)

    # calculate the mean and sd of the climatology
    climamean = np.mean(climametric)
    climasd = np.std(climametric)
    
    # calculate the mean and sd of the the projected
    # yield based on climatology weather data
    # we need the weighted yield forecast
    projmean, projsd = weight_forecast(forecametric, wmetric, weights)
    projsd = np.maximum(projsd, 0.001)  # avoid division by zero

    if stat == 'normal':
        # calculate the normal distribution
        probabilityyields = []
        for z in range(0, len(thresholds)):
            thres = sps.norm.ppf(thresholds[z], climamean, climasd)
            probyield = sps.norm.cdf(thres, projmean, projsd)
            probabilityyields = np.append(probabilityyields, probyield)
            del probyield         
        np.savetxt('./data_output/probyield_normal.txt', probabilityyields.T, fmt='%0.2f')
       
    elif stat == 'ecdf':
        # calculate the empirical distribution
        ecdf_clima = ECDF(climametric)
        probabilityyields = []
        for z in range(0, len(ecdf_clima.x)):
            thres = ecdf_clima.x[z]  # (thresholds[z])
            ecdf_proj = ECDF(forecametric)
            probyield = ecdf_proj(thres)
            probabilityyields = np.append(probabilityyields, probyield)
            del probyield
        np.savetxt('./data_output/probyield_ecdf.txt', probabilityyields.T, fmt='%0.2f')
    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')

    # Plots of results
    # Risk probability plot (original format ECB)
    sns.set_style("ticks")
    fig = plt.figure(figsize=(8, 6))
    ax = plt.subplot(111)
    if stat == 'normal':
        # Plot using normal distribution
        plt.plot(thresholds*100, thresholds, '--k', lw=1, label='Climatology')
        line = plt.plot(thresholds*100, probabilityyields, 'k', lw=1, label='Projected')
        # indicating critical points
        highlight_point(ax, line[0], [thresholds[79]*100, probabilityyields[79]], 'g')  # below average
        highlight_point(ax, line[0], [thresholds[59]*100, probabilityyields[59]], 'y')  # below average
        highlight_point(ax, line[0], [thresholds[39]*100, probabilityyields[39]], 'm')  # below average
        highlight_point(ax, line[0], [thresholds[19]*100, probabilityyields[19]], 'r')  # well below average
      
    elif stat == 'ecdf':
        # Plot using empirical cumulative distribution
        plt.plot(ecdf_clima.y*100, ecdf_clima.y, '--k', lw=1, label='Climatology')
        line = plt.plot(ecdf_clima.y*100, probabilityyields, 'k', lw=1, label='Projected')
        # identifying the index for the critical points
        nn = int(round(len(climayears)/5., 0))  # this should be an integer
        wba_i = nn 
        ba_i = (nn * 2) 
        a_i = (nn * 3) 
        av_i = (nn * 4) 
        # indicating critical points
        highlight_point(ax, line[0], [ecdf_clima.y[av_i]*100, probabilityyields[av_i]], 'g')  # below average
        highlight_point(ax, line[0], [ecdf_clima.y[a_i]*100, probabilityyields[a_i]], 'y')  # below average
        highlight_point(ax, line[0], [ecdf_clima.y[ba_i]*100, probabilityyields[ba_i]], 'm')  # below average
        highlight_point(ax, line[0], [ecdf_clima.y[wba_i]*100, probabilityyields[wba_i]], 'r')  # well below average
    
    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')

    plt.title('Theme: Probability of yield estimate (against ' + str(climastartyear) + '-' + str(climaendyear) +
              ' climatology)\nLocation: ' + sta_name + '\nForecast date: ' + f_date, loc='left', fontsize=14)
    plt.xlabel('Climatology', fontsize=14)
    plt.ylabel('Probability <= Climatological percentile', fontsize=14)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.legend()
    plt.tight_layout()
    if stat == 'normal': 
        path = './plot_output/gaussian/'
    elif stat == 'ecdf':
        path = './plot_output/ecdf/'
    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')
    fig.savefig(path + sta_name+'_'+f_date+'_yieldprob.png', dpi=300)
    plt.close()

    # Risk probability plot (Pentiles bar plot format DA)
    pp = []
    sns.set_style("ticks")
    fig = plt.figure(figsize=(8, 6))
    if stat == 'normal':
        verylow = probabilityyields[19] 
        low = probabilityyields[39] - verylow
        average = probabilityyields[59] - (verylow+low)    
        high = probabilityyields[79] - (verylow+low+average)
        veryhigh = 1 - (verylow+low+average+high)
    elif stat == 'ecdf':

        # identifying the index for the critical points
        nn = int(round(len(climayears)/5., 0))  # this should be an integer
        wba_i = nn 
        ba_i = (nn * 2) 
        a_i = (nn * 3) 
        av_i = (nn * 4) 
        
        verylow = probabilityyields[wba_i] 
        low = probabilityyields[ba_i] - probabilityyields[wba_i]  # verylow
        average = probabilityyields[a_i] - probabilityyields[ba_i]  # (verylow+low)
        high = probabilityyields[av_i] - probabilityyields[a_i]  # (verylow+low+average)
        veryhigh = 1 - probabilityyields[av_i]  # (verylow+low+average+high)
    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')    

    val = [verylow, low, average, high, veryhigh]   # the bar lengths
    pos = np.arange(5)+.5        # the bar centers on the y axis
    plt.barh(pos[0], val[0]*100, align='center', color='r', label='Very low (0-20%)')
    plt.barh(pos[1], val[1]*100, align='center', color='m', label='Low (20-40%)')
    plt.barh(pos[2], val[2]*100, align='center', color='grey', label='Average (40-60%)')
    plt.barh(pos[3], val[3]*100, align='center', color='b', label='High (60-80%)')
    plt.barh(pos[4], val[4]*100, align='center', color='g', label='Very high (80-100%)')
    
    plt.annotate(str(round(val[0]*100, 1))+'%', ((val[0]*100)+1, pos[0]), xytext=(0, 1), textcoords='offset points', fontsize=20)
    plt.annotate(str(round(val[1]*100, 1))+'%', ((val[1]*100)+1, pos[1]), xytext=(0, 1), textcoords='offset points', fontsize=20)
    plt.annotate(str(round(val[2]*100, 1))+'%', ((val[2]*100)+1, pos[2]), xytext=(0, 1), textcoords='offset points', fontsize=20)
    plt.annotate(str(round(val[3]*100, 1))+'%', ((val[3]*100)+1, pos[3]), xytext=(0, 1), textcoords='offset points', fontsize=20)
    plt.annotate(str(round(val[4]*100, 1))+'%', ((val[4]*100)+1, pos[4]), xytext=(0, 1), textcoords='offset points', fontsize=20)

    plt.yticks(pos, ('Very low', 'Low', 'Average', 'High', 'Very high'), fontsize=14)
    plt.xticks(fontsize=14)
    plt.xlabel('Probability', fontsize=14)
    plt.title('Theme: Probability of yield estimate (against ' + str(climastartyear) + '-' + str(climaendyear) +
              ' climatology)\nLocation: ' + sta_name+'\nForecast date: ' + f_date, loc='left', fontsize=14)
    plt.xlim(0, 101)
    plt.legend()
    plt.tight_layout()
    if stat == 'normal': 
        path = './plot_output/gaussian/'
    elif stat == 'ecdf':
        path = './plot_output/ecdf/'
    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')

    # append the probabilities to pp
    pp = np.append(pp, round(val[0]*100, 1))
    pp = np.append(pp, round(val[1]*100, 1))
    pp = np.append(pp, round(val[2]*100, 1))
    pp = np.append(pp, round(val[3]*100, 1))
    pp = np.append(pp, round(val[4]*100, 1))
    
    fig.savefig(path + sta_name+'_'+f_date+'_pentile.png', dpi=300)
    plt.close()
    
    # save the probabilities of each category on a text file
    headval = '1 = Very low(0-20%)  2 = Low(20-40%)   3 = Average(40-60%)  4 = High(60-80%)  5 = Very high(80-100%)\n\
Category    Probability'
    category = [1, 2, 3, 4, 5]
    rp = np.array([category, pp])
    rp = rp.T
    np.savetxt('./data_output/RiskProbability.txt', rp, delimiter=' ', header=headval, fmt='%i   %6.2f')

    # probability density plot
    sns.set_style("ticks")
    fig = plt.figure(figsize=(8, 6))
    if stat == 'normal':
        # Plot using normal distribution
        sns.kdeplot(climametric, bw=10, shade=True, label='Climatology', cumulative=False)
        sns.kdeplot(forecametric, bw=10, shade=False, color='g', label='Projected', cumulative=False)

    elif stat == 'ecdf':
        # Plot using empirical cumulative distribution
        sns.kdeplot(climametric, bw=10, shade=True, label='Climatology', cumulative=False)
        sns.kdeplot(forecametric, bw=10, shade=False, label='Projected', cumulative=False)

    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')
    plt.title('Theme: Probability of yield estimate (against ' + str(climastartyear)+'-' + str(climaendyear) +
              ' climatology)\nLocation: ' + sta_name + '\nForecast date: ' + f_date, loc='left', fontsize=14)
    plt.xlabel('Yield (Kg/ha)', fontsize=14)
    plt.ylabel('Probability density', fontsize=14)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.legend()
    plt.tight_layout()
    if stat == 'normal': 
        path = './plot_output/gaussian/'
    elif stat == 'ecdf':
        path = './plot_output/ecdf/'
    else:
        raise ValueError('Please use only "normal" or "ecdf" stat method')
    fig.savefig(path + sta_name + '_' + f_date + '_ked_plot.png', dpi=300)
    plt.close()

    # histogram plot
    sns.set_style("ticks")
    fig = plt.figure(figsize=(8, 6))
    binboundaries = np.linspace(min(forecametric)-(0.01*(min(forecametric))), max(forecametric)+(0.01*(max(forecametric))), 10)
    sns.distplot(forecametric, bins=binboundaries, hist=True, kde=False, label=f_date, hist_kws={"color": "b"})
    plt.xlabel('Yield ($\mathregular{Kg ha^{-1}}$)', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.title('Theme: Probability of yield estimate (against ' + str(climastartyear) + '-' + str(climaendyear) +
              ' climatology)\nLocation: ' + sta_name + '\nForecast date: ' + f_date, loc='left', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlim(min(forecametric)-(0.01*(min(forecametric))), max(forecametric)+(0.01*(max(forecametric))))
    plt.ylim(0, len(forecametric)+1)
    plt.tight_layout()                
    fig.savefig(path + sta_name + '_' + f_date + '_hist_plot.png', dpi=300)
    plt.close()

    # plot additional variables of the input data
    cum_plots(climastartyear, climaendyear, forecastyear, sta_name, wth_path, weights)
    return pp

        
def highlight_point(ax, line, point, c, linestyle=':'):
    """
    This is an extra function to highlight three of the probability
    points on the plot. It is part of the main plotting function.
    """
    label = ['well below average = ', 'Below average = ', 'Average = ', 'Above average = ']
    c = c 
    xmin = 0  # ax.get_xlim()[0]
    ymin = 0  # ax.get_ylim()[0]
    if c == 'r':
        label = label[0]
    elif c == 'm':
        label = label[1]
    elif c == 'y':
        label = label[2]
    elif c == 'g':
        label = label[3]
    else:
        raise ValueError('Only chose colors green,yellow or red')
    ax.plot([xmin, point[0]], [point[1], point[1]], color=c, linestyle=linestyle, label=label+str(round(point[1], 2)))
    ax.plot([point[0], point[0]], [ymin, point[1]], color=c, linestyle=linestyle)
    return None


def weight_forecast(forecametric, wmetric, weights):
    fy_wmean = []
    # the metric for ordering the true metric(forecametric)
    # is total precipitation or mean temperature.
    out = zip(wmetric, forecametric)  # put the metric with true metric (forecametric)
    out = sorted(out)  # sort in  ascending order based on the metric
    out = np.array(out)  # convert it to array
    # weighting forecast metric with the weighting metric
    n_reps = np.shape(out)[0] / len(weights) 
    allweights = []
    for j in range(0, len(weights)):
        allweights = np.append(allweights, np.repeat(weights[j], n_reps))
    allweights = (allweights/sum(allweights))
    # weighted average of forecasted yield after being sorted by the metric
    a = np.average(out[:, 1], weights=allweights)
    fy_wmean = np.append(fy_wmean, a)  # projected weighted mean
    # projected weighted standard deviation
    variance = np.average((forecametric-fy_wmean)**2, weights=allweights)  
    fy_wsd = np.sqrt(variance) 
    del allweights
    return fy_wmean, fy_wsd


def cum_plots(climastartyear, climaendyear, forecastyear, sta_name, wth_path, weights):
    """
    :param climastartyear: the year climatology value start.
    :param climaendyear: the year climatology value end.
    :param forecastyear: the year for which we are going to forecast yield
                         from historical climatic weather.
    :param forecastyear: the year forecast start.
    :param sta_name: the name of the station or point.
    :param wth_path: the path of the wth file (where the weather data is.)
    :param weights: the tercile forecast weights

    :return None 
   """
    climayears = np.arange(climastartyear, climaendyear+1)

    # warning that certain number of years have been removed from the climatology
    # to make the length divisioble by len(weight) 
    ny_del = len(climayears) % len(weights)
    if ny_del != 0:
        climayears = climayears[:(len(climayears) - ny_del)]
        message = "WARNING: The last %s year of climatology years has been removed \n " \
                  "only %s ensembles are used!" % (ny_del, len(climayears))
        print message
    else:
        climayears = climayears

    path = wth_path
    # read the file containing the forecast year weather data
    forecastyeardata = np.genfromtxt(path+'origi_'+sta_name+'001001'+str(forecastyear)+'.wth', skip_header=4)

    # reading the climatological years data
    precip = forecastyeardata[:, 4]
    cumprecip = np.cumsum(precip)

    tmin = forecastyeardata[:, 3]
    tmax = forecastyeardata[:, 2]
    swr = forecastyeardata[:, 1]
    
    climarain_all = []
    climatmin_all = []
    climatmax_all = []
    climaswr_all = []
    for i in range(0, len(climayears)):
        # read the file containing the climatological weather data
        climadata = np.genfromtxt(path+sta_name+'001001'+str(climayears[i])+'.wth', skip_header=4)
        climarain = climadata[:, 4]
        climarain = np.cumsum(climarain)
        climarain_all = np.append(climarain_all, climarain)

        climatmin = climadata[:, 3]
        climatmin_all = np.append(climatmin_all, climatmin)

        climatmax = climadata[:, 2]
        climatmax_all = np.append(climatmax_all, climatmax)

        climaswr = climadata[:, 1]
        climaswr_all = np.append(climaswr_all, climaswr)
        
    climarain_all = np.reshape(climarain_all, (len(climayears), 365))
    climatmin_all = np.reshape(climatmin_all, (len(climayears), 365))
    climatmax_all = np.reshape(climatmax_all, (len(climayears), 365))
    climaswr_all = np.reshape(climaswr_all, (len(climayears), 365))

    av_rain = np.mean(climarain_all, axis=0)
    av_tmin = np.mean(climatmin_all, axis=0)
    av_tmax = np.mean(climatmax_all, axis=0)
    av_swr = np.mean(climaswr_all, axis=0)

    fig = plt.figure(figsize=(8, 6))
    sns.set_style("ticks")
    plt.plot(cumprecip, 'b', label=str(forecastyear))
    plt.plot(av_rain, 'r', label='Climatology average ('+str(climayears[0])+'-'+str(climayears[-1])+')')
    plt.xlabel('DOY', fontsize=14)
    plt.ylabel('Precipitation (mm)', fontsize=14)
    plt.title('Theme: Cumulative rainfall\nLocation: '+sta_name, loc='left', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend()
    plt.tight_layout()                
    fig.savefig('./plot_output/cum_precip.png', dpi=300)
    plt.close()

    fig = plt.figure(figsize=(8, 6))
    sns.set_style("ticks")
    plt.plot(tmin, 'b', label=str(forecastyear))
    plt.plot(av_tmin, 'r', label='Climatology average ('+str(climayears[0])+'-'+str(climayears[-1])+')')
    plt.xlabel('DOY', fontsize=14)
    plt.ylabel('Temperature (C)', fontsize=14)
    plt.title('Theme: Minimum Temperature\nLocation: '+sta_name, loc='left', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend()
    fig.tight_layout()
    plt.savefig('./plot_output/tmin.png', dpi=300)
    plt.close()

    fig = plt.figure(figsize=(8, 6))
    sns.set_style("ticks")
    plt.plot(tmax, 'b', label=str(forecastyear))
    plt.plot(av_tmax, 'r', label='Climatology average ('+str(climayears[0])+'-'+str(climayears[-1])+')')
    plt.xlabel('DOY', fontsize=14)
    plt.ylabel('Temperature (C)', fontsize=14)
    plt.title('Theme: Maximum Temperature\nLocation: '+sta_name, loc='left', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend()
    plt.tight_layout()                
    fig.savefig('./plot_output/tmax.png', dpi=300)
    plt.close()

    fig = plt.figure(figsize=(8, 6))
    sns.set_style("ticks")
    plt.plot(swr, 'b', label=str(forecastyear))
    plt.plot(av_swr, 'r', label='Climatology average ('+str(climayears[0])+'-'+str(climayears[-1])+')')
    plt.xlabel('DOY', fontsize=14)
    plt.ylabel('SWR (MJ m-2 day-1)', fontsize=14)
    plt.title('Theme: Short Wave Radiation\nLocation: '+sta_name, loc='left', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend()
    plt.tight_layout()                
    fig.savefig('./plot_output/swr.png', dpi=300)
    plt.close()
