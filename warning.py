# This is a warning script for checking TAMSAT-ALERT_GLAM input variables


def check_input_var(filename, sta_name, stat, wth_path, glam_command, soiltex, lat, lon,
                    datastartyear, dataendyear, climastartyear, climaendyear, forecastyear,
                    forecastmonth, forecastday, weights, weight_var, wf_year, wf_month,
                    wf_day, w_leadtime):

    # check for the file name
    if type(filename) is str:
        pass
    else:
        raise ValueError("File name input is not correct please give the file name as string. [e.g. 'abcd.txt']")

    if filename.lower().endswith('.txt'):
        pass
    else:
        raise ValueError("File should be a text file with extension .txt! [e.g. 'abcd.txt']")

    # check for station name
    if type(sta_name) is str:
        pass
    else:
        raise ValueError("Station name input is not correct please give the station name as string. [e.g. 'xyz']")

    # check for stat
    if stat == "normal" or stat == "ecdf":
        pass
    else:
        raise ValueError("stat can only take 'normal' or 'ecdf'. Please check the variable you put!")

    # check for wth_path and glam_command
    if type(wth_path) is str:
        pass
    else:
        raise ValueError("wth_path input is not correct please give the as string.")

    if type(glam_command) is str:
        pass
    else:
        raise ValueError("glam_command input is not correct please give the as string." +
                         "Please refer to the TAMSAT-ALERT manual for  detail on GLAM command")

    # check for soil texture name
    soiltex_class = ['clay', 'silty clay', 'sandy clay', 'silty clay loam',
                     'clay loam', 'sandy clay loam', 'loam', 'silt loam',
                     'sandy loam', 'silt', 'loamy sand', 'sand']

    if soiltex in soiltex_class:
        pass
    else:
        raise ValueError("soiltex can only take one of these values 'clay', 'silty clay'," +
                         "'sandy clay', 'silty clay loam','clay loam', 'sandy clay loam'," +
                         "'loam', 'silt loam','sandy loam', 'silt', 'loamy sand', 'sand'")

    # check lat and lon
    if lat <= -90. or lat >= 90.:
        raise ValueError("Latitude value must be between -90.0 and 90.0")
    if lon <= -180. or lon >= 180.:
        raise ValueError("Longitude value must be between -180.0 and 180.0")

    # check data start year and data end year
    if type(datastartyear) is int:
        pass
    else:
        raise ValueError("datastartyear must be an integer value [e.g. 1978]")
    if type(dataendyear) is int:
        pass
    else:
        raise ValueError("dataendyear must be an integer value [e.g. 1978]")

    if dataendyear < datastartyear:
        raise ValueError("dataendyear can not be less than datastartyear!")

    # check climatology years
    if type(climastartyear) is int:
        pass
    else:
        raise ValueError("climastartyear must be an integer value [e.g. 1978]")
    if type(climaendyear) is int:
        pass
    else:
        raise ValueError("climaendyear must be an integer value [e.g. 1978]")

    if climaendyear < climastartyear:
        raise ValueError("climaendyear can not be less than climastartyear!")

    # cross check between data years and clima years
    if climaendyear > dataendyear:
        raise ValueError("climaendyear can not be greater than dataendyear!")
    if climastartyear < datastartyear:
        raise ValueError("climastartyear can not be less than datastartyear!")

    # check forecast year, month, day
    if type(forecastyear) is int:
        pass
    else:
        raise ValueError("forecastyear must be an integer value [e.g. 1978]")
    if forecastyear > dataendyear:
        raise ValueError("forecastyear can not be greater than dataendyear")

    if type(forecastmonth) is int:
        pass
    else:
        raise ValueError("forecastmonth must be an integer value [e.g. 1]")
    if forecastmonth < 1 or forecastmonth > 12:
        raise ValueError("forecastmonth must be between 1 and 12!")
    if type(forecastday) is int:
        pass
    else:
        raise ValueError("forecastday must be an integer value [e.g. 23]")
    if forecastday < 1 or forecastday > 31:
        raise ValueError("forecastday must be between 1 and 31")

    # check weight
    if type(weights) is list:
        pass
    else:
        raise ValueError("weights must be a list of values for tercile or pentile forecast (e.g. [0.33, 0.34, 0.33])")

    # check weight variable
    if type(weight_var) is int:
        pass
    else:
        raise ValueError("weight_var must be an integer value of 0 or 1!")

    if weight_var == 0 or weight_var == 1:
        pass
    else:
        raise ValueError("weight_var must be  0 (rainfall sum) or 1 (mean temperature)")

    # check for weight forecast year, month, day
    if type(wf_year) is int:
        pass
    else:
        raise ValueError("wf_year must be an integer value [e.g. 1978]")

    if type(wf_month) is int:
        pass
    else:
        raise ValueError("wf_month must be an integer value [e.g. 6]")
    if wf_month < 1 or wf_month > 12:
        raise ValueError("wf_month must be between 1 and 12!")
    if type(wf_day) is int:
        pass
    else:
        raise ValueError("wf_day must be an integer value [e.g. 23]")
    if wf_day < 1 or wf_day > 31:
        raise ValueError("wf_day must be between 1 and 31")

    # check for the lead time
    if type(w_leadtime) is int:
        pass
    else:
        raise ValueError("w_leadtime must be an integer value [e.g. 90]")
    if w_leadtime < 1 or w_leadtime > 365:
        raise ValueError("w_leadtime must be between 1 and 365")

    return None
