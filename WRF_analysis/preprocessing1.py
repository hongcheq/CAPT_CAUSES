'''
Function: preprocessing using python scripts
Date: 20200318
'''
from __future__ import print_function

from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES, extract_times

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import pandas
import datetime
import ESMF

# This call enables debug logging
# esmpy = ESMF.Manager(debug=True)
print ("Hello ESMPy World from PET (processor) {0}!".format(ESMF.local_pet()))

dir_string = "/global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/LGdm.STD2011/"

#month_str = ['05','06','07','08']
month_str = ['05']

#name_str = [''] * 2922
#name_str = [''] * 738
name_str = [''] * (3*24-6)  # for faster testing

day_str = ['01','02','03']

#day_str = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14',\
#           '15','16','17','18','19','20','21','22','23','24','25','26','27','28',\
#           '29','30','31']
hour_str = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13',\
            '14','15','16','17','18','19','20','21','22','23']


#for i in range(0,18):
#    name_str[i] = "wrfout_d01_2011-05-01_"+hour_str[i+6]+":00:00"

# Note the wrfout put does not have 08-31 outputs
icount = 0
for i_month in range(len(month_str)):
    if i_month == 0 or i_month == 2 : # May, Jul;
        for i_day in range(len(day_str)):
            if (i_month == 0 and i_day == 0): # 05-01
                for i_hour in range(0,18):
                    name_str[icount] = dir_string+"wrfout_d01_2011-"+month_str[i_month]+"-"+day_str[i_day]+"_"+hour_str[i_hour+6]+":00:00"
                    icount = icount + 1
            else:
                for i_hour in range(len(hour_str)):
                    # print(icount)
                    name_str[icount] = dir_string+"wrfout_d01_2011-"+month_str[i_month]+"-"+day_str[i_day]+"_"+hour_str[i_hour]+":00:00"
                    icount = icount + 1
    else: # June, only has 30 days; Aug: the wrfout puts does not have 08-31 outputs
        for i_day in range(len(day_str)-1):
            for i_hour in range(len(hour_str)):
                    name_str[icount] = dir_string+"wrfout_d01_2011-"+month_str[i_month]+"-"+day_str[i_day]+"_"+hour_str[i_hour]+":00:00"
                    icount = icount + 1

wrflist = [Dataset(name_str[i]) for i in range(len(name_str))]

print(wrflist)

#wrf_times = times.get_times(wrflist, timeidx=ALL_TIMES, method='cat')

wrf_times = extract_times(wrflist, timeidx=ALL_TIMES, method='cat', do_xtime=False)
print(pandas.to_datetime(wrf_times))

times = getvar(wrflist,"times",timeidx=ALL_TIMES,method="cat")
ntimes = np.size(times.values)
print(times.values)
print(ntimes)

T2 = getvar(wrflist,"T2",timeidx=ALL_TIMES,method="cat")
RAINNC = getvar(wrflist, "RAINNC",timeidx=ALL_TIMES,method="cat")
RAINC = getvar(wrflist, "RAINC",timeidx=ALL_TIMES,method="cat")
HFX = getvar(wrflist, "HFX",timeidx=ALL_TIMES,method="cat")
LH = getvar(wrflist, "LH",timeidx=ALL_TIMES,method="cat")

print(wrf_times)
print(T2)
print(RAINNC)
print(RAINC)
print(HFX)
print(LH)
print(times)

######## calculate total rain tendency #######
RAIN_tot = RAINNC + RAINC
print(RAIN_tot)

rain_tot_tend = RAIN_tot
rain_tot_tend.attrs["description"] = "(RAINNC+RAINC) tendency"
print(rain_tot_tend)
print(rain_tot_tend.shape)

#tend_int = 24
tend_int = 1
rain_tot_tend[tend_int:ntimes:tend_int,:,:] = RAIN_tot[tend_int:ntimes:tend_int,:,:]\
                                        - RAIN_tot[0:ntimes-tend_int+1:tend_int,:,:]
rain_tot_tend.attrs["units"] = "mm/hr"

print(rain_tot_tend)

#### calculate daily values from hourly values ####
T2_daily = T2.resample(Time='D').mean(dim='Time')
HFX_daily = HFX.resample(Time='D').mean(dim='Time')
LH_daily = LH.resample(Time='D').mean(dim='Time')
rain_tot_tend_daily = rain_tot_tend.resample(Time='D').mean(dim='Time')
rain_tot_tend_daily = rain_tot_tend_daily * 24.0 # from mm/hr to mm/day
rain_tot_tend_daily.attrs["units"] = "mm/day"

print(T2_daily)
print(HFX_daily)
print(LH_daily)
print(rain_tot_tend_daily)

### regridding to a common 1x1 grid ###
obs_dir = "/global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/CAUSES/obs/"
# http://www.earthsystemmodeling.org/esmf_releases/public/ESMF_8_0_0/esmpy_doc/html/examples.html
# Note that this ESMF python interface is less well documented comparing to NCL
# ESMF regridding https://www.ncl.ucar.edu/Applications/ESMF.shtml.
# Just use NCL for the first-stage preprocessing for now.










