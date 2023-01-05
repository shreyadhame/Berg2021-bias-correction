=======================================
Berg et al. 2021 bias correction method
=======================================

Datasets and sources + data cleaning:
------------------------------------

Climatology:-

Precipitation - chpclim (chpclim.9090.monthly.nc; https://chc.ucsb.edu/data/chpclim)
  - Regrid to 0.5 x 0.5 grid
      cdo remapbil,./../grid_0.5,txt chpclim.9090.monthly.nc chpclim.9090.monthly_0.5.nc
Nwet - cru (https://catalogue.ceda.ac.uk/uuid/10d3e3640f004c578403419aac167d82)
  - Select years from 1980 to 2009 to calculate climatology
      cdo -monmean -selyear,1980/2009 cru/wet/cru_ts4.05.wet.dat.nc cru/wet/cru_ts4.05.1980-2009.wet.clim.nc
  - Regrid to 0.5 x 0.5 grid
      cdo remapbil,./../grid_0.5,txt cru/wet/cru_ts4.05.1980-2009.wet.clim.nc cru/wet/cru_ts4.05.1980-2009.wet.clim_0.5.nc
Temperature - cpct (https://downloads.psl.noaa.gov/Datasets/cpc_global_temp/)
  - Variables Tmin and Tmax were averaged using CDO to obtain T
      cdo ensmean tmin.nc tmax.nc t.nc
  - Select years from 1980 to 2009 to calculate climatology
      cdo -monmean -selyear,1980/2009 t.nc t_1980-2009_clim.nc
  - Regrid to 0.5 x 0.5 grid
      cdo remapbil,./../grid_0.5,txt t_1980-2009_clim.nc t_1980-2009_clim_0.5.nc

Anomalies:-

Precipitation -
gpcch (1979-2016)
gpccm (2017-M-3)
gpccf (M-3-M0)
(https://opendata.dwd.de/climate_environment/GPCC/html/gpcc_firstguess_doi_download.html)

Temperature -
cru (1979-2016)
cpct (2017-2022)

  - Calculate anomalies
      e.g. cdo -monmean -selyear,1980/2009
           cdo sub

ERA5:- download monthly and hourly data
Notes:  - To convert data from GRIB to netcdf
         e.g. cdo -f nc copy <input grib> <output netcdf>
        - If era5t data has 2 levels, use 'cdo -b F64 -mergetime -vertsum' to merge files

  - Separate data into yearly files
    cdo splityear era5/HH/tp/1979-2021.nc tp_
    cdo splityear era5/HH/2mT/1979-2021.nc 2mT_
  - Regrid to 0.5 x 0.5 grid
      cdo remapbil,./../grid_0.5,txt era5/HH/tp/1979.nc era5/HH/tp/tp_1979_0.5.nc
      cdo remapbil,./../grid_0.5,txt era5/HH/2mT/1979.nc era5/HH/2mT/2mT_1979_0.5.nc
  - Convert temperature from K to C
      cdo subc,273.15 era5/HH/2mT/2mT_1979_0.5.nc  era5/HH/2mT/2mT_1979_0.5C.nc

Method:
------
- All datasets were interpolated onto 0.5 x 0.5 global grid using the bilinear interpolation method of CDO
- ERA5 data is split into separate years

- For precipitation bias correction,
  nohup bash ./run_tp_bc.sh 1979 01 2022 04 &

- For temperature bias correction,
  nohup bash ./run_2mT_bc.sh 1979 01 2022 04 &


Output:
------
tabsmean_1979-202211.nc
pabsmean_1979-202211.nc
nwet_1979-202204.nc

Bias corrected yearly files in folder 2mT_bc and tp_bc
  e.g. /2mT_bc/2mT_bc_1979_0.5.nc

