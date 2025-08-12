import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse
import re
import warnings
warnings.filterwarnings("ignore")

def get_hrts(histf):
    elmfl=Dataset(histf,"r")

    area=elmfl.variables["area"][:]
    landfr=elmfl.variables["landfrac"][:]
    hr_flx=elmfl.variables["HR"][:]
    garea=landfr*area
    nts=hr_flx.shape[0]
    hrts=np.zeros(nts)
    for j in range(nts):
        hrflx=np.squeeze(hr_flx[j,:,:]*garea)
        hrts[j]=np.nansum(hrflx)
    elmfl.close()
    return hrts

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

g2pg=1.e6*86400.0*1.e-15

year_mon_match = re.search(r'\.h0\.(\d{4})-(\d{2})\.nc$', histf)
daz=[31.,28.,31.,30.,31.,30.,31.,31.,30.,31.,30.,31]

if year1 > year2:
    hrts=get_hrts(histf)
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    if year_mon_match:
        xmon=histf[(k+9):(k+11)]
        for year in range(year1,year2+1):
            syear='%04d'%year
            newf=histf.replace(xyear,syear)
            firstm=True
            for m in range(0,12):
                smon='%02d'%(m+1)
                newf1=newf.replace(xmon,smon)
                g2pg1=g2pg*daz[m]
                if firstm:
                    hrtsm=get_hrts(newf1)*g2pg1
                    firstm=False
                else:
                    ts=get_hrts(newf1)*g2pg1
                    hrtsm=np.concatenate((hrtsm,ts))
            if first:
                hrts=np.array([np.sum(hrtsm)])
                first=False
            else:
                ts=np.array([np.sum(hrtsm)])
                hrts=np.concatenate((hrts,ts))
    else:  
        g2pg=g2pg*365.0
        for year in range(year1,year2+1):
            syear='%04d'%year
            newf=histf.replace(xyear,syear)
            if first:
                hrts=get_hrts(newf)*g2pg
                first=False
            else:
                ts=get_hrts(newf)*g2pg
                hrts=np.concatenate((hrts,ts))

print (hrts)


csv_file=args.csv_file[0]

if csv_file:
    np.savetxt(csv_file, hrts, delimiter=",")
