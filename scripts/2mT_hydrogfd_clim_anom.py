#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__title__ = "Creates HydroGFD3 climatology and anomalies for temperature"
__reference__ = "Berg et al. 2021"
__author__ = "Shreya Dhame"
__version__ = "3.6.3"
__email__ = "shreyadhame@gmail.com"

#=================================================================
### Load modules
import argparse
import numpy as np
import numpy.ma as ma
import pandas as pd
import xarray as xr

#=================================================================
### Execute script
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_tclim') #cpct/tm_1980-2009_clim_0.5.nc
    parser.add_argument('file_cru_1979_2016') #cru/ts/cru_ts4.05.1979-2016.tmp.dat_anom_0.5.nc
    parser.add_argument('file_cpct_2017_M0') #cpct/tm_2017-202211_anom_0.5.nc

    parser.add_argument('start_year') #1979
    parser.add_argument('end_year') #2022
    parser.add_argument('end_month') #11

    args = parser.parse_args()

    file_tclim = str(args.file_tclim)
    file_cru = str(args.file_cru_1979_2016)
    file_cpct = str(args.file_cpct_2017_M0)

    start_year = int(args.start_year)
    end_year = int(args.end_year)
    end_month = int(args.end_month)

    ### Create HydroGFD climatology
    ##Load climatological data
    #Climatologies were calculated using CDO and interpolated on a 0.5x0.5 grid

    ##Temp
    tclim=xr.open_dataset(file_tclim).tmax #degC
    #latlon
    lat = tclim.lat
    lon=tclim.lon
    #Mask nan values
    tclim = ma.masked_invalid(tclim)

    #Create land-sea mask
    lsmask = np.empty(tclim.shape)
    for i in range(lsmask.shape[0]):
        for j in range(lsmask.shape[1]):
            for k in range(lsmask.shape[2]):
                if (type(tclim[i,j,k])==np.float32):
                    lsmask[i,j,k]=True
                else:
                    lsmask[i,j,k]=False

    #Mask zeros
    lsmask = ma.masked_where(lsmask==0.,lsmask)

    #Apply land-sea mask to climatologies
    tclim=ma.masked_invalid(tclim.data*lsmask)

    ### Anomaly method
    #Monthly anomalies of different datasets wrt their climatologies were calculated using CDO and interpolated on a 0.5x0.5 grid
    ##Load anomalies data
    #CRU (1979-2016)
    cru_anom = xr.open_dataset(file_cru, decode_coords=False).tmp
    #CPCT (2017-2022)
    cpct_anom = xr.open_dataset(file_cpct, decode_coords=False).tmax

    #Combine anomalies from all datasets
    tanom = xr.concat((cru_anom,cpct_anom),dim='time',join='override')

    #Add anomalies to HydroGFD climatology
    if end_month==12:
        tclimt = np.tile(tclim,(tanom.shape[0]//12,1,1))
    elif end_month<12:
        tclimt = np.concatenate((np.tile(tclim,(tanom.shape[0]//12,1,1)),tclim[:end_month]))
    tabsmean = tclimt + tanom

    #Convert to xarray
    tabsmean_xr = xr.DataArray(tabsmean, dims=tanom.dims, attrs=tanom.attrs)
    
    #Create time array
    dt = pd.date_range(str(start_year)+'-01-01', freq = '1M', periods=12*(end_year-start_year) + (end_month))
    tabsmean_xr = tabsmean_xr.assign_coords(time=dt, lon=lon, lat=lat)
    tabsmean_xr = tabsmean_xr.rename("tmp")

    #Export absolute precipitation as netcdf
    tabsmean_xr.to_netcdf('tabsmean_'+str(start_year)+'-'+str(end_year)+str(end_month).zfill(2)+'.nc')

    # #Load era5 monthly data
    # te5_mm = xr.open_dataset('/work/mh0033/m300952/UW/era5/MM/2mT/era5_2mT_MM_197901-202205_0.5.nc').t2m - 273.15
    # time = te5_mm.time
    # # te5_mm = te5_mm.sel(time=slice('1979','2021'))
    # #Apply mask
    # lsmask_r = np.tile(lsmask,(te5_mm.shape[0]//12, 1,1))
    # lsmask_r = np.concatenate((lsmask_r,lsmask_r[:5]))
    # #Mask zeros
    # lsmask_r = ma.masked_where(lsmask_r==0.,lsmask_r)
    # te5_mm_ma = te5_mm*lsmask_r
    # 
    # #Take difference
    # tdiff = te5_mm_ma[:-1] - tabsmean
    # 
    # #Export as netcdf
    # tdiff.to_netcdf('/work/mh0033/m300952/UW/tdiff_1979-202204.nc')

