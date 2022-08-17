================================
Berg 2021 bias correction method
================================

Datasets and sources: 
--------------------

Climatology:-

Precipitation - chpclim (chpclim.9090.monthly.nc; https://chc.ucsb.edu/data/chpclim)
Temperature - cpct (https://downloads.psl.noaa.gov/Datasets/cpc_global_temp/)
 - Variables Tmin and Tmax were averaged using CDO to obtain T 
Nwet - cru (https://catalogue.ceda.ac.uk/uuid/10d3e3640f004c578403419aac167d82)

Anomalies:- 

Precipitation - 
gpcch (1979-2016)
gpccm (2017-M-3)
gpccf (M-3-M0)
(https://opendata.dwd.de/climate_environment/GPCC/html/gpcc_firstguess_doi_download.html)
Temperature - 
cru (1979-2016)
cpct (2017-2022)

Method:
------
- Climatologies and anomalies were calculated using CDO and all datasets were interpolated onto 
0.5 x 0.5 global grid using the bilinear interpolation method of CDO 
- Load climatological data into Python 
- Create land-sea mask to only retain grid points with all data and months 
- Apply mask to all datasets to generate hfd-clim 

- Load anomaly data into Python 
- Add anomalies to hfd-clim to generate absolute reference data 
- Calculate the number of wet days for P 

- Load hourly era5 data (0.5 x 0.5 grid)
- Remove the weakest excessive wet days in era5 (P)
- Calculate the ratio (for P) or difference (for T) between
the monthly means of the reference and era5
- Apply ratio to all hourly time steps within the month 
- Calculate mean, minimum, maximum T from hourly time steps

Output:
------




 

