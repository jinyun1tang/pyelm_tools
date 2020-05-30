import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse

import warnings
warnings.filterwarnings("ignore")

g2pg=1.e6*1.e-15

def get_cts(histf):
    elmfl=Dataset(histf,"r")

    area=elmfl.variables["area"][:]
    landfr=elmfl.variables["landfrac"][:]
    vegc_ste=elmfl.variables["TOTVEGC"][:]
    somc_ste=elmfl.variables["TOTSOMC"][:]
    litc_ste=elmfl.variables["TOTLITC"][:]
    cwdc_ste=elmfl.variables["CWDC"][:]
    ecosc_ste=elmfl.variables["TOTECOSYSC"][:]

    garea=landfr*area
    nts=ecosc_ste.shape[0]
    vegcts=np.zeros(nts)
    somcts=np.zeros(nts)
    litcts=np.zeros(nts)
    cwdcts=np.zeros(nts)
    ecoscts=np.zeros(nts)
    for j in range(nts):
        datac=np.squeeze(vegc_ste[j,:,:]*garea)
        vegcts[j]=np.nansum(datac)*g2pg
        datac=np.squeeze(somc_ste[j,:,:]*garea)
        somcts[j]=np.nansum(datac)*g2pg
        datac=np.squeeze(litc_ste[j,:,:]*garea)
        litcts[j]=np.nansum(datac)*g2pg
        datac=np.squeeze(cwdc_ste[j,:,:]*garea)
        cwdcts[j]=np.nansum(datac)*g2pg
        datac=np.squeeze(ecosc_ste[j,:,:]*garea)
        ecoscts[j]=np.nansum(datac)*g2pg

    elmfl.close()
    return vegcts,somcts,litcts,cwdcts,ecoscts

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--h0file', dest="h0file", metavar='h0file', type=str, nargs=1, default=[""],
  help='the original app to be cloned')


parser.add_argument('--model_year', dest="model_year", metavar='beg_year end_year', type=int, nargs=2, default=[],
  help='the start and end of model year')

parser.add_argument('--csv_file', dest="csv_file", metavar='csv_file', type=str, nargs=1, default=[""],
  help='csv file to output results')


args = parser.parse_args()

histf=args.h0file[0]
model_year=args.model_year

if not model_year:
    year1=0
    year2=-1
else:
    year1=model_year[0]
    year2=model_year[1]



if year1 > year2:
    vegcts,somcts,litcts,cwdcts,ecoscts=get_cts(histf)
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    for year in range(year1,year2+1):
        syear='%04d'%year
        newf=histf.replace(xyear,syear)
        if first:
            vegcts,somcts,litcts,cwdcts,ecoscts=get_cts(newf)
            first=False
        else:
            vegcts1,somcts1,litcts1,cwdcts1,ecoscts1=get_cts(newf)
            vegcts=np.concatenate((vegcts,vegcts1))
            somcts=np.concatenate((somcts,somcts1))
            litcts=np.concatenate((litcts,litcts1))
            cwdcts=np.concatenate((cwdcts,cwdcts1))
            ecoscts=np.concatenate((ecoscts,ecoscts1))


print ('vegc   ,somc   ,litc   ,cwdc   ,ecosc  ,res')
for j in range(len(vegcts)):
    res=vegcts[j]+somcts[j]+litcts[j]+cwdcts[j]-ecoscts[j]
    print ('%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f'%(vegcts[j],somcts[j],litcts[j],cwdcts[j],ecoscts[j],res))


csv_file=args.csv_file[0]

if csv_file:
    np.savetxt(csv_file, vegcts, delimiter=",")
