'''
Function: preprocessing using python scripts
Date: 20200318
'''
from __future__ import print_function

from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES

dir_string = "/global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/LGdm.STD2011/"
wrflist = [Dataset(dir_string+"wrfout_d01_2011-06-22_01:00:00"),
           Dataset(dir_string+"wrfout_d01_2011-06-22_02:00:00"),
           Dataset(dir_string+"wrfout_d01_2011-06-22_03:00:00")]

T2 = getvar(wrflist,"T2",timeidx=ALL_TIMES,method="cat")
# RAINNC = getvar(ncfile, "RAINNC")
# RAINC = getvar(ncfile, "RAINC")
# HFX = getvar(ncfile, "HFX")
# LH = getvar(ncfile, "LH")

print(T2)
# print(RAINNC)
# print(RAINC)
# print(HFX)
# print(LH)

