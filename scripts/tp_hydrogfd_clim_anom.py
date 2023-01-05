#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__title__ = "Creates HydroGFD3 climatology and anomalies for precipitation"
__reference__ = "Berg et al. 2021"
__author__ = "Shreya Dhame"
__version__ = "3.6.3"
__email__ = "shreyadhame@gmail.com"

#=================================================================
### Load modules
import os 
import sys 
import argparse
import numpy as np
import numpy.ma as ma
import pandas as pd
import xarray as xr

#=================================================================
### Execute script

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_pclim') #chpclim/chpclim.9090.monthly_0.5.nc
    parser.add_argument('file_nwetclim') #cru/wet/cru_ts4.05.1980-2009.wet.clim_0.5.nc
    parser.add_argument('file_gpcch_clim') #gpcch/full_data_monthly_v2022_1980-2009_clim_0.5.nc
    parser.add_argument('file_gpcch_1979_2016') #gpcch/full_data_monthly_v2022_1979-2016_0.5.nc
    parser.add_argument('file_gpccm_2017_M_3') #gpccm/monitoring_v2022_10_2017-202208_0.5.nc
    parser.add_argument('file_gpccf_M_3_M0') #gpccf/first_guess_monthly_202209-202211_0.5.nc

    parser.add_argument('start_year') #1979
    parser.add_argument('end_year') #2022
    parser.add_argument('end_month') #11

    args = parser.parse_args()

    file_pclim = str(args.file_pclim)
    file_nwetclim = str(args.file_nwetclim)
    file_gpcchc = str(args.file_gpcch_clim)
    file_gpcch = str(args.file_gpcch_1979_2016)
    file_gpccm = str(args.file_gpccm_2017_M_3)
    file_gpccf = str(args.file_gpccf_M_3_M0)

    start_year = int(args.start_year)
    end_year = int(args.end_year)
    end_month = int(args.end_month)

    #HYDROGFD3 CLIMATOLOGY
    #Load climatological data
    #Climatologies were calculated using CDO and interpolated on a 0.5x0.5 grid
    ##Precip
    pclim=xr.open_dataset(file_pclim).precip #mm/month
    #latlon
    lat = pclim.lat
    lon=pclim.lon
    pclim = ma.masked_invalid(pclim)
    ##Nwet 
    nwetclim = xr.open_dataset(file_nwetclim).wet
    nwetclim = [x.astype('timedelta64[D]') / np.timedelta64(1, 'D') for x in nwetclim] 
    nwetclim = ma.masked_invalid(nwetclim) #days

    #Create land-sea mask
    lsmask = np.empty(pclim.shape)
    for i in range(lsmask.shape[0]):
        for j in range(lsmask.shape[1]):
            for k in range(lsmask.shape[2]):
                if (type(pclim[i,j,k])==np.float32) and (type(nwetclim[i,j,k])==np.float64):
                    lsmask[i,j,k]=True
                else:
                    lsmask[i,j,k]=False

    #Mask zeros
    lsmask = ma.masked_where(lsmask==0.,lsmask)

    #Apply land-sea mask to climatologies
    pclim=ma.masked_invalid(pclim.data*lsmask)
    nwetclim=ma.masked_invalid(nwetclim.data*lsmask)

    ### Anomaly method
    #Monthly anomalies of different datasets wrt their climatologies were calculated using CDO and interpolated on a 0.5x0.5 grid
    ##Load anomalies data
    #gpcch mm/month
    preciph = xr.open_dataset(file_gpcch, decode_coords=False).precip
    preciph_clim = xr.open_dataset(file_gpcchc, decode_coords=False).precip
    preciph_climh = np.tile(preciph_clim,(preciph.shape[0]//12,1,1))
    preciph_anom = preciph/preciph_climh

    #gpccm mm/month
    precipm = xr.open_dataset(file_gpccm, decode_coords=False).p
    mend_month = end_month - 3
    if mend_month==12:
        preciph_climm = np.tile(preciph_clim,(precipm.shape[0]//12,1,1))
    elif mend_month<12:
        preciph_climm = np.concatenate((np.tile(preciph_clim,(precipm.shape[0]//12,1,1)),preciph_clim[:mend_month]))
    precipm_anom = precipm.values/preciph_climm

    #gpccf mm/month
    precipf = xr.open_dataset(file_gpccf,decode_times=False,decode_coords=False).p
    fstart_month = end_month - 3
    preciph_climf = preciph_clim[fstart_month:fstart_month+3]
    precipf_anom = precipf.values/preciph_climf

    #Combine anomalies from all datasets
    panom = np.concatenate((preciph_anom,precipm_anom,precipf_anom))

    #Add anomalies to HydroGFD climatology
    if end_month==12:
        pclimt = np.tile(pclim,(panom.shape[0]//12,1,1))
    elif end_month<12:
        pclimt = np.concatenate((np.tile(pclim,(panom.shape[0]//12,1,1)),pclim[:end_month]))
    pabsmean = pclimt*panom

    #Convert to xarray
    pabsmean_xr = xr.DataArray(pabsmean, dims=preciph.dims, attrs=preciph.attrs)
    #Create time array
    dt = pd.date_range(str(start_year)+'-01-01', freq = '1M', periods=12*(end_year-start_year) + (end_month))
    pabsmean_xr = pabsmean_xr.assign_coords(time=dt, lon=lon, lat=lat)
    pabsmean_xr = pabsmean_xr.rename("p")
    #Export absolute precipitation as netcdf
    pabsmean_xr.to_netcdf('pabsmean_'+str(start_year)+'-'+str(end_year)+str(end_month).zfill(2)+'.nc')

    #Calculate wet-day frequency
    if end_month==12:
        nwetclim = np.tile(nwetclim,(panom.shape[0]//12,1,1))
    elif end_month<12:
        nwetclim = np.ma.concatenate((np.tile(nwetclim,(panom.shape[0]//12,1,1)),nwetclim[:end_month]))
    k = 0.28
    nwet = (panom**k)*nwetclim #target number of wet days

    #Export wet-day frequency as netcdf
    nwet_xr =  xr.DataArray(nwet, dims=pabsmean_xr.dims, attrs=pabsmean_xr.attrs, coords = pabsmean_xr.coords)
    nwet_xr = nwet_xr.rename("nwet")
    nwet_xr.to_netcdf('nwet_'+str(start_year)+'-'+str(end_year)+str(end_month).zfill(2)+'.nc')
