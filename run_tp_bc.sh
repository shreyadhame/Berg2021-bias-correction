start_year="${1}"
start_month="${2}"
end_year="${3}"
end_month="${4}"

#HydroGFD climatology and anomalies
python ./scripts/tp_hydrogfd_clim_anom.py chpclim/chpclim.9090.monthly_0.5.nc cru/wet/cru_ts4.05.1980-2009.wet.clim_0.5.nc gpcch/full_data_monthly_v2022_1980-2009_clim_0.5.nc gpcch/full_data_monthly_v2022_1979-2016_0.5.nc gpccm/monitoring_v2022_10_2017-202208_0.5.nc gpccf/first_guess_monthly_202209-202211_0.5.nc 1979 2022 ${end_month}

#Remove weakest precipitation days in era5
for ((year=${start_year}; year<=${end_year}; year++))
do
        echo $year
        for ((mth=${start_month}; mth<=12; mth++))
        do
                echo $mth
                #Select era5 data
                mkdir -p tmp
                cdo -s -selmon,$mth -selyear,$year ./era5/HH/tp/tp_${year}_0.5.nc ./tmp/tmp_tp_${year}_$(printf "%02d" $mth).nc

                #Convert m/hour to mm/hour
                cdo -mulc,1000 ./tmp/tmp_tp_${year}_$(printf "%02d" $mth).nc ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_mmhr.nc

                #Select target nwet days
                cdo -s selmon,$mth -selyear,$year nwet_*.nc ./tmp/tmp_nwet.nc

                #Calculate daily from hourly data mm/day 
                cdo daysum ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_mmhr.nc ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_d.nc
                
                #Remove excess precipitation days
                python ./scripts/excess_wet.py ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_d.nc ./tmp/tmp_nwet.nc

                #convert daily to monthly data mm/month
                cdo monsum ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_d.nc_c.nc ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_mc.nc

                #Select obs data mm/month
                cdo -selmon,$mth -selyear,$year pabsmean_*.nc ./tmp/tmp_tp.nc

                #Take ratio of era vs obs
                cdo div ./tmp/tmp_tp.nc ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_mc.nc ./tmp/tmp_pratio.nc

                #Convert ratio from mm/month to mm/hour 
                if [ $mth -eq 1 ] || [ $mth -eq 3 ] || [ $mth -eq 5 ] || [ $mth -eq 7 ] || [ $mth -eq 8 ] || [ $mth -eq 10 ] || [ $mth -eq 12 ];
                then
                  cdo -divc,744 ./tmp/tmp_pratio.nc ./tmp/tmp_pratio_mmhr.nc
                elif [ $mth -eq 4 ] || [ $mth -eq 6 ] || [ $mth -eq 9 ] || [ $mth -eq 11 ];
                then
                  cdo -divc,720 ./tmp/tmp_pratio.nc ./tmp/tmp_pratio_mmhr.nc
                elif [ $mth -eq 2 ];
                then
                  if [ $[$year % 4] -eq 0 ];
                  then
                    cdo -divc,696 ./tmp/tmp_pratio.nc ./tmp/tmp_pratio_mmhr.nc
                  else
                    cdo -divc,672 ./tmp/tmp_pratio.nc ./tmp/tmp_pratio_mmhr.nc
                  fi
                fi            
                
                #Apply ratio to all hourly timesteps of era5 in each month
                cdo mul ./tmp/tmp_tp_${year}_$(printf "%02d" $mth).nc ./tmp/tmp_pratio_mmhr.nc ./tmp/tmp_tp_${year}_$(printf "%02d" $mth)_c.nc
        done
        #Merge corrected era5 files
        mkdir -p tp_bc
        cdo mergetime ./tmp/tmp_tp_${year}_??_c.nc ./tp_bc/tp_bc_${year}_0.5.nc
        #Remove tmp files
        #rm -rf ./tmp
done

