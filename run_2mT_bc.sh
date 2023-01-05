start_year="${1}"
start_month="${2}"
end_year="${3}"
end_month="${4}"

#HydroGFD climatology and anomalies
nohup python ./scripts/2mT_hydrogfd_clim_anom.py cpct/tm_1980-2009_clim_0.5.nc cru/ts/cru_ts4.05.1979-2016.tmp.dat_anom_0.5.nc cpct/tm_2017-202211_anom_0.5.nc 1979 2022 ${end_month}

#Convert K to degC in era5 data
#cdo subc,273.15 2mT_${year}.nc 2mT_${year}_0.5C.nc

for ((year=${start_year}; year<=${end_year}; year++));
do
  echo $year
  for ((mth=${start_month}; mth<=12; mth++))
  do
    echo $mth
    #Select era5 data 
    mkdir tmp 
    cdo -s -selmon,$mth -selyear,$year ./era5/HH/2mT/2mT_${year}_0.5C.nc ./tmp/tmp_2mT_${year}_$(printf "%02d" $mth).nc
    #Calculate monthly from hourly data 
    cdo monmean ./tmp/tmp_2mT_${year}_$(printf "%02d" $mth).nc ./tmp/tmp_2mT_${year}_$(printf "%02d" $mth)_mon.nc
    #Select obs data 
    cdo -selmon,$mth -selyear,$year tabsmean_*.nc ./tmp/tmp_2mT.nc
    #Take diff of era vs obs
    cdo sub ./tmp/tmp_2mT.nc ./tmp/tmp_2mT_${year}_$(printf "%02d" $mth)_mon.nc ./tmp/tmp_tdiff.nc
    #Apply diff to all timesteps of era5 in each month 
    mkdir 2mT_bc 
    cdo add ./tmp/tmp_2mT_${year}_$(printf "%02d" $mth).nc ./tmp/tmp_tdiff.nc ./2mT_bc/2mT_${year}_$(printf "%02d" $mth)_bc_0.5.nc 
  done
#Merge bias corrected era5 files 
cdo mergetime ./2mT_bc/2mT_${year}_??_bc.nc ./2mT_bc/2mT_${year}_bc_0.5.nc
#Remove tmp files
rm -rf ./tmp
done

