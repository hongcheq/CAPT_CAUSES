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

dir_string = "/global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/LGdm.STD2011/"
wrflist = [Dataset(dir_string+"wrfout_d01_2011-06-22_01:00:00"),
           Dataset(dir_string+"wrfout_d01_2011-06-22_02:00:00"),
           Dataset(dir_string+"wrfout_d01_2011-06-22_03:00:00")]

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
rain_tot_tend.attrs["units"] = "mm/day"

print(rain_tot_tend)

#### calculate daily values from hourly values ####

















