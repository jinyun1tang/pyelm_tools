import netCDF4
import numpy as np
import os,time,sys,argparse


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ncfile', dest="ncfilein", metavar='ncfilein', type=str, nargs=1, default=[""],
  help='the restart file to be corrected')


args = parser.parse_args()

nc_file=args.ncfilein[0]


data_file = netCDF4.Dataset(nc_file, 'r')
pfts1d_itypveg=data_file['pfts1d_itypveg'][:]
pfts1d_wtcol=data_file['pfts1d_wtcol'][:]
pfts1d_active=data_file['pfts1d_active'][:]

pft_flag=np.zeros((len(pfts1d_wtcol)))

for j in range(len(pft_flag)):
    if pfts1d_itypveg[j]>0 and pfts1d_wtcol[j]>0 and pfts1d_active[j]==1:
        pft_flag[j]=1
        
data_file.close()

flag_strings=['pfts1d_itypveg','pfts1d_wtcol','pfts1d_active']

data_file = netCDF4.Dataset(nc_file, 'a')
variable_names = list(data_file.variables.keys())

for var in variable_names:
    variable=data_file[var]  
    dimension_names = variable.dimensions
    matches = [string for string in flag_strings if string == var]
    if not matches:
        dataval=data_file[var][:]        
        ndim=len(dataval.shape)
        if ndim==1 and dimension_names[0]=='pft':
            for j in range(len(pft_flag)):
                if dataval[j]!=dataval[j] and pft_flag[j]==1:
                    dataval[j]=0.
            data_file[var][:]=dataval
data_file.close()

print("NaN removed from file %s"%nc_file)