import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse

import warnings
warnings.filterwarnings("ignore")

g2pg=1.e6*1.e-15

def get_vegcts(histf):
    elmfl=Dataset(histf,"r")

    area=elmfl.variables["area"][:]
    landfr=elmfl.variables["landfrac"][:]
    vegc_ste=elmfl.variables["TOTLITC_1m"][:]
    garea=landfr*area
    nts=vegc_ste.shape[0]
    vegcts=np.zeros(nts)
    for j in range(nts):
        vegcste=np.squeeze(vegc_ste[j,:,:]*garea)
        vegcts[j]=np.nansum(vegcste)*g2pg
    elmfl.close()
    return vegcts

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
    vegcts=get_vegcts(histf)
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    for year in range(year1,year2+1):
        syear='%04d'%year
        newf=histf.replace(xyear,syear)
        if first:
            vegcts=get_vegcts(newf)
            first=False
        else:
            ts=get_vegcts(newf)
            vegcts=np.concatenate((vegcts,ts))

print (vegcts)


csv_file=args.csv_file[0]

if csv_file:
    np.savetxt(csv_file, vegcts, delimiter=",")
