#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__title__ = "Remove excess precipitation days in ERA5"
__reference__ = "Berg et al. 2021"
__author__ = "Shreya Dhame"
__version__ = "3.6.3"
__email__ = "shreyadhame@gmail.com"

#=================================================================
### Load modules
import argparse 
import numpy as np
import numpy.ma as ma
import xarray as xr 

#=================================================================
### Execute script

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_tp') #
    parser.add_argument('file_nwet') #

    args = parser.parse_args()

    file_tp = str(args.file_tp)
    file_nwet = str(args.file_nwet)

    #Load precipation file
    pe5_d = xr.open_dataset(file_tp).tp #mm/day


    #Load nwet file
    nwet = xr.open_dataset(file_nwet).nwet

    pe5_c = pe5_d.copy()
    for i in range(nwet.shape[-2]):
        for j in range(nwet.shape[-1]):
            if ma.masked_invalid(nwet).mask.squeeze()[i,j] == True:
                pe5_c[:,i,j] = np.nan
            elif ma.masked_invalid(nwet).mask.squeeze()[i,j] == False:
                #Number of wet days
                n = int(nwet[:,i,j])
                #Number of dry days 
                nd = len(pe5_c[:,i,j]) - n
                #Replace minimum rain days with 0.
                pe5 = pe5_d[:,i,j].copy()
                isort = np.argsort(pe5).values
                pe5[isort[:nd]] = 0.
                #Apply values to original array
                pe5_c[:,i,j] = pe5    

    #Export as netcdf
    pe5_c.to_netcdf(str(file_tp)+'_c.nc')
