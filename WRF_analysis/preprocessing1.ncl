;Function: extract T2, RAINNC, RAINC, HFX, LH from /global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/LGdm.STD2011/ hourly WRF output files;
;Date: 20200310


load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRF_contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/esmf/ESMF_regridding.ncl"

begin

dir = "/global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/LGdm.STD2011/"
;files = systemfunc("ls " + dir + "wrfout_d01_2011-05-0*")
files = systemfunc("ls " + dir + "wrfout_d01_2011*")

a     = addfiles(files,"r")
printVarSummary(a)

times = wrf_user_getvar(a,"times",-1)  ; get all times in the file
  ntimes = dimsizes(times)         ; number of times in the file

T2   = wrf_user_getvar(a,"T2",-1)
RAINNC = wrf_user_getvar(a,"RAINNC",-1)
RAINC = wrf_user_getvar(a,"RAINC",-1)
HFX = wrf_user_getvar(a,"HFX",-1)
LH = wrf_user_getvar(a,"LH",-1)

printVarSummary(T2)
printVarSummary(RAINNC)
printVarSummary(RAINC)
printVarSummary(HFX)
printVarSummary(LH)

T2&Time =  wrf_times_c(a[:]->Times, 0)  ; convert to "hours since"
RAINNC&Time =  wrf_times_c(a[:]->Times, 0)  ; convert to "hours since"
RAINC&Time =  wrf_times_c(a[:]->Times, 0)  ; convert to "hours since"
HFX&Time =  wrf_times_c(a[:]->Times, 0)  ; convert to "hours since"
LH&Time =  wrf_times_c(a[:]->Times, 0)  ; convert to "hours since"

RAIN_tot = RAINNC ; metadata
RAIN_tot =  RAINNC + RAINC
RAIN_tot = RAIN_tot ; 
RAIN_tot@description = "(RAINNC+RAINC)"

rain_tot_tend = RAIN_tot
rain_tot_tend = 0.0
rain_tot_tend@description = "Total Precipitation Tendency"

; Calculate tendency values 
  ; We know our data is available every 1 hours, so setting tend_int to 1 gives 
  ; tendencies for 1 hours, setting it to 24, gives 24-hour or 1-day tendencies                               
  tend_int = 24
  rain_tot_tend(tend_int:ntimes-1:tend_int,:,:) = RAIN_tot(tend_int:ntimes-1:tend_int,:,:) - RAIN_tot(0:ntimes-tend_int:tend_int,:,:)

  rain_tot_tend@units = "mm/day"

printVarSummary(T2)
printVarSummary(RAINNC)
printVarSummary(RAINC)
printVarSummary(HFX)
printVarSummary(LH)

printVarSummary(RAIN_tot)
printVarSummary(rain_tot_tend)

;------------ calculate daily values from hourly values ---
nDim = 0
T2_daily = calculate_daily_values(T2, "avg", nDim, False)
HFX_daily = calculate_daily_values(HFX, "avg", nDim, False)
LH_daily = calculate_daily_values(LH, "avg", nDim, False)

;Note rain_tot_tend has the same time dimension as hourly data, but only every 24-hour interval, there's a value other than zero. Therefore:
rain_tot_tend_daily = calculate_daily_values(rain_tot_tend, "sum", nDim, False)

printVarSummary(T2_daily)
printVarSummary(HFX_daily)
printVarSummary(LH_daily)
printVarSummary(rain_tot_tend_daily)

;------------ regrid T2 to 1x1 common grid -------
obs_dir = "/global/cscratch1/sd/hongcheq/LLNL/WRF_simulations_Feng_Zhe/CAUSES/obs/"
f_obs = addfile(obs_dir+"LE_H_FLUXNET_2011_conus_1dgrid.nc","r")

;---------------
    Opt                = True
    Opt@SrcTitle       = "WRF grid"   ; optional
    Opt@WgtFileName    = "WRF_to_Rect.nc"   
; Note: Error message: "(0)	ESMF_regrid_gen_weights: could not find ESMF_RegridWeightGen executable."
; This WRF_to_Rect.nc was uploaded from local laptop to NERSC as a workaround

    Opt@ForceOverwrite = True
    ;;Opt@PrintTimings = True

;---Get the source lat/lon grid
    lat2d = a[0]->XLAT(0,:,:)
    lon2d = a[0]->XLONG(0,:,:)
    
    ;lon2d = where(lon2d.lt.0,360+lon2d,lon2d)

    rain_tot_tend_daily@lat2d = lat2d              ; This information will be used by
    rain_tot_tend_daily@lon2d = lon2d              ; ESMF_regrid for the source grid
    T2_daily@lat2d   = lat2d
    T2_daily@lon2d   = lon2d
    HFX_daily@lat2d   = lat2d
    HFX_daily@lon2d   = lon2d
    LH_daily@lat2d   = lat2d
    LH_daily@lon2d   = lon2d

    Opt@SrcFileName     = "WRF_SCRIP.nc"      ; Name of source and
    Opt@DstFileName     = "Rectilinear.nc"    ; destination files

;---Create the destination lat/lon grid
    lat = f_obs->latitude
    lon = f_obs->longitude

    Opt@DstGridType          = "rectilinear"
    Opt@DstGridLat           = lat
    Opt@DstGridLon           = lon

    Opt@InterpMethod         = "bilinear"   
; Or use conserve for high-frequency rainfall? see https://climatedataguide.ucar.edu/climate-data-tools-and-analysis/regridding-overview
    Opt@SrcRegional          = True
    Opt@DstRegional          = True

;Note the WRF_to_Rect.nc weight file was uploaded as a workaround. Therefore adding the following three lines of code.
    Opt@SkipSrcGrid   = True
    Opt@SkipDstGrid   = True
    Opt@SkipWgtGen    = True
    
    RAIN_tot_regrid = ESMF_regrid(rain_tot_tend_daily,Opt)     ; Do the regridding for rain_tot_tend_daily
;
; The source and destination grid description files and
; weight file will be the same for the next call to
; ESMF_grid, so no need to regenerate them.
;
;------------------------------;
    Opt@SkipSrcGrid   = True
    Opt@SkipDstGrid   = True
    Opt@SkipWgtGen    = True

    T2_regrid          = ESMF_regrid(T2_daily,Opt)   ; Do the regridding for U
;--------------------------------
    Opt@SkipSrcGrid   = True
    Opt@SkipDstGrid   = True
    Opt@SkipWgtGen    = True

    HFX_regrid          = ESMF_regrid(HFX_daily,Opt)   ; Do the regridding for U
;--------------------------------
    Opt@SkipSrcGrid   = True
    Opt@SkipDstGrid   = True
    Opt@SkipWgtGen    = True

    LH_regrid          = ESMF_regrid(LH_daily,Opt)   ; Do the regridding for U

;-------------------------------

printVarSummary(RAIN_tot_regrid)
printVarSummary(T2_regrid)
printVarSummary(HFX_regrid)
printVarSummary(LH_regrid)

;;------------------------
;------------- output nc files test

system("rm WRF.postprocessing.extract.nc")
ncdf = addfile("WRF.postprocessing.extract.nc","c")

fAtt               = True
fAtt@title         = "Feng2018 WRF simulation"

filedimdef(ncdf,"time",-1,True)

ncdf->RAIN_tot_regrid = RAIN_tot_regrid
ncdf->T2_regrid = T2_regrid
ncdf->HFX_regrid = HFX_regrid
ncdf->LH_regrid = LH_regrid



end
