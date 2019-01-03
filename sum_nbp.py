import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse

import warnings
warnings.filterwarnings("ignore")

def get_nbpts(histf):
    elmfl=Dataset(histf,"r")

    area=elmfl.variables["area"][:]
    landfr=elmfl.variables["landfrac"][:]
    nbp_flx=elmfl.variables["NBP"][:]
    garea=landfr*area
    nts=nbp_flx.shape[0]
    nbpts=np.zeros(nts)
    for j in range(nts):
        nbpflx=np.squeeze(nbp_flx[j,:,:]*garea)
        nbpts[j]=np.nansum(nbpflx)*g2pg
    elmfl.close()
    return nbpts

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--h0file', dest="h0file", metavar='h0file', type=str, nargs=1, default=[""],
  help='the original app to be cloned')


parser.add_argument('--model_year', dest="model_year", metavar='beg_year end_year', type=int, nargs=2, default=[],
  help='the start and end of model year')



args = parser.parse_args()

histf=args.h0file[0]
model_year=args.model_year

if not model_year:
    year1=0
    year2=-1
else:
    year1=model_year[0]
    year2=model_year[1]

g2pg=1.e6*365.0*86400.0*1.e-15


if year1 > year2:
    nbpts=get_nbpts(histf)
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    for year in range(year1,year2+1):
        syear='%04d'%year
        newf=histf.replace(xyear,syear)
        if first:
            nbpts=get_nbpts(histf)
            first=False
        else:
            ts=get_nbpts(histf)
            nbpts=np.concatenate(nbpts,ts)

print nbpts
